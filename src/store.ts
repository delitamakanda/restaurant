import seed from "../db.json";

export type Row = Record<string, unknown> & { id: string | number };
export type Db = Record<string, Row[]>;

/**
 * Base en mémoire, initialisée depuis db.json.
 *
 * Sur Cloudflare Workers, chaque isolate possède sa propre copie : les
 * écritures (POST/PUT/PATCH/DELETE, webhooks) sont volatiles et ne sont pas
 * partagées entre isolates ni conservées entre déploiements.
 */
export let db: Db = structuredClone(seed) as unknown as Db;

export function resetDb(): void {
  db = structuredClone(seed) as unknown as Db;
}

export const sameId = (a: unknown, b: unknown): boolean => String(a) === String(b);

export function findById(resource: string, id: unknown): Row | undefined {
  return db[resource]?.find((r) => sameId(r.id, id));
}
