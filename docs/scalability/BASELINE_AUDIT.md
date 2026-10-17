# ToolHub-AI Scalability Baseline Audit

Date: 2026-10-14. Method: code inspection + test execution. No live benchmarks were
run (no staging infra with Redis/Postgres/AI keys); no invented numbers below.

## 1. Inventory (verified)

- Backend: Django 6.1 + DRF, 28 apps in `backend/apps/` (`accounts, admin_logs,
  admin_panel, affiliates, ai, ai_tools, ai_workspace, analytics, api, api_keys,
  audio_tools, authentication, billing, blog, business_tools, data_science,
  developer_tools, ecommerce_studio, image_tools, notifications, pdf_tools,
  processing, seo_tools, storage, subscriptions, system, video_tools, workspace`).
  Real routing lives in `apps/ai_workspace/{gateway,routing,provider_registry}.py`
  and `apps/ai_tools/{services,registry,tasks}.py` (`services/`, `workers/`,
  `integrations/` contain only `__init__.py`).
- Frontend: Next.js 16.3 + React 19, 146 `page.tsx` routes, heavy editor deps
  (`fabric@7, jspdf, jszip, html2canvas-pro, react-advanced-cropper`), only 3x
  `next/dynamic` splits, polling everywhere (no SSE/WS), no list virtualization.
- Infra: `docker-compose.yml` (postgres:15, redis:7, backend gunicorn 2 workers /
  120s timeout, celery + beat, frontend, optional cloudflared). Dev default DB is
  SQLite (`db.sqlite3` present). No nginx, no CDN, media served by Django
  (`SERVE_MEDIA`).
- Package manager: pip (`requirements/base.txt`); frontend npm. Tests: pytest
  (700 collected) + vitest (not run — node env untouched).

## 2. Request lifecycles (verified)

- Web: browser → Next.js → `/api/*` rewrite → Django DRF (JWT) → Postgres/Redis.
- AI: `TOOL_REGISTRY → AiService.runOperation → entitlement/credit reserve →
  Celery → provider → persist → settle/refund → frontend polls job`.
- Billing: Stripe/LemonSqueezy/bKash/Nagad webhooks → signature verify →
  `WebhookEvent` dedup → `select_for_update` state machine → idempotent credit
  allocation. Credit core (`CreditService._apply_credit_change`) uses
  `select_for_update` + idempotency/reference dedup + non-negative guard. Strong.
- Files: multipart → `user_<id>/uuid_name` on local disk → File row; AI artefacts
  via `FileField` on local disk. No S3, no signed URLs, no retention purge.

## 3. Findings by severity

### P0 (fixed this pass)
1. `apps/workspace/views.py` — `Folder` used but never imported: every folder
   endpoint 500'd (`NameError`). 5 baseline tests failed. FIXED (import added;
   23/23 storage tests pass).
2. Google OAuth userinfo `req.get` had no `timeout` (worker hang risk; GitHub
   calls already had `timeout=10`). FIXED.

### P0 (documented, not changed — needs product/infra decision)
3. No pagination anywhere (`shared/pagination.py` was empty; all lists unbounded,
   e.g. `storage/views.py`, `workspace/views.py`, `billing/views.py`). Partially
   addressed: storage list now bounded (200 legacy cap + opt-in `?page&page_size`,
   max 100) with legacy shape preserved. Other lists still unbounded.
4. DRF throttles disabled when `DEBUG=True`; `anon 10000/day / user 100000/day`
   ≈ unlimited. Left as-is (changing rates risks breaking paid use; flagged).
5. Local-disk media + Django-served `/media/*`: single point of failure for
   multi-instance deploys. Documented; migration to object storage deferred.

### P1 (fixed this pass)
6. `File`/`ProcessedFile`/`Payment`/`Invoice`/`Project`/`History` had no indexes
   for their hottest filters. FIXED via additive migrations (`storage 0004`,
   `billing 0007`, `workspace 0005`).
7. `FileDetailView.delete` left orphaned bytes on disk. FIXED (best-effort
   `default_storage.delete`).
8. Bare `@shared_task` (analytics, subscriptions sweep, data-science, image
   worker) had no time limits/acks_late. FIXED (bounded, `acks_late=True`).
9. Single `HealthCheckView` for liveness+readiness; provider/DB blip = whole app
   "unhealthy". FIXED: `/health/` (liveness, dependency-free) + `/ready/`
   (DB+cache checks, 503 when DB down, cache fail-open).
10. N+1 on storage list (folder/project per row). FIXED (`select_related`).
11. DB connections: no `CONN_MAX_AGE`/health checks; Redis cache: no socket
    timeouts; Celery: no global time limits/result expiry/prefetch guard.
    FIXED with env-overridable defaults.

### P2/P3 (verified, left for follow-up)
- `pdf_tools/conversion_services.py` already has `timeout=120` (earlier report of
  missing timeout was stale). `ai_tools/tasks.py` already hardened
  (soft 3600/hard 3900, claim + idempotent finalize). Billing money path already
  atomic + idempotent (not migrated wholesale per directive).
- In-memory `_ADAPTER_CACHE` / live-status mtime cache diverge across replicas;
  ML model in web RAM; `str(e)` error passthroughs; frontend bundle/polling work.
  See IMPLEMENTATION_REPORT §J.

## 4. Baseline test evidence

- `pytest tests --collect-only`: 700 tests.
- Redis unavailable in this env (`Connection refused` on localhost:6379):
  Redis-dependent tests fail at baseline (e.g. affiliates attribution).
- `tests/unit/apps/storage`: baseline 5 failed / 18 passed → after fix 23 passed.
- `billing+subscriptions+authentication` subset: 9 failed / 118 passed, byte-identical
  on stashed baseline (pre-existing: auth API/hardening + 1 billing retry test).
- `manage.py check`: clean. `makemigrations --check`: clean after new migrations.
- Frontend vitest + load benchmarks: NOT RUN (no node/prod env here).
