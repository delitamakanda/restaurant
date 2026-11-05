# Restaurant API — mock json-server sur Cloudflare Workers

<!-- START doctoc -->
<!-- END doctoc -->

[![CI](https://github.com/delitamakanda/restaurant/actions/workflows/ci.yaml/badge.svg?branch=main&event=push)](https://github.com/delitamakanda/restaurant/actions/workflows/ci.yaml)

Mock de l'API Restaurant (anciennement une application Django), servi par un
[Cloudflare Worker](https://developers.cloudflare.com/workers/) à partir d'un
fichier [`db.json`](db.json) au format [json-server](https://github.com/typicode/json-server).

Le Worker expose deux familles de routes :

- **`/api/*`** : compatibilité avec l'ancienne API Django. Les chemins, les paramètres et
  l'enveloppe `{ status_code, message, data }` sont identiques, donc les fronts existants
  fonctionnent sans modification.
- **`/:resource`** : routes génériques façon json-server (filtres, tri, pagination,
  relations, CRUD) sur toutes les collections de `db.json`.

json-server dépend de Node et du système de fichiers, donc il ne tourne pas tel quel sur
Workers. Ses routes sont réimplémentées avec [Hono](https://hono.dev) dans
[`src/jsonServer.ts`](src/jsonServer.ts).

---

## Stack

| Couche | Technologie |
|--------|-------------|
| Runtime | Cloudflare Workers |
| Routeur | Hono |
| Données | `db.json` (embarqué dans le bundle) |
| Langage | TypeScript |
| Tests | Vitest |
| Déploiement | Cloudflare Workers Builds (intégration Git) |

## Démarrage

```bash
npm install
cp .dev.vars.example .dev.vars   # WEBHOOK_TOKEN pour le dev local
npm run dev                      # http://localhost:8787 (runtime workerd)
```

Autres scripts :

| Commande | Rôle |
|----------|------|
| `npm test` | Tests Vitest |
| `npm run typecheck` | Vérification TypeScript |
| `npm run deploy` | Déploiement sur Cloudflare |
| `npm run mock:local` | Lance le vrai `json-server` sur `db.json` (port 3000), sans Worker et sans les routes `/api/*` |

## Données

Toutes les données sont dans [`db.json`](db.json). Les relations suivent les conventions de json-server :

| Collection | Relations |
|------------|-----------|
| `users` | — |
| `addresses` | `customerId` → users |
| `schedules` | — |
| `categories` | — |
| `supplements` | — |
| `products` | `supplementId` → supplements |
| `meals` | `productIds[]` → products |
| `menus` | `mealIds[]` → meals |
| `restaurants` | `userId`, `addressId`, `scheduleIds[]`, `categoryIds[]`, `menuIds[]`, `is_deleted` |
| `tags` | `restaurantId` → restaurants |
| `orders` | `restaurantId`, `createdById`, `updatedById` |
| `orderItems` | `orderId` → orders |
| `webhookMessages` | rempli par `POST /api/webhook/` |

> **Persistance** : les écritures (POST/PUT/PATCH/DELETE, webhooks) restent en mémoire, dans
> l'isolate du Worker. Elles sont perdues au redémarrage et ne sont pas partagées entre
> isolates ni entre régions. Pour modifier les données de façon durable, éditez `db.json`
> puis redéployez.

## Routes compatibles Django (`/api/*`)

Le slash final est optionnel.

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Racine de l'API |
| GET | `/hello` | Health-check (`Hello world`) |
| GET | `/api/restaurants/` | Liste paginée (`page`, `per_page`=20, `search`, `categories` répétable) |
| GET | `/api/restaurants/<id>/` | Détail d'un restaurant |
| GET | `/api/restaurants/csv/` | Export CSV |
| GET | `/api/categories/` | Catégories triées par `position` |
| GET | `/api/products/` | Produits (`page`, `per_page`=99, `search`) |
| GET | `/api/meals/` | Formules (`page`, `per_page`=99, `search`) |
| GET | `/api/menus/` | Menus (`page`, `per_page`=99, `search`) |
| GET | `/api/tags/` | Tags |
| GET | `/api/users/` | Utilisateurs (`page`, `per_page`=10, `search`) |
| POST | `/api/webhook/` | Webhook (en-tête `Webhook-Token` requis) |
| GET | `/sitemap.xml` | Sitemap des restaurants |

Les restaurants avec `is_deleted: true` sont exclus, comme avec le soft-delete Django.

## Routes json-server (`/:resource`)

| Méthode | Route |
|---------|-------|
| GET | `/db` |
| GET | `/:resource` |
| GET | `/:resource/:id` |
| POST | `/:resource` |
| PUT / PATCH / DELETE | `/:resource/:id` |

Paramètres de `GET /:resource` :

| Paramètre | Exemple |
|-----------|---------|
| Égalité (valeurs répétées = OU) | `/users?is_staff=true`, `/tags?restaurantId=…` |
| Opérateurs `_ne`, `_lt`, `_lte`, `_gt`, `_gte`, `_like` (ou `:lt`…) | `/products?price_lt=5` |
| Recherche plein texte | `/products?q=pizza` |
| Tri (`-` = décroissant, ou `_order=desc`) | `/products?_sort=-price` |
| Pagination v1 (enveloppe `first/prev/next/last/pages/items/data`) | `/products?_page=2&_per_page=5` |
| Pagination v0 (tableau + en-tête `X-Total-Count`) | `/products?_page=2&_limit=5`, `?_start=0&_end=5` |
| Relations enfants / N-N | `/restaurants/<id>?_embed=tags&_embed=categories` |
| Relation parente | `/tags?_expand=restaurant` |

## Configuration

| Variable | Type | Défaut | Rôle |
|----------|------|--------|------|
| `WEBHOOK_TOKEN` | secret | — | Jeton attendu par `/api/webhook/`. Sans lui, tous les webhooks sont refusés |
| `READ_ONLY` | var | `"false"` | `"true"` refuse les écritures sur `/:resource` (403) |
| `CORS_ORIGINS` | var | `"*"` | Origines autorisées, séparées par des virgules |

```bash
npx wrangler secret put WEBHOOK_TOKEN
```

## Déploiement

```bash
npx wrangler login
npm run deploy
```

La CI ([`.github/workflows/ci.yaml`](.github/workflows/ci.yaml)) lance le typecheck, les
tests et un `wrangler deploy --dry-run` sur chaque PR et chaque push. Elle ne déploie pas :
le déploiement est assuré par Cloudflare Workers Builds, connecté directement au dépôt GitHub,
qui déploie automatiquement à chaque push sur `main`. Aucun secret Cloudflare n'est nécessaire
côté GitHub.
