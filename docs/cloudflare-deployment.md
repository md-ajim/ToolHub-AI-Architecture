# Cloudflare Deployment Guide — ToolHub-AI

Version: v1.0
Status: Additive (does not replace the existing Docker deployment)

---

## Overview

ToolHub-AI is a Docker-based monolith: **Next.js 16 frontend** + **Django
backend** (Postgres / Redis / Celery). Cloudflare is used in three separate,
independent layers:

| Layer | What | Status |
| --- | --- | --- |
| Workers AI | Backend image generation / editing provider (SDXL, SD1.5, FLUX.2 klein) | ✅ Live & verified |
| Tunnel | Forward the whole Docker stack through Cloudflare edge (no open inbound ports) | Optional service in docker-compose |
| Pages/DNS/CDN | Frontend edge hosting + domain + cache | Needs a zone + Pages-scoped token |

Everything below is **additive** — the existing Docker stack keeps working
unchanged.

---

## 1. Workers AI (image provider) — DONE

Already integrated in `backend/apps/ai_tools/providers/cloudflare.py`.

### Verified live (2026-09-08)

| Check | Result |
| --- | --- |
| `GET /client/v4/user/tokens/verify` | `success: true`, token `active` |
| `GET /accounts/{id}/ai/models/search` | `success: true` |
| `POST /ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0` | `HTTP 200`, valid PNG returned |
| FLUX.2 klein (`@cf/black-forest-labs/flux-2-klein-4b`) | HTTP 400 expects `multipart` — provider already sends multipart (`input_image_0`) |

### Required env (already in `.env` / `.env.example`)

```dotenv
CLDFLARE_ACCOUNT_ID=<account id>
CLDFLARE_API_TOKEN=<Workers AI token>   # scope: "Workers AI: Run" only
```

### Note on token scope

The current token is scoped **to Workers AI only**: calling `/zones`,
`/accounts/{id}/pages/projects`, or `/user` returns `403`/`9109`. That is
intentional and sufficient for Workers AI, but any Pages/DNS config below will
need a second token with the matching zone permissions.

### Provider behavior

- Registered only when both credentials are set (`is_configured()`).
- Model registry `get_image_models()` hides Cloudflare entries until configured.
- SD1.5 img2img/inpaint models that are not permitted on the account fall back
  to FLUX.2 klein automatically.
- All jobs flow through the existing job pipeline, credits and entitlement
  checks.

---

## 2. Cloudflare Tunnel (expose the Docker stack) — config added

Adds an optional `cloudflared` service to `docker-compose.yml` under the
`cloudflare` compose profile, so the default `docker compose up` behaviour is
unchanged.

### Start

```bash
docker compose --profile cloudflare up -d
```

### Setup

1. Zero Trust → Networks → Tunnels → **Create a tunnel** (remotely-managed).
2. Copy the tunnel token into `CLOUDFLARE_TUNNEL_TOKEN` (in `.env`).
3. In the tunnel dashboard add public hostnames:
   - `app.example.com` → `http://localhost:3000` (frontend)
   - `api.example.com` → `http://localhost:8000` (backend)
4. `cloudflared` uses `network_mode: host` + `extra_hosts` so
   `host.docker.internal` still resolves for ComfyUI/self-hosted AI.

No inbound firewall ports are opened; Cloudflare edge proxies traffic to the
tunnel.

---

## 3. Cloudflare Pages / DNS / CDN (frontend edge) — files added

The frontend is already fully env-driven:
- `NEXT_PUBLIC_API_URL` (default `/api/v1`) — see `src/lib/api.ts`,
  `src/features/auth/services/authApi.ts`
- `NEXT_PUBLIC_SITE_URL` / `NEXT_PUBLIC_APP_URL` — SEO/metadata

Added files:

- `frontend/wrangler.toml` — Pages project config (`toolhub-frontend`)
- `frontend/.dev.vars.example` — local secret template for `wrangler pages dev`

### Deploying the frontend to Pages (requires a Pages-scoped token)

```bash
cd frontend
npm i -D @cloudflare/next-on-pages   # or @opennextjs/cloudflare adapter
npx wrangler pages project create toolhub-frontend --production-branch main
# add build output dir + build command in dashboard (out/ for static export,
# or @cloudflare/next-on-pages for SSR)
npm run build
npx wrangler pages deploy out --project-name toolhub-frontend
# production env secrets:
npx wrangler pages secret put NEXT_PUBLIC_SITE_URL --project-name toolhub-frontend
npx wrangler pages secret put NEXT_PUBLIC_APP_URL --project-name toolhub-frontend
```

### DNS / CDN

- Put the custom domain on the zone (dashboard: Pages project → Custom domains).
- Proxy status = **Proxied (orange cloud)** so Cloudflare CDN, caching and
  DDoS protection apply automatically.
- WAF / bot rules: optional, enable in Security → WAF.

### Backend reachability for the edge frontend

`next.config.ts` currently rewrites `/api/*` and `/media/*` to
`http://backend:8000` **inside Docker**. When the frontend runs on Pages, point
`NEXT_PUBLIC_API_URL` at a public HTTPS backend origin instead (Cloudflare
Tunnel hostname from section 2, or the VPS behind Cloudflare DNS).

---

## 4. Validation

```bash
# docker-compose syntax
docker compose config --quiet && echo VALID

# backend Cloudflare provider unit tests (all networking mocked)
docker compose run --rm backend python manage.py test \
  backend.tests.unit.apps.ai_tools.test_cloudflare_provider
```

### Live credential check (read-only)

```bash
TOKEN=<CLDFLARE_API_TOKEN>
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.cloudflare.com/client/v4/user/tokens/verify
```

---

## Files touched

| File | Change |
| --- | --- |
| `docker-compose.yml` | Added optional `cloudflared` service (profile `cloudflare`) |
| `frontend/wrangler.toml` | New — Cloudflare Pages config |
| `frontend/.dev.vars.example` | New — Pages local secrets template |
| `.env.example` | Added Cloudflare Tunnel + Pages env docs |
| `docs/cloudflare-deployment.md` | This guide |

No existing service, route, model or env file was removed or renamed.