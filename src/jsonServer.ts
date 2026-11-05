import { Hono, type Context } from "hono";
import { db, findById, sameId, type Row } from "./store";
import type { Env } from "./env";

/**
 * Réimplémentation des routes de json-server (https://github.com/typicode/json-server)
 * compatible Workers (pas d'accès au système de fichiers).
 *
 *   GET    /db
 *   GET    /:resource          filtres, q, _sort, _order, _page, _per_page, _limit, _start, _end, _embed, _expand
 *   GET    /:resource/:id      _embed, _expand
 *   POST   /:resource
 *   PUT    /:resource/:id
 *   PATCH  /:resource/:id
 *   DELETE /:resource/:id
 */
export const jsonServer = new Hono<{ Bindings: Env }>();

const OPERATORS = ["ne", "lt", "lte", "gt", "gte", "like"] as const;
type Operator = (typeof OPERATORS)[number];
const OPERATOR_KEY = new RegExp(`^(.+?)[_:](${OPERATORS.join("|")})$`);
const RESERVED = new Set(["q", "_sort", "_order", "_page", "_per_page", "_limit", "_start", "_end", "_embed", "_expand"]);

export function singular(resource: string): string {
  if (resource.endsWith("ies")) return `${resource.slice(0, -3)}y`;
  if (resource.endsWith("sses")) return resource.slice(0, -2);
  if (resource.endsWith("s")) return resource.slice(0, -1);
  return resource;
}

const getPath = (row: Row, path: string): unknown =>
  path.split(".").reduce<unknown>((v, k) => (v == null ? undefined : (v as Record<string, unknown>)[k]), row);

function compare(a: unknown, b: unknown): number {
  const na = Number(a);
  const nb = Number(b);
  if (a !== "" && b !== "" && a != null && b != null && !Number.isNaN(na) && !Number.isNaN(nb)) return na - nb;
  return String(a ?? "").localeCompare(String(b ?? ""));
}

function matches(value: unknown, op: Operator | "eq", expected: string): boolean {
  switch (op) {
    case "eq":
      return Array.isArray(value) ? value.some((v) => sameId(v, expected)) : sameId(value, expected);
    case "ne":
      return !sameId(value, expected);
    case "lt":
      return compare(value, expected) < 0;
    case "lte":
      return compare(value, expected) <= 0;
    case "gt":
      return compare(value, expected) > 0;
    case "gte":
      return compare(value, expected) >= 0;
    case "like":
      try {
        return new RegExp(expected, "i").test(String(value ?? ""));
      } catch {
        return false;
      }
  }
}

function fullText(row: Row, q: string): boolean {
  const needle = q.toLowerCase();
  return Object.values(row).some((v) => typeof v !== "object" && String(v).toLowerCase().includes(needle));
}

function embed(resource: string, row: Row, names: string[]): Row {
  const out: Row = { ...row };
  for (const name of names) {
    if (!db[name]) continue;
    const ids = row[`${singular(name)}Ids`];
    out[name] = Array.isArray(ids)
      ? // relation N-N : restaurants.categoryIds -> categories
        ids.map((id) => findById(name, id)).filter(Boolean)
      : // relation 1-N : tags.restaurantId -> restaurant
        db[name].filter((child) => sameId(child[`${singular(resource)}Id`], row.id));
  }
  return out;
}

function expand(row: Row, names: string[]): Row {
  const out: Row = { ...row };
  for (const name of names) {
    const collection = Object.keys(db).find((k) => singular(k) === name);
    if (collection) out[name] = findById(collection, row[`${name}Id`]) ?? null;
  }
  return out;
}

function decorate(c: Context, resource: string, row: Row): Row {
  const embeds = c.req.queries("_embed") ?? [];
  const expands = c.req.queries("_expand") ?? [];
  return expand(embed(resource, row, embeds), expands);
}

function readOnlyGuard(c: Context<{ Bindings: Env }>) {
  if (c.env?.READ_ONLY === "true") return c.json({ error: "API en lecture seule" }, 403);
  return null;
}

async function readBody(c: Context): Promise<Record<string, unknown> | null> {
  try {
    const body = await c.req.json();
    return body && typeof body === "object" && !Array.isArray(body) ? body : null;
  } catch {
    return null;
  }
}

function nextId(rows: Row[]): string | number {
  if (rows.length > 0 && rows.every((r) => typeof r.id === "number")) {
    return Math.max(...rows.map((r) => r.id as number)) + 1;
  }
  return crypto.randomUUID();
}

jsonServer.get("/db", (c) => c.json(db));

jsonServer.get("/:resource", (c) => {
  const resource = c.req.param("resource");
  const rows = db[resource];
  if (!rows) return c.json({}, 404);

  const query = c.req.queries();
  let items = rows.filter((row) =>
    Object.entries(query).every(([key, values]) => {
      if (RESERVED.has(key)) return true;
      const m = OPERATOR_KEY.exec(key);
      const [field, op] = m ? [m[1], m[2] as Operator] : [key, "eq" as const];
      // Valeurs répétées (?id=1&id=2) = OU logique
      return values.some((v) => matches(getPath(row, field), op, v));
    }),
  );

  const q = c.req.query("q");
  if (q) items = items.filter((row) => fullText(row, q));

  const sort = c.req.query("_sort");
  if (sort) {
    const orders = (c.req.query("_order") ?? "").split(",");
    const keys = sort.split(",").map((k, i) => {
      const desc = k.startsWith("-") || orders[i]?.toLowerCase() === "desc";
      return { key: k.replace(/^-/, ""), dir: desc ? -1 : 1 };
    });
    items = [...items].sort((a, b) => {
      for (const { key, dir } of keys) {
        const r = compare(getPath(a, key), getPath(b, key));
        if (r !== 0) return r * dir;
      }
      return 0;
    });
  }

  items = items.map((row) => decorate(c, resource, row));
  const total = items.length;

  // Pagination json-server v1 : ?_page=1&_per_page=10 -> enveloppe
  const perPageParam = c.req.query("_per_page");
  if (perPageParam !== undefined) {
    const perPage = Math.max(1, Number.parseInt(perPageParam, 10) || 10);
    const pages = Math.max(1, Math.ceil(total / perPage));
    const page = Math.min(Math.max(1, Number.parseInt(c.req.query("_page") ?? "1", 10) || 1), pages);
    return c.json({
      first: 1,
      prev: page > 1 ? page - 1 : null,
      next: page < pages ? page + 1 : null,
      last: pages,
      pages,
      items: total,
      data: items.slice((page - 1) * perPage, page * perPage),
    });
  }

  // Pagination json-server v0 : ?_page=1&_limit=10 ou ?_start=0&_end=10 -> tableau + X-Total-Count
  const pageParam = c.req.query("_page");
  const limitParam = c.req.query("_limit");
  const startParam = c.req.query("_start");
  const endParam = c.req.query("_end");
  if (pageParam !== undefined || limitParam !== undefined || startParam !== undefined || endParam !== undefined) {
    let start: number;
    let end: number;
    if (pageParam !== undefined) {
      const limit = Math.max(1, Number.parseInt(limitParam ?? "10", 10) || 10);
      const page = Math.max(1, Number.parseInt(pageParam, 10) || 1);
      start = (page - 1) * limit;
      end = start + limit;
    } else {
      start = Math.max(0, Number.parseInt(startParam ?? "0", 10) || 0);
      end = endParam !== undefined ? Number.parseInt(endParam, 10) : limitParam !== undefined ? start + Number.parseInt(limitParam, 10) : total;
    }
    c.header("X-Total-Count", String(total));
    c.header("Access-Control-Expose-Headers", "X-Total-Count");
    return c.json(items.slice(start, end));
  }

  return c.json(items);
});

jsonServer.get("/:resource/:id", (c) => {
  const resource = c.req.param("resource");
  if (!db[resource]) return c.json({}, 404);
  const row = findById(resource, c.req.param("id"));
  return row ? c.json(decorate(c, resource, row)) : c.json({}, 404);
});

jsonServer.post("/:resource", async (c) => {
  const guard = readOnlyGuard(c);
  if (guard) return guard;
  const resource = c.req.param("resource");
  const rows = db[resource];
  if (!rows) return c.json({}, 404);
  const body = await readBody(c);
  if (!body) return c.json({ error: "Corps JSON invalide" }, 400);
  if (body.id !== undefined && findById(resource, body.id)) return c.json({ error: "id déjà utilisé" }, 409);
  const row = { ...body, id: (body.id as string | number | undefined) ?? nextId(rows) } as Row;
  rows.push(row);
  return c.json(row, 201);
});

async function update(c: Context<{ Bindings: Env }>, merge: boolean) {
  const guard = readOnlyGuard(c);
  if (guard) return guard;
  const resource = c.req.param("resource")!;
  const rows = db[resource];
  if (!rows) return c.json({}, 404);
  const index = rows.findIndex((r) => sameId(r.id, c.req.param("id")));
  if (index === -1) return c.json({}, 404);
  const body = await readBody(c);
  if (!body) return c.json({ error: "Corps JSON invalide" }, 400);
  const current = rows[index];
  rows[index] = { ...(merge ? current : {}), ...body, id: current.id } as Row;
  return c.json(rows[index]);
}

jsonServer.put("/:resource/:id", (c) => update(c, false));
jsonServer.patch("/:resource/:id", (c) => update(c, true));

jsonServer.delete("/:resource/:id", (c) => {
  const guard = readOnlyGuard(c);
  if (guard) return guard;
  const resource = c.req.param("resource");
  const rows = db[resource];
  if (!rows) return c.json({}, 404);
  const index = rows.findIndex((r) => sameId(r.id, c.req.param("id")));
  if (index === -1) return c.json({}, 404);
  const [removed] = rows.splice(index, 1);
  return c.json(removed);
});
