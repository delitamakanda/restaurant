import { Hono, type Context } from "hono";
import { db, findById, type Row } from "./store";
import type { Env } from "./env";

/**
 * Routes compatibles avec l'ancienne API Django (coreapp/views.py) :
 * mêmes chemins, mêmes paramètres et même enveloppe de réponse
 * `{ status_code, message, data }`.
 */
export const legacy = new Hono<{ Bindings: Env }>();

type Rec = Record<string, any>;

export const envelope = (data: unknown, status_code = 200, message = "Success") => ({ status_code, message, data });

const methodNotAllowed = (c: Context) => c.json(envelope({}, 405, "Method not allowed"), 405);

const icontains = (value: unknown, search: string) => String(value ?? "").toLowerCase().includes(search.toLowerCase());

const byKey =
  (key: string, desc = false) =>
  (a: Rec, b: Rec) => {
    const r = String(a[key] ?? "").localeCompare(String(b[key] ?? ""), "fr");
    return desc ? -r : r;
  };

const rows = (resource: string) => (db[resource] ?? []) as Rec[];
const resolve = (resource: string, ids: unknown) =>
  (Array.isArray(ids) ? ids : []).map((id) => findById(resource, id)).filter((r): r is Row => Boolean(r)) as Rec[];

/** Équivalent de coreapp/pagination.handle_pagination (django.core.paginator). */
export function paginate<T>(items: T[], pageParam: string | undefined, perPageParam: string | undefined, defaultPerPage: number) {
  const parsedPerPage = Number.parseInt(perPageParam ?? "", 10);
  const perPage = parsedPerPage > 0 ? parsedPerPage : defaultPerPage;
  const numPages = Math.max(1, Math.ceil(items.length / perPage));
  const parsedPage = Number.parseInt(pageParam ?? "", 10);
  let page = Number.isNaN(parsedPage) ? 1 : parsedPage;
  // Django : EmptyPage (page < 1 ou > num_pages) -> dernière page
  if (page < 1 || page > numPages) page = numPages;
  return {
    objectList: items.slice((page - 1) * perPage, page * perPage),
    meta: { total_pages: numPages, current_page: page, per_page: perPage },
  };
}

const activeRestaurants = () => rows("restaurants").filter((r) => !r.is_deleted);

/** Équivalent de Restaurant.restaurant_tags_list (Tags ordonnés par -name). */
const restaurantTags = (restaurant: Rec) =>
  rows("tags")
    .filter((t) => String(t.restaurantId) === String(restaurant.id))
    .sort(byKey("name", true))
    .map((t) => t.name)
    .join(", ");

const addressSummary = (restaurant: Rec) => {
  const address = findById("addresses", restaurant.addressId) as Rec | undefined;
  return { id: address?.id ?? null, street_address: address?.street_address ?? null };
};

legacy.get("/", (c) =>
  c.json(
    envelope({
      products: "/api/products/",
      meals: "/api/meals/",
      menus: "/api/menus/",
      tags: "/api/tags/",
      restaurants: "/api/restaurants/",
      users: "/api/users/",
      categories: "/api/categories/",
      webhook: "/api/webhook/",
    }),
  ),
);

legacy.get("/hello", (c) => c.text("Hello world"));

legacy.get("/api/users", (c) => {
  const search = c.req.query("search") ?? "";
  const users = rows("users")
    .filter((u) => icontains(u.username, search))
    .sort((a, b) => Number(a.id) - Number(b.id));
  const { objectList } = paginate(users, c.req.query("page"), c.req.query("per_page"), 10);
  return c.json(
    envelope({
      users: objectList.map((u) => ({
        id: u.id,
        username: u.username,
        email: u.email,
        contact_number: u.contact_number,
        contact_email: u.contact_email,
        date_joined: u.date_joined,
        first_name: u.first_name,
        last_name: u.last_name,
        is_active: u.is_active,
        is_staff: u.is_staff,
      })),
      search,
    }),
  );
});

legacy.get("/api/restaurants/csv", (c) => {
  const escape = (v: unknown) => {
    const s = String(v ?? "");
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [["id", "name", "address", "phone", "email", "category", "tags"]];
  for (const r of activeRestaurants()) {
    const address = findById("addresses", r.addressId) as Rec | undefined;
    const user = findById("users", r.userId) as Rec | undefined;
    lines.push([
      r.id,
      r.name,
      address ? `${address.street_address}, ${address.locality}, ${address.postal_code}` : "",
      address?.phone ?? "",
      user?.contact_email ?? user?.email ?? "",
      resolve("categories", r.categoryIds)
        .map((cat) => cat.name)
        .join(", "),
      restaurantTags(r),
    ]);
  }
  return c.body(lines.map((l) => l.map(escape).join(",")).join("\r\n") + "\r\n", 200, {
    "Content-Type": "text/csv; charset=utf-8",
    "Content-Disposition": 'attachment; filename="restaurants.csv"',
  });
});

legacy.get("/api/restaurants", (c) => {
  const search = c.req.query("search") ?? "";
  const categories = c.req.queries("categories") ?? [];
  let restaurants = activeRestaurants()
    .filter((r) => icontains(r.name, search))
    .sort(byKey("name"));
  if (categories.length) {
    restaurants = restaurants.filter((r) => (r.categoryIds ?? []).some((id: string) => categories.includes(String(id))));
  }
  const { objectList, meta } = paginate(restaurants, c.req.query("page"), c.req.query("per_page"), 20);
  return c.json(
    envelope({
      restaurants: objectList.map((r) => ({
        id: r.id,
        name: r.name,
        address: addressSummary(r),
        image_url: r.image_url,
        schedule: resolve("schedules", r.scheduleIds).map((s) => ({
          id: s.id,
          day: s.day,
          is_enabled: s.is_enabled,
          start_time: s.begin_hour,
          end_time: s.end_hour,
        })),
        categories: resolve("categories", r.categoryIds).map((cat) => ({ id: cat.id, name: cat.name })),
        menus: resolve("menus", r.menuIds).map((m) => ({ id: m.id })),
        user: r.userId,
        tags: restaurantTags(r),
      })),
      ...meta,
    }),
  );
});

legacy.get("/api/restaurants/:id", (c) => {
  const r = activeRestaurants().find((x) => String(x.id) === c.req.param("id"));
  if (!r) return c.json(envelope({}, 404, "Restaurant not found"), 404);
  return c.json(envelope({ id: r.id, name: r.name, address: addressSummary(r), image_url: r.image_url }));
});

legacy.get("/api/categories", (c) => {
  const categories = [...rows("categories")]
    .sort((a, b) => Number(a.position) - Number(b.position))
    .map(({ id, name, position, image_url }) => ({ id, name, position, image_url }));
  return c.json(envelope({ categories }));
});

legacy.get("/api/products", (c) => {
  const search = c.req.query("search") ?? "";
  const products = rows("products")
    .filter((p) => icontains(p.name, search) || icontains(p.description, search))
    .sort(byKey("name"));
  const { objectList, meta } = paginate(products, c.req.query("page"), c.req.query("per_page"), 99);
  return c.json(
    envelope({
      products: objectList.map((p) => {
        const supplement = p.supplementId ? (findById("supplements", p.supplementId) as Rec | undefined) : undefined;
        return {
          id: p.id,
          name: p.name,
          price: p.price,
          image_url: p.image_url,
          description: p.description,
          supplements: supplement ? [{ id: supplement.id, name: supplement.name, price: supplement.price }] : [],
        };
      }),
      ...meta,
      search,
    }),
  );
});

legacy.get("/api/meals", (c) => {
  const search = c.req.query("search") ?? "";
  const meals = rows("meals")
    .filter((m) => icontains(m.name, search))
    .sort(byKey("name"));
  const { objectList, meta } = paginate(meals, c.req.query("page"), c.req.query("per_page"), 99);
  return c.json(
    envelope({
      meals: objectList.map((m) => ({
        id: m.id,
        name: m.name,
        order: m.order,
        products: resolve("products", m.productIds).map((p) => ({
          id: p.id,
          name: p.name,
          price: p.price,
          image_url: p.image_url,
        })),
      })),
      ...meta,
      search,
    }),
  );
});

legacy.get("/api/menus", (c) => {
  const search = c.req.query("search") ?? "";
  const menus = rows("menus")
    .filter((m) => icontains(m.name, search))
    .sort(byKey("name"));
  const { objectList, meta } = paginate(menus, c.req.query("page"), c.req.query("per_page"), 99);
  return c.json(
    envelope({
      menus: objectList.map((m) => ({
        id: m.id,
        name: m.name,
        description: m.description,
        meals: resolve("meals", m.mealIds).map((meal) => ({ id: meal.id, name: meal.name, order: meal.order })),
      })),
      ...meta,
      search,
    }),
  );
});

legacy.get("/api/tags", (c) => {
  const tags = [...rows("tags")].sort(byKey("name", true)).map(({ id, name }) => ({ id, name }));
  return c.json(envelope({ tags }));
});

/** Comparaison en temps constant (équivalent de secrets.compare_digest). */
function safeEqual(a: string, b: string): boolean {
  const ea = new TextEncoder().encode(a);
  const eb = new TextEncoder().encode(b);
  let diff = ea.length ^ eb.length;
  for (let i = 0; i < Math.max(ea.length, eb.length); i++) diff |= (ea[i] ?? 0) ^ (eb[i] ?? 0);
  return diff === 0;
}

legacy.post("/api/webhook", async (c) => {
  const expected = c.env?.WEBHOOK_TOKEN ?? "";
  const given = c.req.header("Webhook-Token") ?? "";
  if (!expected || !safeEqual(given, expected)) return c.text("Invalid webhook token", 403);

  let payload: unknown;
  try {
    payload = await c.req.json();
  } catch {
    return c.text("Invalid JSON payload", 400);
  }

  const now = new Date();
  const cutoff = now.getTime() - 7 * 24 * 60 * 60 * 1000;
  const messages = (db.webhookMessages ??= []);
  for (let i = messages.length - 1; i >= 0; i--) {
    if (new Date(String(messages[i].received_at)).getTime() <= cutoff) messages.splice(i, 1);
  }
  messages.push({ id: crypto.randomUUID(), received_at: now.toISOString(), payload });
  return c.text("Message received");
});

// Autres méthodes sur les routes GET-only -> 405 (comme les vues Django)
for (const path of [
  "/api/users",
  "/api/restaurants",
  "/api/restaurants/csv",
  "/api/restaurants/:id",
  "/api/categories",
  "/api/products",
  "/api/meals",
  "/api/menus",
  "/api/tags",
  "/api/webhook",
]) {
  legacy.all(path, methodNotAllowed);
}

legacy.get("/sitemap.xml", (c) => {
  const origin = new URL(c.req.url).origin;
  const urls = activeRestaurants()
    .map(
      (r) =>
        `<url><loc>${origin}/restaurants/${r.id}</loc><lastmod>${String(r.created_at).slice(0, 10)}</lastmod>` +
        `<changefreq>weekly</changefreq><priority>0.5</priority></url>`,
    )
    .join("");
  return c.body(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}</urlset>\n`,
    200,
    { "Content-Type": "application/xml" },
  );
});
