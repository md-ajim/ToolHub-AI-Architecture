# ToolHub-AI — PRODUCTION DISCOVERY REPORT

**Date:** 2026-09-28 · **Mode:** read-only audit (no code modified for this report)
**Repo:** `/run/media/md-ajim/Linux_Data/Repo/ToolHub-AI` · **Branch:** main · **HEAD:** `bec5706`
**Method:** 7 parallel subagent audits (editor, credits, API contracts, security,
public-routes/SEO, responsive/a11y, analytics-CI-deploy) + direct verification.
Every claim carries `file:line` evidence. Nothing below is estimated.

Related prior art (already in repo, not duplicated here):
`docs/WEBSITE_TOOL_INVENTORY.md` (58→60 tools), `docs/MODEL_CAPABILITY_MATRIX.md`.

---

## 1. REPOSITORY INVENTORY (verified)

### 1.1 Layout
- `frontend/` — Next.js 16.3 App Router (`frontend/package.json:23`), Tailwind v4
  (`globals.css` + `lib/design/theme.css` tokens, `th-*` brand system).
- `backend/` — Django 6.1, DRF, Celery + beat, Redis cache, Postgres (compose),
  Stripe billing. Tests: `backend/tests/unit/*` — **39 test files**, no
  integration/e2e dirs. Frontend: **13** `*.test.*` (vitest).
- `docker-compose.yml` (234 lines): db (postgres:15), redis:7, backend
  (migrate + `seed_plans` + `seed_ai_models` + gunicorn ×2), celery,
  celery-beat, frontend (`:32768→3000`), cloudflared (profile-gated).
  **No HEALTHCHECK anywhere** (Dockerfiles or compose).
- CI: **none** — no `.github/`, no Jenkins/GitLab/Circle configs.
- `backend/apps/`: 25 app dirs. Mounted API prefixes (`config/urls.py:22-44`):
  `pricing, auth, accounts, image, pdf, seo, developer, business, workspace,
  storage, admin, ai, studio, subscriptions, billing, ai-workspace` (+ health).
  **Never mounted (dead stub apps):** `api, system, api_keys, video_tools,
  audio_tools, blog, notifications, analytics, processing, admin_logs`.
  Legacy `apps/ai/*` (7 endpoints) has **no include** — dead code path.
- `console.*` in `frontend/src`: 8 hits, all `console.error` in catch blocks
  (workspace FavoriteButton, admin page, dashboard usage/billing/overview,
  pricing ×3). Zero `console.log`. Recommend central `lib/logger.ts`
  (currently 0 bytes).

### 1.2 Scale facts (counted, not estimated)
- Central tool registry: **60 tools**, all `status:"available"`, 15 mega-menu
  categories (largest: Product Photography 13).
- Tool pages: 56 dedicated + dynamic `[slug]`; editor sub-pages: **36**
  (32 + 4 built this session: ai-relight, background-generator,
  expand-canvas, generative-fill).
- Backend AI: **30** canonical operations (`ai_tools/registry.py:1284`),
  **39**-model capability matrix; Batch Studio: 7 ops, same enqueue path.
- AI Workspace seed: 62 models (14 mock gated by `AI_ALLOW_MOCK_MODELS`,
  default off); 10 real providers.
- Dashboard routes: overview + favorites, projects (+`[id]`), files, history,
  usage, billing, profile, settings, affiliate (new), + auth-gated `/ai/*`.

---

## 2. ARCHITECTURE MAP (single source of truth per concern)

### 2.1 Frontend
`app/` routes → `app/layout.tsx` (brand, metadataBase, title template) →
`components/marketing/*` (public) · `components/editor/*` (sole editor:
`EditorShell → EditorProvider → ToolRail/Canvas/Inspector`, one
`runOperation` path in `useEditorOperation.ts:122`, one `TOOL_REGISTRY`) →
`app/dashboard/*` + `features/dashboard/*` → API clients (`services/*.ts`,
`lib/api.ts` fetchApi with 401-refresh mutex) → state: React context
(Auth, AI-workspace, Editor) + local component state; **no global store**
except two tiny zustand slices (workspace/layerOrder, editor-tested).

### 2.2 Backend request lifecycle (AI image job)
`POST /api/v1/ai/operation/` → `services.py:enqueue` (quote → reserve →
Celery dispatch) → `tasks.py:process_ai_job` (claim → `_try_provider` w/
same-capability fallback → measure) → success finalize (`consumed=reserved`,
**no second debit**) / failure → refund (per-attempt idempotency keys,
state-machine guards under `select_for_update`) → sweeper (beat 300s, 2h
window) covers orphans. Stripe money→credits is a separate path
(`billing/webhooks.py` invoice-paid dedup).

### 2.3 Truth table (authoritative owner per concern)
| Concern | Owner | Consumers must not duplicate |
|---|---|---|
| Credit price/quote | `ai_tools/registry.py:quote_credits_for_model` (floor + `ceil(USD×R/0.0094)`) | frontend displays `cost_per_operation` only (verified: no formula in `frontend/src`) |
| Model eligibility | `eligibility.py` + quality gate (`live_status.py`, `verify_models`) | selectors render flags only |
| Entitlement/tier | `subscriptions/services.py EntitlementService` (QA choke: `is_qa()`) | UI gates are cosmetic |
| Provider health | adapter `is_configured()` + payment-state memory (`provider_registry.py`) | UI shows `available/unavailability_reason` |
| Affiliate terms | `settings AFFILIATE_*` → `/affiliates/program/` | `/partners` + dashboard read the endpoint |
| Tool catalog | `centralToolRegistry.ts` (frontend) / `OPERATION_REGISTRY` (backend) | pages resolve, never redefine |

---

## 3. WHAT IS SOLID (preserve — do not regress)

1. **Editor architecture intact.** Single shell/context/canvas/history/execution
   loop; 36 ToolTypes; no competing second editor (dormant unmounted
   `canvas/FabricCanvas.tsx` is dead weight, not a fork).
2. **Credit chain safe.** Reserve-on-enqueue, idempotency keys per attempt,
   ledger dedup, state-machine finalizers, sweeper, QA bypass centralized on
   `is_qa()`. Frontend never prices (display-only `cost_per_operation`).
3. **Zero hard-404 API mismatches.** Every frontend `fetchApi` resolves to a
   mounted route. Auth/refresh mutex correct; SSE streaming has its own
   refresh path (correct but divergent — see §5.4).
4. **Quality gating real.** `VERIFIED_PRODUCTION`-only selectors, mock gate
   (`AI_ALLOW_MOCK_MODELS`, default off) covers listing/routing/execution.
5. **Brand system exists.** `th-*` tokens (orange #f97316), light/dark,
   Poppins/Space Grotesk, `tokens.ts`. Problem is inconsistent *application*,
   not absence.
6. **SEO base real.** Title template, OG/Twitter defaults, canonicals on key
   pages, sitemap (139→141 routes incl. `/partners`), robots with sane
   disallows, `[slug]` exemplar metadata + SoftwareApplication/BreadcrumbList
   JSON-LD, Organization schema, pricing FAQPage schema, branded OG image.
7. **Affiliate pipeline complete (new).** Track → cookie → attribution (email +
   OAuth) → first-payment commission → holding → payout request → admin.
   15 backend tests green; build 141 pages green.
8. **Dashboard Phase 1 wired.** Settings (profile PATCH, prefs persist, real
   password-reset flow), favorites (GET/DELETE), usage storage (new scoped
   `GET /storage/usage/`), history (fake badge removed), projects→detail
   links. Billing page was already exemplary.

---

## 4. GAP REGISTER (ranked — this is the implementation backlog)

### P0 — Security (fix before any production traffic)
- **P0-1 Anonymous file dump:** `storage/views.py:9-13` `FileListView`
  (`AllowAny`, `File.objects.all()`, no user filter). *Note: new
  `StorageUsageView` added this session is correctly `IsAuthenticated` +
  user-scoped — same file still hosts the hole.*
- **P0-2 Anonymous arbitrary file delete:** `storage/views.py:20-29`
  (`AllowAny`, `File.objects.get(pk)` + delete, no ownership).
- **P0-3 Workspace comment IDOR:** `workspace/views.py:235-240,263-265`
  (`get_object_or_404(Project, pk=...)` without `user=`; siblings at :60,64
  do it right).
- **P0-4 PDF validation bypass:** `validate_pdf_upload()` exists
  (`pdf_tools/serializers.py:10-29`) but only 1 of 8 serializers calls it;
  all views `AllowAny` → decompression-bomb/polyglot risk.
- **P0-5 Throttles dead when `DEBUG=True`:** `base.py:241-244` empties
  `DEFAULT_THROTTLE_CLASSES`; `backend/.env` sets `DEBUG=True` while root
  `.env` says `False` (config source ambiguity — decide ONE).
- **P0-6 Secrets hygiene:** real keys live in untracked `.env` files (correctly
  git-ignored, but present on disk/backups); `SECRET_KEY` falls back to a
  **public default** (`base.py:29`) — app boots in prod with a known key.
- **P0-7 Path traversal via upload filename:** `pdf_tools/views.py:22-27`
  (`default_storage.save(f"temp/{file_obj.name}")`), media served
  unauthenticated when `SERVE_MEDIA` (defaults to DEBUG).

### P1 — Correctness / honesty / contracts
- **P1-1 Logout/reset never blacklist tokens** (`authentication/views.py:112-121`;
  `services.py:312-326`): refresh valid 24h post-logout; `AllowAny` on logout
  with a comment admitting it should be `IsAuthenticated`.
- **P1-2 No brute-force protection on auth** (no throttles/lockout on
  login/register/forgot/reset/OAuth; reset endpoint is a timing/email oracle
  + spam vector).
- **P1-3 OAuth trust gaps:** Google `id_token` verified via `tokeninfo`
  without `aud/iss/exp` checks (`services.py:121-143`); code exchange
  proceeds with empty client id; GitHub accepts raw tokens, `GET ?code=`
  (logs/history leak, no state/PKCE) (`views.py:208-250`).
- **P1-4 Reset tokens live 3 days** (Django default, no `PASSWORD_RESET_TIMEOUT`);
  old JWTs survive password reset.
- **P1-5 `plan_id` filter silently ignored:** `payment.service.ts:23-24`
  sends `?plan_id=`, backend `billing/views.py:110-114` never reads
  `query_params` (returns all prices).
- **P1-6 Affiliate POST payouts omits `created_at`** (GET includes it) —
  introduced with the new affiliate endpoints; frontend renders `—`.
  (Fix when touching affiliates.)
- **P1-7 Gateway error-shape drift:** `_gateway_error_response`
  (`ai_workspace/views.py:43-56`) returns `{success:false, error:{...}}`
  but `fetchApi` parses `message/errors` → users see generic text on
  402/403/429. Same drift in `business_tools/views.py:31`,
  `developer_tools/views.py:25,46`.
- **P1-8 `previewPreset` bypasses refresh logic** (`ai.service.ts:441-444`,
  manual `Authorization`, generic throw) — expired token mid-editor hard-fails.
- **P1-9 Hardcoded `/api/v1` bypasses base-URL resolution**
  (`aiWorkspace.service.ts:97,298`, `AuthContext.tsx:94`) — breaks
  absolute-URL deployments + skips refresh on logout.
- **P1-10 Dead `authApi` client** (`features/auth/services/authApi.ts`):
  raw fetch, no auth header, no retry, divergent unwrap, **zero call-sites** —
  migrate or delete per regression protocol (§7).
- **P1-11 Predictable project `share_token`** (`workspace/views.py:74-78`,
  timestamp+UUID fragment) + dead sharing surface (no public route).
- **P1-12 404-vs-403 user oracle** (`ai_tools/views.py` ×6 sites): scope
  lookups by `user=` instead of check-after-fetch.
- **P1-13 `ProjectMemberListView.post`** references unimported
  `ProjectPermission.VIEWER` (probable 500) + no role check
  (`workspace/views.py:96-107`).
- **P1-14 History has no status field** — table shows tool/file/date only
  (fake badge already removed this session); failed-vs-done runs are
  indistinguishable. Needs model field + writer updates (migration).
- **P1-15 Storage `FileListView` unscoped** (see P0-1); dashboard files page
  depends on it — scope + auth it or replace with user-scoped endpoint.

### P2 — Product completeness / UX honesty
- **P2-1 Homepage imbalance** (reported earlier): hero + 5/7 CTAs → `/ai`;
  no deep links to flagship tools; category tile copy omits AI editing
  services; pricing bullets model-only. (Homepage tools count fixed 8→12.)
- **P2-2 Thin content pages:** `/about` (no links/CTA), `/contact`
  (submit button, verify handler), `/blog` (3 hardcoded posts, self-loop
  "Read more"), `/guides` (4 unclickable cards, no detail routes),
  `/docs` (4×1–2 sentences), `/security`, `/status` (static badges),
  legal pages (short, contact-as-plain-text).
- **P2-3 Tool pages uneven:** most lack `relatedTools`; `image-editor`
  missing canonical; several How-To-only thin pages (qr/password/webp).
- **P2-4 Capability content removed this session**: homepage STT/TTS/
  embeddings/video cards + footer AI Video/Voice + Careers/Partners/
  Affiliate placeholders + social icons removed as fake. Per Rule 1 these
  stay out **unless** real targets ship (video/audio backends are stubs;
  Partners exists now → footer restored for Partners/Affiliate only).
- **P2-5 `allowedTools` prop is dead plumbing** (stored, never enforced);
  `FabricCanvas` dormant duplicate engine (wire or remove per protocol);
  `ExportFormat` defined twice; `ZoomToolbar` unmounted; three mask inputs
  (correctly funneled, but know it).
- **P2-6 Frontend cheapest-tie-break** (`ModelSelector.tsx:241`) nudges
  against backend never-cheapest-first (display-only, but inconsistent).
- **P2-7 Quota surprise:** frontend totals use static floor; backend charges
  `max(floor, MP-scaled)` — authoritative 402 protects revenue, but users
  can be surprised. Expose real quote pre-upload (backend already persists
  `quoted_*`).
- **P2-8 ComfyUI lock 1h + 5s requeue spin** (`tasks.py`); dual retry
  budgets stack; `billing_attempt` static on auto-retries; dead
  `record_successful_payment` with divergent renewal ref (delete/unify —
  webhook path is canonical); renewal fallback 500; `refund_minor_to_credits`
  100:1 hole (isolate); renewal fallback 500; QA-email auto-heal risk
  (reserve/block `QA_USER_EMAIL` registration in prod); sweep-vs-timeout
  window + beat-liveness monitoring missing; cancel fire-and-forget UX.

### P3 — Platform hardening (post-launch safe)
- No CI (no `.github/`), no Docker HEALTHCHECKs, no beat-liveness monitor.
- Analytics: stub tables only, no SDK, no event taxonomy (master command
  Phase 20 events unimplemented).
- `console.error` ×8 (catch blocks; route via `lib/logger.ts`, currently empty).
- next.config thin: no `images.remotePatterns` (Unsplash used unconfigured),
  no security/caching headers, no redirects.
- OG/Twitter images: root branded image added; per-page images absent.
- Schema gaps: no Article (blog), no Product/Offer (pricing), WebSite/
  SearchAction absent. No `{}` irrelevant schema injected — keep it that way.
- Reduced-motion: present and correct (`globals.css:407-418`,
  `theme.css:309-318`). A11y system strong (focus-visible, labels) with
  known gaps: `InspectorRow` renders `<span>` not `<label>` (9+ unlabeled
  range/select controls — highest-impact a11y fix), icon-button `title`-only
  names (ExportPresets, ShortcutsDialog, VersionHistory, AICommandBar
  submit), `ToolLayout` h1→h3 skip, raw range inputs lack focus rings,
  3 generic image alts.
- Responsive top risks: `dashboard/files` table (no scroll wrapper, long
  filenames untruncated), history toolbar squeeze at 320px, `lg`-breakpoint
  editor chrome crowding (~596px at 1024px), duplicate right-panel
  definitions (`CanvasChrome:825` vs `:2007` — confirm dead, delete one).

---

## 5. UNCOMMITTED WORK BASELINE (for regression protection)

Working tree is **clean** — all session work is committed
(`bec5706`, `5b518a3`, `97da186`, `4b4b13c`). No stashes. Inventory baseline
for §7 comparisons: 60 registry tools · 36 editor pages · 30 AI ops ·
39-model matrix · 7 batch ops · 18 backend API prefixes · 139–141 page
build green · backend 39 unit test files · frontend 13 test files.

---

## 6. RISKS & DECISIONS NEEDED

1. **Config source ambiguity** (P0-5): `backend/.env: DEBUG=True` wins over
   root `.env: DEBUG=False` via `load_dotenv`. Decide ONE source before prod.
2. **QA-user-email reservation** (credit §4.9): block registration of the
   QA email + unset it in prod env.
3. **Removed navigational placeholders** (§4 P2-4): keep out until real
   targets exist (video/audio backends, careers content, social profile
   URLs, refund policy). Social icons need owner URLs to restore.
4. **Analytics vendor**: implement self-hosted collector on existing stub
   tables, or adopt PostHog/Plausible? Needs owner call (privacy + cost).
5. **ComfyUI engine**: wire `FabricCanvas`, or delete per protocol.
6. **History status**: requires migration + writer changes — approve scope.
7. **Dead code deletions** (`authApi`, legacy `apps/ai/*`, stub apps):
   prove-unreachable first per protocol, owner approves each.

---

## 7. REGRESSION PROTOCOL (binding for all later phases)

Before/after every phase compare: routes, features, tools, models,
providers, API endpoints, dashboard routes. Unexpected deletion = BLOCKER.
Deletion requires: proven unreachable + no dynamic/lazy import + no route
reference + no test dependency + no registry reference; port feature logic
first; history preserved in Git; when uncertain, DO NOT DELETE.

*End of discovery report. Next per workflow: PRODUCTION_IMPLEMENTATION_PLAN.md,
then phased implementation with tests after every phase.*
