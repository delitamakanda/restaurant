import { beforeEach, describe, expect, it } from "vitest";
import app from "../src/index";
import { db, resetDb } from "../src/store";

const env = { WEBHOOK_TOKEN: "secret-token", READ_ONLY: "false" };
const get = (path: string) => app.request(path, {}, env);
const send = (method: string, path: string, body?: unknown, headers: Record<string, string> = {}) =>
  app.request(
    path,
    { method, body: body === undefined ? undefined : JSON.stringify(body), headers: { "Content-Type": "application/json", ...headers } },
    env,
  );

const json = async (res: Response | Promise<Response>): Promise<any> => (await res).json();

beforeEach(() => resetDb());

describe("compatibilité API Django", () => {
  it("GET /hello", async () => {
    const res = await get("/hello");
    expect(res.status).toBe(200);
    expect(await res.text()).toBe("Hello world");
  });

  it("GET / renvoie la racine de l'API", async () => {
    const body = await json(get("/"));
    expect(body).toMatchObject({ status_code: 200, message: "Success" });
    expect(body.data.restaurants).toBe("/api/restaurants/");
  });

  it("GET /api/restaurants/ exclut les restaurants supprimés et pagine", async () => {
    const body = await json(get("/api/restaurants/"));
    const names = body.data.restaurants.map((r: any) => r.name);
    expect(names).not.toContain("Ancien Bistrot");
    expect(names).toEqual([...names].sort((a: string, b: string) => a.localeCompare(b, "fr")));
    expect(body.data).toMatchObject({ total_pages: 1, current_page: 1, per_page: 20 });
    const first = body.data.restaurants[0];
    expect(first).toHaveProperty("address.street_address");
    expect(first.schedule[0]).toHaveProperty("start_time");
    expect(typeof first.tags).toBe("string");
  });

  it("le slash final est optionnel", async () => {
    expect((await get("/api/restaurants")).status).toBe(200);
  });

  it("filtre les restaurants par recherche et catégorie", async () => {
    const search = await json(get("/api/restaurants/?search=saku"));
    expect(search.data.restaurants.map((r: any) => r.name)).toEqual(["Sakura"]);

    const burgers = db.categories.find((c) => c.name === "Burgers")!;
    const byCat = await json(get(`/api/restaurants/?categories=${burgers.id}`));
    expect(byCat.data.restaurants.map((r: any) => r.name)).toEqual(["Big Smash"]);
  });

  it("pagination : page hors limites -> dernière page", async () => {
    const body = await json(get("/api/restaurants/?per_page=2&page=99"));
    expect(body.data).toMatchObject({ total_pages: 3, current_page: 3, per_page: 2 });
    expect(body.data.restaurants).toHaveLength(1);
  });

  it("GET /api/restaurants/:id et 404", async () => {
    const r = db.restaurants.find((x) => !x.is_deleted)!;
    const ok = await json(get(`/api/restaurants/${r.id}/`));
    expect(ok.data.name).toBe(r.name);

    const deleted = db.restaurants.find((x) => x.is_deleted)!;
    const res = await get(`/api/restaurants/${deleted.id}/`);
    expect(res.status).toBe(404);
    expect(await json(res)).toMatchObject({ status_code: 404, message: "Restaurant not found" });
  });

  it("GET /api/categories/ triées par position", async () => {
    const body = await json(get("/api/categories/"));
    const positions = body.data.categories.map((c: any) => c.position);
    expect(positions).toEqual([...positions].sort((a, b) => a - b));
  });

  it("GET /api/products/ inclut les suppléments", async () => {
    const body = await json(get("/api/products/?search=pizza"));
    expect(body.data.products.length).toBe(2);
    expect(body.data.products[0].supplements[0]).toHaveProperty("price");
    expect(body.data.per_page).toBe(99);
  });

  it("GET /api/meals/, /api/menus/, /api/tags/, /api/users/", async () => {
    const meals = await json(get("/api/meals/"));
    expect(meals.data.meals[0].products.length).toBeGreaterThan(0);
    const menus = await json(get("/api/menus/"));
    expect(menus.data.menus[0].meals.length).toBeGreaterThan(0);
    const tags = await json(get("/api/tags/"));
    expect(tags.data.tags.length).toBe(db.tags.length);
    const users = await json(get("/api/users/?search=ali"));
    expect(users.data.users.map((u: any) => u.username)).toEqual(["alice"]);
  });

  it("GET /api/restaurants/csv/", async () => {
    const res = await get("/api/restaurants/csv/");
    expect(res.headers.get("content-type")).toContain("text/csv");
    const lines = (await res.text()).trim().split("\r\n");
    expect(lines[0]).toBe("id,name,address,phone,email,category,tags");
    expect(lines).toHaveLength(6);
  });

  it("méthode non autorisée -> 405", async () => {
    const res = await send("POST", "/api/restaurants/", {});
    expect(res.status).toBe(405);
  });

  it("webhook : jeton requis, message stocké", async () => {
    expect((await send("POST", "/api/webhook/", { a: 1 }, { "Webhook-Token": "nope" })).status).toBe(403);
    const res = await send("POST", "/api/webhook/", { a: 1 }, { "Webhook-Token": "secret-token" });
    expect(res.status).toBe(200);
    expect(await res.text()).toBe("Message received");
    expect(db.webhookMessages).toHaveLength(1);
  });

  it("webhook refusé si aucun jeton n'est configuré", async () => {
    const res = await app.request("/api/webhook/", { method: "POST", body: "{}", headers: { "Webhook-Token": "" } }, {});
    expect(res.status).toBe(403);
  });
});

describe("routes json-server", () => {
  it("GET /:resource et /:resource/:id", async () => {
    const list = await json(get("/categories"));
    expect(list).toHaveLength(db.categories.length);
    const one = await json(get(`/categories/${list[0].id}`));
    expect(one.name).toBe(list[0].name);
    expect((await get("/categories/inconnu")).status).toBe(404);
    expect((await get("/inconnu")).status).toBe(404);
  });

  it("filtres, opérateurs, q et tri", async () => {
    const staff = await json(get("/users?is_staff=true"));
    expect(staff.map((u: any) => u.username)).toEqual(["admin"]);

    const cheap = await json(get("/products?price_lt=5&_sort=price"));
    expect(cheap.map((p: any) => p.price)).toEqual(["3.50", "4.00", "4.50"]);

    const desc = await json(get("/products?_sort=-price&_limit=1"));
    expect(desc[0].name).toBe("Butter chicken");

    const q = await json(get("/products?q=matcha"));
    expect(q.map((p: any) => p.name)).toEqual(["Mochi glacé"]);
  });

  it("pagination v0 (_page/_limit) et v1 (_per_page)", async () => {
    const v0 = await get("/products?_page=2&_limit=5");
    expect(v0.headers.get("X-Total-Count")).toBe("12");
    expect(await json(v0)).toHaveLength(5);

    const v1 = await json(get("/products?_page=3&_per_page=5"));
    expect(v1).toMatchObject({ first: 1, prev: 2, next: null, last: 3, pages: 3, items: 12 });
    expect(v1.data).toHaveLength(2);
  });

  it("_embed et _expand", async () => {
    const sakura = db.restaurants.find((r) => r.name === "Sakura")!;
    const r = await json(get(`/restaurants/${sakura.id}?_embed=tags&_embed=categories&_expand=address`));
    expect(r.tags.map((t: any) => t.name).sort()).toEqual(["ramen", "sushi"]);
    expect(r.categories.map((c: any) => c.name)).toEqual(["Japonais"]);
    expect(r.address.locality).toBe("Paris");
  });

  it("CRUD en mémoire", async () => {
    const created = await json(send("POST", "/tags", { name: "nouveau", restaurantId: "x" }));
    expect(created.id).toBeTruthy();

    const patched = await json(send("PATCH", `/tags/${created.id}`, { name: "modifié" }));
    expect(patched).toMatchObject({ name: "modifié", restaurantId: "x" });

    const put = await json(send("PUT", `/tags/${created.id}`, { name: "remplacé" }));
    expect(put).toEqual({ id: created.id, name: "remplacé" });

    expect((await send("DELETE", `/tags/${created.id}`)).status).toBe(200);
    expect((await get(`/tags/${created.id}`)).status).toBe(404);

    const user = await json(send("POST", "/users", { username: "dave" }));
    expect(user.id).toBe(5);
  });

  it("READ_ONLY bloque les écritures", async () => {
    const res = await app.request("/tags", { method: "POST", body: "{}" }, { READ_ONLY: "true" });
    expect(res.status).toBe(403);
  });
});
