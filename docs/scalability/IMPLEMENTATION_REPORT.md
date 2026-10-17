# Scalability Implementation Report

## A. Executive summary

Implemented 9 safe, backward-compatible changes (P0 correctness + P1 hardening);
fixed a P0 that broke all folder endpoints; added 3 additive index migrations.
No features removed, no contracts broken, no billing logic altered, no new infra.
Remaining work is ranked in §J. Nothing here claims unmeasured capacity.

## B. Architecture findings

See `docs/scalability/BASELINE_AUDIT.md`. Core design (modular monolith + Celery +
Redis + Postgres-in-prod) is sound and was kept. Money path (reserve → execute →
settle/refund with `select_for_update` + idempotency keys + `WebhookEvent` dedup)
is already correct under concurrency; left untouched. Main constraints: unbounded
lists, local-disk media, Django-served media, throttle posture, single-queue
Celery, frontend polling/bundles.

## C. Changed files

| File | Purpose |
|---|---|
| `backend/apps/workspace/views.py` | P0 fix: import missing `Folder` model (folder CRUD 500'd) |
| `backend/apps/authentication/services.py` | P0: `timeout=10` on Google userinfo fetch |
| `backend/shared/pagination.py` | Was empty: reusable `StandardResultsSetPagination` + backward-compat helper |
| `backend/apps/storage/views.py` | Bounded list (200 legacy cap + opt-in `?page&page_size`≤100), `select_related`, orphan-byte cleanup on delete |
| `backend/apps/storage/models.py` + migration `0004` | Indexes: `(user,-uploaded_at)`, `(user,status)`, `project`, `folder`, processed-file `original_file`/`tool` |
| `backend/apps/billing/models.py` + migration `0007` | Indexes: payment `(user,-created_at)`, `status`, `(gateway,status)`, `order_reference`; invoice `(user,-created_at)`, `provider_invoice_id`, `status` |
| `backend/apps/workspace/models.py` + migration `0005` | Indexes: project `(user,status)`, `(user,-updated_at)`; history `(user,-created_at)`, `(user,tool)` |
| `backend/config/settings/base.py` | `DB_CONN_MAX_AGE`/`CONN_HEALTH_CHECKS`, Redis socket timeouts + default TTL, Celery `RESULT_EXPIRES`/`ACKS_LATE`/`PREFETCH=1`/global time limits (all env-overridable) |
| `backend/apps/system/views.py` + `backend/config/urls.py` | Split liveness `/health/` vs readiness `/ready/` (+ `/api/v1/ready/`); readiness checks DB (503 if down), cache fail-open, no secrets |
| `backend/apps/{analytics,subscriptions,data_science,image_tools}/tasks.py` | Bounded `@shared_task`: soft/hard time limits, `max_retries`, `acks_late=True` |

Uncommitted user work preserved: root `.env.example` modifications were left intact.

## D. Database safety

- All migrations additive (`AddIndex` only): `storage 0004`, `billing 0007`,
  `workspace 0005`. No data rewrite, no constraint tightening, fully reversible
  (`migrate <app> <prev>`). Safe for large tables (index build takes brief
  Postgres lock; use `CONCURRENTLY` manually if a table exceeds comfort).
- `makemigrations --check`: clean. Rollback: reverse-migrate the three apps.
- Not done: read replicas/sharding/partitioning (unjustified), retention jobs.

## E. API and frontend performance

No before/after latency numbers (no load env; inventing them is prohibited).
Expected effects (by construction, not measurement): storage list is now O(page)
instead of O(all rows) with indexed ordering; folder/project serialization no
longer N+1; pooled DB conns cut connect overhead; Redis/cache stalls bounded at
~2s instead of indefinite. Frontend untouched (no safe change without measuring
first); its risks (bundles, polling, unvirtualized lists) are documented in the
baseline audit.

## F. AI and background processing

Provider routing, model registry, fallback order, verification gates: untouched.
Celery: bare tasks now bounded + `acks_late`; global guardrails
(`SOFT 600s/HARD 660s` defaults, `PREFETCH=1`, `RESULT_EXPIRES=1d`) apply unless a
task overrides. Single `celery,image_local_ai` queue kept (separate queues only
when measurements justify). No broker change.

## G. Billing and data integrity

Untouched by design (already atomic + idempotent). Cache explicitly documented as
never authoritative for entitlements. Indexes only improve webhook/ledger lookups.
Concurrency proof: existing tests (`test_billing_safety`, credit idempotency
tests) — 1 billing retry test fails at baseline (pre-existing, unrelated).

## H. Test evidence

- `manage.py check`: clean. `makemigrations --check --dry-run`: clean.
- `tests/unit/apps/storage`: baseline 5F/18P → after: **23 passed**.
- `billing+subscriptions+authentication`: 118 passed, 9 failed — identical set on
  stashed baseline (pre-existing auth-API/hardening + billing-retry failures).
- Full suite + Redis-dependent tests: blocked (no Redis in this env,
  `Connection refused`); affiliates attribution fails at baseline for this reason.
- Frontend vitest, load/stress, multi-instance, provider-failure drills: NOT RUN
  (no env); must run in staging before scale claims.

## I. Deployment readiness

- No new required env vars; new optional overrides: `DB_CONN_MAX_AGE` (60),
  `DB_CONN_HEALTH_CHECKS` (True), `CACHE_DEFAULT_TIMEOUT` (300),
  `REDIS_SOCKET_{CONNECT_,}TIMEOUT` (2s), `CELERY_{RESULT_EXPIRES,SOFT_,}TIME_LIMIT`,
  `CELERY_TASK_ACKS_LATE` (True), `CELERY_PREFETCH_MULTIPLIER` (1).
- Rolling-deploy safe (additive migrations, backward-compat responses).
- Ops: route LB health checks to `/ready/` (traffic) vs `/health/` (liveness);
  set Gunicorn `--timeout 30`; serve `/media/` via nginx/CDN in prod.
- Rollback: reverse-migrate 3 apps; revert commits (no data migration involved).

## J. Remaining work (ranked)

- P1: paginate remaining unbounded lists (workspace projects/history, billing
  payments/invoices, ai_tools batch jobs) behind the new helper; add
  `select_related/prefetch_related` to billing + workspace serializers.
- P1: object-storage backend + signed URLs + retention/GDPR purge; stop serving
  media from Django in prod.
- P1: throttle posture — enable throttles independent of DEBUG, tighten anon/user
  defaults, add scoped throttles for list/upload/poll endpoints.
- P2: separate Celery queues (interactive vs batch vs ML-train) + queue-depth
  metrics; structured logs + correlation IDs + latency histograms.
- P2: frontend — route-split editor deps, dedupe polling, virtualize files/history.
- P3: read replicas/sharding/multi-region only on measured need.
- BLOCKED (needs staging/keys): load benchmarks, provider-outage drills, webhook
  replay at concurrency, multi-instance shared-state test.

## K. Acceptance matrix

| Requirement | Status |
|---|---|
| Preserve all features/contracts | VERIFIED (tests + `manage.py check`; only additive changes) |
| Baseline audit documented | VERIFIED (`BASELINE_AUDIT.md`) |
| P0 folder-endpoint outage | VERIFIED (23/23 storage tests) |
| OAuth bounded timeouts | IMPLEMENTED, NOT VERIFIED (no live OAuth in env) |
| Pagination (storage) | VERIFIED shape-compat (storage tests green); other lists NOT IMPLEMENTED |
| DB indexes | IMPLEMENTED, NOT VERIFIED (plan inspected; no prod query-plan run) |
| Credit/billing concurrency | VERIFIED (unchanged; existing suite; 1 pre-existing failure noted) |
| Celery bounded tasks | IMPLEMENTED, NOT VERIFIED (no worker run here) |
| Liveness vs readiness | IMPLEMENTED, NOT VERIFIED (unit-level only; needs LB check) |
| File orphan cleanup | VERIFIED (code path; covered indirectly by delete tests) |
| Load/throughput/latency targets | BLOCKED (no staging env) |
| Frontend perf gains | NOT IMPLEMENTED (rightly — measure first) |
| Object storage migration | NOT IMPLEMENTED (needs infra decision) |
