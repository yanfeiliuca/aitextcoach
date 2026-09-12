# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AITextCoach (aitextcoach.com) — an AI text rewriting/humanizing tool. A Cloudflare Worker (TypeScript API) backed by D1 (SQLite) and KV, paired with static HTML pages deployed separately via Cloudflare Pages. Migrated from a Render (Python/Postgres) stack in 2026-07; see `docs/sop/MIGRATION_SOP.md` for migration history and hard-won lessons (not committed to git — local only).

## Commands

```bash
npm run dev      # wrangler dev — local Worker dev server
npm run deploy    # wrangler deploy — deploy Worker to Cloudflare
npm run cf-typegen # regenerate Cloudflare binding types
```

There is no test suite or linter configured in this repo.

**Static pages** (`public/`) are deployed separately, not via `npm run deploy`:
```bash
npx wrangler pages deploy public --project-name=aitextcoach --branch=main
```

**D1 migrations** are applied manually (no migration runner):
```bash
npx wrangler d1 execute aitextcoach-db --remote --file ./migrations/0001_initial.sql
```

**Secrets** (not in `wrangler.toml`, set via wrangler):
```bash
npx wrangler secret put DS_API_KEY            # DeepSeek API key
npx wrangler secret put PAYPAL_CLIENT_SECRET
```

## Architecture

**Two separately-deployed pieces on two subdomains** — this split is load-bearing, not incidental:
- `api.aitextcoach.com` → the Worker (`src/index.ts`, this repo's `npm run deploy` target). Must be bound to its own Custom Domain in the Cloudflare dashboard, NOT routed through Pages — POST requests to `/api/*` get intercepted (405) if Pages owns the route instead.
- `aitextcoach.com` → static pages in `public/`, deployed via `wrangler pages deploy`. Each HTML page hardcodes `const API_BASE = 'https://api.aitextcoach.com'` and calls `fetch(API_BASE + '/api/...')` for all backend calls (see `public/index.html`).

**Worker structure** (`src/`):
- `index.ts` — all HTTP routing (flat if-chain on `url.pathname` + `method`, no framework/router), CORS handling, request/response JSON parsing.
- `db.ts` — all D1 queries. Exports the `Env` interface (bindings: `DB`, `KV`, `DS_API_KEY`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_MODE`, `PAYPAL_PLAN_ID`).
- `deepseek.ts` — DeepSeek API integration (`callDeepSeek`) plus budget tracking logic.

**API endpoints** (all under `/api/`, routed in `index.ts`):

| Endpoint | Method | Notes |
|---|---|---|
| `/enhance` | POST | Rewrites text; enforces free quota + budget mode |
| `/activate-pro` | POST | Verifies a PayPal subscription, marks the email Pro |
| `/config` | GET | Returns PayPal client ID/mode/plan ID for the frontend |
| `/check-pro` | GET | Looks up Pro status by email |
| `/track-click` | POST | Increments `click_stats` for a button |
| `/stats` | GET | Dashboard data (click stats + budget state) |
| `/debug-add-pro` | POST | Manually marks an email Pro — **no auth guard**, callable by anyone with the URL |

**Writing styles**: `formal`, `casual` (default), `academic`, `simple`, `creative`, `business` — prompt templates live in the `prompts` map in `deepseek.ts`.

**Budget control**: spend is tracked in KV (`budget_state` key) as a running dollar total against a $10 hardcoded limit (`BUDGET_LIMIT` in `deepseek.ts`). `checkBudget()` derives a mode from spend percentage: `normal` (<75%) → `limited` (75-95%, caps response to 300 tokens) → `critical` (≥95%, refuses new DeepSeek calls entirely, returns 503). Cost is estimated per-call from a rough tokens≈chars/4 heuristic, not the API's actual usage figures.

**Usage quotas**: free users get 500 chars/day tracked in `usage_stats` (D1, keyed by lowercased email + date, `email` is nullable/anonymous-tolerant); Pro users (`users.is_pro`) are unlimited. Pro status is granted via PayPal subscription verification (`handleActivatePro`) or the `/api/debug-add-pro` backdoor route (no auth guard — be aware this is callable by anyone with the URL).

**PayPal Pro upgrade flow**: user clicks "Upgrade to Pro" → PayPal subscription popup → frontend calls `/api/activate-pro` with the subscription ID → Worker verifies subscription status directly with PayPal's API (OAuth token, then `GET /v1/billing/subscriptions/{id}`, checks `status === "ACTIVE"`) → `users.is_pro` set in D1. The PayPal client ID is hardcoded in `handleConfig`/`handleActivatePro` in `index.ts` (not env-injected); only `PAYPAL_CLIENT_SECRET` is a secret. See `PAYPAL_SETUP.md` for full setup steps.

**D1 schema** (`migrations/0001_initial.sql`): `users`, `usage_stats`, `click_stats`. No migration framework — new schema changes require hand-writing a new numbered `.sql` file and running it manually against `--remote`.

## Conventions

- All API responses go through `jsonResponse()` in `index.ts`, which always attaches the shared `CORS_HEADERS` (wildcard origin).
- Emails are always lowercased+trimmed before use as a lookup key — do this consistently in any new handler touching `users` or `usage_stats`.
- D1 upserts use `ON CONFLICT ... DO UPDATE` (see `db.ts`) rather than manual read-then-write.
