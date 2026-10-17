# E-Commerce AI Image Platform — Roadmap Implementation

This document records the implementation of the e-commerce AI product-content
roadmap (`ecommerce_ai_image_platform_roadmap.md`) on top of the existing
production AI Image Editor. The existing workspace, tool rail, inspector,
canvas, history, upload and export flows were **preserved and extended** — no
working tools or routes were removed.

## 1. Architecture preserved

- Existing image editor workspace (`frontend/src/components/editor/*`) and the
  `useEditorOperation` pipeline (upload → validate → job → preview → apply →
  history → export) were kept intact.
- The existing `apps.ai_tools` job pipeline, provider registry, credits and
  entitlement checks were reused for all new operations.
- `apps.image_tools` core editing tools (crop, resize, compress, convert,
  rotate, watermark, etc.) are unchanged.

## 2. AI provider abstraction

`apps.ai_tools/providers/`:

- `base.py` — `ImageProviderAdapter` ABC + `ImageProcessingRequest` /
  `ImageProcessingResult` + `ProviderError`.
- `local_provider.py` — **`LocalImageProvider`** (always configured, no
  credentials). Implements **every** e-commerce operation as a real Pillow
  transform (`providers/pil_ops.py`), so the full pipeline works end-to-end
  without external AI. Results are tagged `metadata.method = "deterministic"`.
- `mock.py`, `huggingface.py`, `openai_provider.py`, `stability.py` — existing
  adapters. `select_model()` in `registry.py` ranks providers
  `huggingface > openai > stability > local > mock`, so a **configured real AI
  provider is always preferred** over the deterministic fallback.
- `providers/__init__.py` — `PROVIDER_ADAPTERS` registry + `get_fallback_provider()`
  for safe provider fallback on failure.

> Honesty rule: deterministic transforms are real image processing, not faked
> AI. Generative operations (background-generate, product-staging, fashion-model,
> ghost-mannequin, etc.) reach **production quality only when a real provider is
> configured**. Without one, the local provider returns a clearly-labeled
> deterministic approximation and never pretends an AI call succeeded.

## 3. Operations registry

`apps.ai_tools/registry.py` — `OPERATION_REGISTRY` is the single source of truth
for every operation: display name, phase/category, minimum plan tier, whether it
is generative, and its entitlement feature key (`ai_<op>`). `list_operations()`
and `get_operation()` back the capability endpoint, tool rail, and gating.

New operations added: `shadow`, `background-generate` (AI Background),
`marketplace-resize`, `product-staging`, `product-photography`, `expand`,
`relight`, `recolor`, `retouch`, `fashion-model`, `ghost-mannequin`, `flat-lay`,
`fashion-retouch`, `infographic`, `size-chart`, `carousel`, `social-creative`,
`ad-creative`. Plus existing `background-remove`, `upscale`, `enhance`,
`object-remove`, `generative-fill`, `passport-photo`.

## 4. Generic operation endpoint

`POST /api/v1/ai/operation/` accepts any registered `tool_name` + a JSON
`parameters` blob and routes through the same `enqueue_ai_job` pipeline
(auth → entitlement `ai_<op>` → credit reserve → idempotency → background
Celery job → versioning). Existing dedicated views (`/background-remove/`, …)
remain.

## 5. New app: `apps.ecommerce_studio`

Centralizes marketplace presets, saved workflows, brand kit, AI Product Studio
sessions, and exports. Reuses `ai_tools.AIProcessingJob` via FK.

### Models (`apps/ecommerce_studio/models.py`)
- `MarketplacePreset` — canvas dimensions, aspect ratio, format, quality, fit,
  padding, background rule, export-naming template; system presets
  (`is_system`) seeded from config, users may create custom ones.
- `SavedWorkflow` — user-defined ordered `steps` (operation + params), reusable.
- `BrandKit` — logo, brand colors, fonts, background/product-image style,
  export presets, saved templates; scoped to the user.
- `StudioSession` / `StudioSessionStep` — the AI Product Studio run: ordered
  steps each linked to a background job, with current image, status, error.
- `ExportRecord` — produced single files or ZIPs with owner + audit fields.

### Centralized preset config (`apps/ecommerce_studio/presets.py`)
Amazon, Shopify, Instagram, Facebook, TikTok, Custom — each with multiple
variants. `render_export_name()` builds filenames like
`product-name-main.jpg`. Seeded via `manage.py seed_marketplace_presets`.

### Services (`apps/ecommerce_studio/services.py`)
- `apply_marketplace_preset()` — deterministic compose onto preset canvas.
- `export_image()` / `build_zip_from_jobs()` — single + batch ZIP export.
- `create_studio_session()` / `continue_studio_session()` / `skip_studio_step()`
  / `retry_studio_step()` / `cancel_studio_session()` / `resume_studio_session()`
  — full studio orchestration with input chaining (step N input = step N-1
  output), preview, retry, skip, cancel, save/resume, error recovery.
- `run_saved_workflow()` — replays a saved workflow as a studio session.

## 6. API endpoints (new, under `/api/v1/studio/`)

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `presets/` | list (system + user) / create custom preset |
| POST | `presets/<code>/preview/` | apply preset to an image (raw image response) |
| GET/POST | `workflows/` | list / create saved workflow |
| GET/PUT/DELETE | `workflows/<id>/` | saved-workflow detail |
| POST | `workflows/<id>/run/` | run workflow on an image → studio session |
| GET/POST | `brand-kits/` | list / create brand kit (Business) |
| GET/PUT/DELETE | `brand-kits/<id>/` | brand-kit detail |
| GET/POST | `sessions/` | list / create studio session |
| GET | `sessions/<id>/` | session detail (with steps) |
| POST | `sessions/create/` | start a session (source image + preset/workflow/steps) |
| POST | `sessions/<id>/<action>/` | `continue` / `skip` / `retry` / `cancel` / `resume` |
| POST | `sessions/<id>/export/` | export current studio image |
| POST | `export/` | single export (image or completed job) |
| POST | `export/batch/` | ZIP of completed job outputs |
| GET | `exports/` | export history |

Plus existing `apps.ai_tools` endpoints: `/ai/operation/`, `/ai/jobs/`,
`/ai/batch/`, `/ai/masks/`, `/ai/capabilities/`, `/ai/versions/`.

## 7. Job architecture

`AIProcessingJob` states: `queued → processing → completed | failed | cancelled`
(+ `expired`). `process_ai_job` (Celery, `CELERY_TASK_ALWAYS_EAGER` in dev)
handles progress stages, provider fallback, retry with backoff (max 3), credit
refund on failure/cancel, non-destructive `AIImageVersion` creation, and result
cleanup via `expires_at`. Idempotency key prevents duplicate submissions.

## 8. Subscription / entitlement

`EntitlementService` is unchanged. `seed_plans` now grants every
`ai_<operation>` feature to **Pro** and **Business**, `brand_kit` /
`saved_presets` / `team_features` to **Business**, and a minimal
`ai_background_remove` + `ai_marketplace_resize` to **Free**. The local
provider is always available; real generative quality is gated behind plan +
configured provider.

## 9. Security

Every new endpoint is `IsAuthenticated`, ownership-checked (`user=request.user`),
and routes through the existing credit/entitlement layer. File size limits
(25 MB), safe filenames, and no provider keys in responses. Presets/brand kit
assets are scoped to the owning user.

## 10. Environment variables (new/changed)

| Var | Default | Meaning |
|-----|---------|---------|
| `AI_GENERATIVE_FILL_ENABLED` | `True` | capability flag |
| `AI_BACKGROUND_GENERATION_ENABLED` | `True` | capability flag |
| `AI_EXPANSION_ENABLED` | `True` | capability flag |
| `AI_RELIGHT_ENABLED` | `True` | capability flag |
| `AI_BATCH_ENABLED` | `True` | batch processing on/off |
| `AI_BATCH_MAX_IMAGES` | `20` | batch size cap |
| `AI_IMAGE_MAX_FILE_SIZE_MB` | `25` | upload cap |
| `AI_CREDIT_COSTS_JSON` | `{}` | per-op credit override |
| `AI_JOB_EXPIRES_DAYS` | `7` | result cleanup |
| `HUGGINGFACE_API_KEY` / `OPENAI_API_KEY` / `STABILITY_API_KEY` | — | real provider credentials (optional; enables production-quality AI) |

## 11. Migrations

`apps/ecommerce_studio/migrations/0001_initial.py` (MarketplacePreset,
SavedWorkflow, BrandKit, StudioSession, StudioSessionStep, ExportRecord).
Seeded via `python manage.py seed_marketplace_presets`.

## 12. Tests

`tests/unit/apps/ecommerce_studio/`:
- `test_providers_local.py` — every operation through `LocalImageProvider`.
- `test_studio.py` — auth, gating, unknown-op rejection, job lifecycle,
  idempotency, parameters, batch child jobs, credit 402, ownership 403/404,
  preset list/create/preview, saved-workflow create+run→studio→completion,
  brand kit gating, studio session pipeline to completion, session export,
  single + batch ZIP export.

All backend tests for `ai_tools`, `subscriptions`, and `ecommerce_studio` pass
(54 tests). Frontend `tsc --noEmit` passes with 0 errors; new service layer in
`src/services/ai.service.ts` (`StudioService`) and generic
`AiService.runOperation` wire the editor to the new endpoints.

## 13. Known limitations / blockers

- ~~**Frontend UI for saved-workflows, brand-kit, and studio-session management**
  has service-layer + type-level wiring but no dedicated management pages yet~~
  **Resolved (UI pass):** saved-workflow listing + run is now embedded in the
  editor via the **AI Studio tool** (`AIProductStudio.tsx`, tool-rail entry
  `ai-product-studio` under PRODUCT & E-COMMERCE). Brand-kit/session REST
  management remains API-first; the studio-session lifecycle itself is fully
  usable from the AI Studio + saved workflows UI.
- **Production-quality generative output** (fashion-model, ghost-mannequin,
  product-staging, background-generation, etc.) requires a configured real AI
  provider (`HUGGINGFACE_API_KEY` / `OPENAI_API_KEY` / `STABILITY_API_KEY`).
  Without it, the deterministic local provider is used and results are labeled
  accordingly. No AI result is ever faked.

## 14. Frontend integration pass (additive)

- `TOOL_REGISTRY` now registers every roadmap operation: `shadow`, `recolor`,
  `marketplace-resize`, `product-staging`, `product-photography`,
  `fashion-model`, `ghost-mannequin`, `flat-lay`, `fashion-retouch`,
  `infographic`, `size-chart`, `carousel`, `social-creative`, `ad-creative`
  and workflow entry `ai-product-studio`. New PRODUCT & E-COMMERCE rail group;
  existing groups/tools untouched.
- `EditorPanelsEcommerce.tsx` — all new inspector panels wired to
  `/api/v1/ai/operation/` with parameters matching `pil_ops`; loaded via
  `next/dynamic` only when the tool is selected (separate ~29 KB chunk; main
  editor bundle unchanged).
- Batch Editor page `/tools/batch-editor` (registered in centralToolRegistry):
  multi-upload → shared preset (incl. marketplace-resize params) → server-side
  batch queue (`AIBatchJob`) with per-item progress, cancel, retry, before/after
  preview and ZIP export via `/studio/export/batch/`.
- `POST /ai/batch/` now accepts an optional JSON `parameters` blob (model field
  already existed); unknown operations are rejected with 422.
