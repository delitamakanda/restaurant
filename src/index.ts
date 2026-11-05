import { Hono } from "hono";
import { cors } from "hono/cors";
import type { Env } from "./env";
import { envelope, legacy } from "./legacy";
import { jsonServer } from "./jsonServer";

// strict: false -> /api/restaurants et /api/restaurants/ sont équivalents (APPEND_SLASH Django)
const app = new Hono<{ Bindings: Env }>({ strict: false });

app.use("*", async (c, next) => {
  const allowed = (c.env?.CORS_ORIGINS ?? "*").split(",").map((o) => o.trim());
  return cors({
    origin: allowed.includes("*") ? "*" : allowed,
    exposeHeaders: ["X-Total-Count"],
  })(c, next);
});

// Les routes de compatibilité Django passent avant les routes génériques /:resource
app.route("/", legacy);
app.route("/", jsonServer);

app.notFound((c) => c.json(envelope({}, 404, "Not found"), 404));
app.onError((err, c) => {
  console.error(err);
  return c.json(envelope({}, 500, "Internal server error"), 500);
});

export default app;
