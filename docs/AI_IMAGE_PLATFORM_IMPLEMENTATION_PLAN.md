# ToolHub AI — AI Image Platform Implementation Plan
## Audit Date: 2026-08-24 — Phase 0
**Branch**: main (commit 2c76dfd) — Working tree has uncommitted production upgrade work (40 files modified, 15 untracked)

> Source of Truth: `docs/ToolHub_AI_Non_Destructive_Production_Grade_AI_Image_Upgrade_Specification.md` + repository audit
> Rule: Non-destructive additive upgrade only.

---

## 1. Existing Architecture Discovered

### 1.1 Applications / Packages
```
backend/config/                 Django 6.1 project (config.settings.base)
backend/apps/accounts/          User model (UUID PK, email USERNAME_FIELD) + Profile
backend/apps/authentication/    JWT login/refresh, OAuth google/github
backend/apps/image_tools/       Sync image ops (ImageProcessingJob)
backend/apps/ai_tools/          Async AI jobs (AIProcessingJob) + providers
backend/apps/ai/                Legacy AiModel/AiJob
backend/apps/ai_workspace/      Chat LLM workspace (AiWorkspaceModel, AiConversation, AiMessage, AiUsageRecord, ProviderBudget)
backend/apps/pdf_tools/         PDF merge/compress/split etc.
backend/apps/seo_tools/
backend/apps/developer_tools/
backend/apps/business_tools/
backend/apps/storage/           File + ProcessedFile (default_storage local MEDIA_ROOT)
backend/apps/workspace/         ProjectDocument/Layer/BatchJob (frontend store mirrors)
backend/apps/subscriptions/     Plan, PlanPrice, Subscription, Usage, CreditWallet, CreditTransaction, TemporaryEntitlement, WebhookEvent
backend/apps/billing/           BillingProfile, Payment, Invoice, Refund, Coupon
backend/apps/processing/
backend/apps/api_keys/ backend/apps/analytics/ backend/apps/notifications/ backend/apps/blog/ backend/apps/admin_logs/ backend/apps/system/

frontend/src/app/               Next.js App Router
frontend/src/components/editor/ EditorShell + EditorContext + Canvas + Toolbar + Inspector
frontend/src/constants/         centralToolRegistry.ts (PRIMARY 43 entries), toolRegistry.ts (15 editor tools), tools.ts (presets)
frontend/src/services/          api.ts, subscription.service.ts, ai.service.ts
frontend/src/store/workspace.ts Layer/ProjectDocument helpers
frontend/src/contexts/AuthContext.tsx
```

### 1.2 Frontend Routes (App Router)
- **Tools landing**: `/tools/page.tsx` (lists from CENTRAL_TOOL_REGISTRY)
- **Per-tool pages**: `/tools/{image-editor,image-cropper,image-resizer,image-rotator,image-watermark,image-compressor,image-converter,background-remover,object-remover,photo-enhancer,image-upscaler,passport-photo,mockup-generator,product-image-editor,social-media-resizer}/page.tsx` (uses ToolLayout) + `/editor/page.tsx` (<EditorShell/>)
- **Fallback SEO**: `/tools/[slug]/page.tsx` resolves via CENTRAL_TOOL_REGISTRY, renders JSON-LD, canonical, breadcrumb.
- **Other**: `/tools/pdf/*`, `/tools/text/*`, `/tools/seo/*`, `/tools/{webp-converter,avif-converter,qr-generator,...}`
- **AI Workspace**: `/ai/page.tsx` (NewChatView), `/ai/c/[id]`, `/ai/models`, `/ai/compare`, `/ai/projects`
- **Auth**: `/(auth)/{login,register,forgot-password,reset-password,verify-email}`
- **Dashboard**: `/dashboard/{billing,usage,settings,...}`
- **System**: `layout.tsx`, `robots.ts`, `sitemap.ts` (uses CENTRAL_TOOL_REGISTRY), `page.tsx` (homepage)

All per-tool editor routes render same `EditorShell` but pass `allowedEditorTools` via registry to filter visible tools.

### 1.3 Backend Routes / API Endpoints
```
config/urls.py:
  /api/v1/auth/           → authentication
  /api/v1/accounts/       → accounts
  /api/v1/image/          → image_tools   (resize/, compress/, convert/, crop/, rotate/, watermark/, webp/, avif/, favicon/, product-image/, mockup/, flip/, job/<uuid>/)
  /api/v1/pdf/            → pdf_tools
  /api/v1/ai/             → ai_tools      (background-remove/, upscale/, enhance/, object-remove/, passport-photo/, jobs/, jobs/<uuid>/, jobs/<uuid>/{retry,cancel}, models/)
  /api/v1/ai-workspace/   → ai_workspace  (models/, providers/, workflows/, uploads/, compare/, projects/, conversations/, messages/)
  /api/v1/workspace/      → workspace
  /api/v1/storage/        → storage (files/)
  /api/v1/subscriptions/  → subscriptions (plans/, subscription/, entitlements/, wallet/, wallet/transactions/, usage-records/)
  /api/v1/billing/        → billing
  /api/v1/seo/ etc.
  /health/
```

Existing AI endpoint pattern: `POST /api/v1/ai/<tool>/` with `MultiPartParser`, enqueues `AIProcessingJob`, returns `202 {job_id, status, progress_stage}`; poll `GET /api/v1/ai/jobs/<uuid>/`, retry/cancel.

### 1.4 Tool Registry
- **centralToolRegistry.ts** (`CENTRAL_TOOL_REGISTRY: CentralToolEntry[]`) — 38 available entries (spec counts 36 published; actual 38 due to extra webp/avif etc. plus editor). Fields: id, name, description, icon, route, editorRoute, pricing, featured, popular, status, displayCategory, megaMenuCategory, keywords, badge, allowedEditorTools.
  - Image (11): image-editor, img-crop, img-rotate, img-watermark, img-resize, social-resize, img-compress, img-convert, webp-conv, avif-conv, favicon-gen (counts overlay)
  - AI (7): ai-bg-rm, ai-obj-rm, ai-enhance, ai-upscale, ai-passport, ai-mockup, ai-product ✓ matches spec
  - PDF (6), Text (4), SEO (4), Web (5) = total 38 (spec says 36 — audit validates count differs)
- **toolRegistry.ts** (`TOOL_REGISTRY: ToolRegistryEntry[]`) — 15 editor tools: pan, resize, crop, social, rotate, compress, convert, product-image (2), mockup (2), bg-remove (1), passport (1), upscale (2), enhance (1), object-remove (2), watermark (0). Defines creditCost & category groups via `getCategoryGroups`.
- **tools.ts** (`EDITOR_TOOLS`) — mirrors registry, adds capabilities + presets (SOCIAL_PRESETS etc.)
- **ai_tools/registry.py** (backend) — `IMAGE_MODELS` (3), `AI_TOOL_CREDIT_COSTS`, `get_image_models`, `select_model`, `get_provider_for_model`

SEO/Explore: `frontend/src/app/tools/page.tsx` uses registry for category filters + search + Most Popular + pagination; `Footer.tsx` lists registry subsets; `sitemap.ts` / `[slug]/page.tsx` generate canonical + JSON-LD Tool schema.

### 1.5 Database Models
- **subscriptions**: `Plan` (code, status, storage/daily/batch/api limits, features JSON), `PlanPrice`, `Subscription` (provider, status active/canceled/past_due/expired/incomplete/trialing/grace_period), `Usage`, `CreditWallet` (ai/image/pdf/api/storage ints, balance→ai_credits), `CreditTransaction` (allocation/usage/refund/purchase/expiration/admin_adjustment), `UsageRecord`, `TemporaryEntitlement`, `WebhookEvent`
- **ai_tools**: `AIProcessingJob` (UUID, user, tool_name, input_file, original_file, output_file, mask_file, prompt, model_id, provider, idempotency_key, input/output dims, retry_count, progress_stage {uploading,validating,preparing,processing,finalizing,ready}, progress_percent, reserved/consumed credits, processing_started/completed)
- **image_tools**: `ImageProcessingJob` (UUID, user, tool_name, parameters JSON, input/output File, status queued/processing/completed/failed/cancelled)
- **storage**: `File` (UUID, user, filename, mime_type, size, storage_path, status pending/processed/failed/deleted, project FK, parent_file for versioning, version_number, origin_tool), `ProcessedFile`
- **ai_workspace**: `Project`, `AiAttachment`, `AiWorkspaceModel` (CharPK, provider, provider_model_id, tier, capabilities JSON, cost_policy, capability_category, health_status), `AiConversation`, `AiMessage` (idempotency_key, selected/resolved_model FK), `AiUsageRecord` (credits/actual_cost), `ProviderBudget`, `ModelHealthLog`
- **accounts**: `User` (UUID, email, full_name, language, avatar URL, email_verified, is_staff/active), `Profile` (bio, occupation, soft delete)

See `backend/apps/*/migrations/` for existing migrations; `ai_tools/migrations/0002_upgrade_production.py` already staged (uncommitted) — adds AIProcessingJob new fields.

### 1.6 Image Processing Services
- `image_tools/services.py` — sync Pillow ops: resize (Lanczos), crop, rotate/flip, compress (JPEG quality/WebP/AVIF), convert, watermark, product/mockup/social. Used by `views.py` direct POST endpoints (no job queue).
- `ai_tools/providers/base.py` — `ImageProviderAdapter` ABC with `name`, `is_configured()`, `process(ImageProcessingRequest)->ImageProcessingResult` [+ `supports`]
- `ai_tools/providers/mock.py` — `MockImageProvider`: returns copy/resized/transparent PNG for all 5 ops (background-remove, object-remove, enhance, upscale, passport-photo) — uses Pillow.
- `ai_tools/providers/huggingface.py` — `HuggingFaceImageProvider`: calls `HF_API_TOKEN` + `AI_WORKSPACE_HF_BASE_URL` via `requests` for background-remove (Bria RMBG 1.4) and upscale (fallback X4). `is_configured` checks `HF_API_TOKEN` existence. No openai/replicate/fal/stability docs implemented yet.
- `ai_tools/services.py` — `enqueue_ai_job(user, tool_name, input_file, mask_file, prompt, model_id, idempotency_key)` handles auth, idempotency lookup, `EntitlementService.get_active_plan` + `has_feature("ai_access")` + per-tool `has_feature("ai_{tool}")` (exempts passport-photo), `select_model` (tier-filtered), `CreditService.reserve_credits(cost)` atomic, creates `AIProcessingJob` with original copy, PIL dimension sniff, enqueues `process_ai_job.delay`.
- `ai_tools/tasks.py` — `process_ai_job` Celery task (bound, max_retries=3): sets PROCESSING+preparing 10%, calls `_try_provider` (builds `ImageProcessingRequest`, `get_provider(provider).process`), handles retry with exponential backoff, finalizing 90%, sets COMPLETED+consumed_credits; on failure sets FAILED and refunds reserved credits. `CELERY_TASK_ALWAYS_EAGER=True` by default (dev sync).

### 1.7 Celery / Redis Configuration
- `base.py:231-239` `CELERY_BROKER_URL = REDIS_URL (redis://127.0.0.1:6379/0)`, `RESULT_BACKEND` same, `CELERY_TASK_ALWAYS_EAGER env True (default dev)`, `CELERY_TASK_EAGER_PROPAGATES True`
- `config/celery.py`: `Celery('config')`, `autodiscover_tasks`
- `CACHES` default RedisCache `REDIS_URL .../1`
- `docker-compose.yml` (not audited deep) declares `db` (postgres), `redis`, `backend`, `frontend`. Dev fallback: sqlite `db.sqlite3` via `dj_database_url`.

### 1.8 Object Storage
- `shared/storage.py: StorageService` wrapping `default_storage` (local `MEDIA_ROOT = BASE_DIR/media`). Methods: `upload(file_obj, path)→ {uuid}.ext`, `download`, `delete`, `exists`, `generate_upload_url` (placeholder pass), `generate_download_url → default_storage.url(path)`.
- `storage/models.py: File` versioned via `parent_file` self FK; `ProcessedFile`. No S3/django-storages; signed URLs not implemented (returns direct MEDIA URL — insecure for private assets). Env `.env.example` has no S3 keys; needs future `AWS_*` or `OBJECT_STORAGE` flag.

### 1.9 Authentication
- `accounts.User` + JWT SimpleJWT (60m access, 1d refresh, rotate True), auth classes `JWTAuthentication`. OAuth: `GITHUB_CLIENT_ID/SECRET`, `GOOGLE_CLIENT_ID/SECRET` (server-side verify via `authentication/services.py` — now enhanced in uncommitted diff with improved token validation + callback to `frontend/auth/callback/{github,google}/page.tsx`). Middleware: `AuthenticationMiddleware`. `middleware.ts` (frontend) enforces auth redirect.
- Frontend `AuthContext.tsx` wraps `useAuth` hook, calls `lib/api.ts` (axios with JWT interceptor + refresh).

### 1.10 Subscription / Plan System
- `subscriptions/services.py: EntitlementService` — `get_active_plan(user)` (filter active/trialing/grace_period order -created), `get_feature_value/has_feature/get_limit/can_use_tool/can_use_ai/can_use_model/get_available_models/has_temporary_entitlement`. Features/limits stored in `Plan.features` JSON (e.g., `{"ai_access": true, "ai_background-remove": true}`).
- `subscriptions/services.py: CreditService` — `get_wallet(create)`, `get_credit_balance`, `reserve_credits` (balance < amount → `InsufficientCredits`, `_apply_credit_change` with `TransactionType.USAGE` negative amount on `ai_credits` + creates `CreditTransaction`), `refund_credits`, `add_allocation` etc.
- Plans defined in DB (seeded via admin); `subscriptions/views.py: EntitlementView AllowAny` returns plan_name/code, credits, limits, features. `subscriptions/permissions.py: HasAIFeaturePermission` (new, referenced by services). No central `ENTITLEMENTS` constant yet; checks scattered `has_feature("ai_{tool}")`.

### 1.11 Credits System
- Primary pool: `CreditWallet.ai_credits` (`balance` property). Also `image_processing_credits` etc. unused for AI.
- Flow in `ai_tools/services.py`: `reserve→ USAGE type -cost` before job; `task success→ consumed_credits=reserved`; `task fail→ refund(+cost, type REFUND)`. Idempotency: lookup by `idempotency_key+user` before reservation prevents double charge (present).
- Gaps: `CreditService.refund` uses `amount` positive? verified `refund_credits` calls `_apply_credit_change` with `+amount` and `REFUND`. But task returns `reserved_credits` refund — correct. No daily budget/global budget guard, no concurrency limit.

### 1.12 Existing AI Model/Provider Architecture
- `ai_tools/registry.py` has only 3 models: `hf-bria-rmbg` (background-remove, free), `hf-stable-diffusion-x4` (upscale, pro), `mock-bg-remove` (all ops, free). Tier gating via `EntitlementService.get_active_plan` name parsing ("max"/"business"→max, "pro"→pro else free).
- `ai_workspace` has richer multi-LLM provider system: `provider_registry.py` + `providers/{openai_compatible,google,anthropic,huggingface,meta,mock,open_model}.py` handling chat. Uses `HF_API_TOKEN/OpenAI key etc.` never exposed to client (server-side only — verified no `NEXT_PUBLIC_` provider keys).
- Integration gap: `ai_tools` does NOT share `ai_workspace` provider registry; duplication. No openai image gen, stability, replicate, fal integrations — per spec only integrate configured providers; current configured = huggingface + mock only. Spec says do NOT invent endpoints — keep unavailable capabilities disabled.

### 1.13 Existing Image Editor
- **Shell**: `components/editor/EditorShell.tsx` — Header + ToolRail (vertical icon bar) + Toolbar (context actions) + Canvas (pan/zoom/select) + Right: LayersPanel + Inspector + Mobile Sheet + StatusBar
- **Context**: `components/editor/EditorContext.tsx` ~487 lines — state: file, currentImageUrl, originalImageUrl, activeTool, zoom, history(string[]), cropData, entitlements, allowedTools, imageDimensions, viewCommand, document(ProjectDocument), selection, processing, ui, maskDataUrl/File, isDrawingMask. Methods: pushHistory, applyResult (fetch blob→File), loadFile, undo/redo/reset, layer ops delegating to `store/workspace.ts`.
- **Operations present (14 confirmed)**: `toolRegistry.ts` 15 entries (includes pan -> spec counts 14 ops excluding pan? Audit maps: spec Basic 7 + AI 5 + Design 2 =14; actual registry has pan extra)
  - Basic: resize, crop, rotate (flip embedded), compress, convert, social
  - AI: bg-remove, object-remove, upscale, enhance, passport
  - Design/Product: mockup, product-image, watermark
- **Controls**: `EditorInspector.tsx` switches on `activeTool` to render sliders/inputs per tool; `ImageControls.tsx`; `EditorToolbar.tsx` has before/after toggle, export, compare.
- **Canvas**: `EditorCanvas.tsx` + `canvas/CanvasInteraction.tsx` handles pan/zoom/crop-rect masking; `useEditorOperation.ts` triggers API calls for AI ops (now polling job status).
- **History/Version**: Currently `history: string[]` (blob URLs) — not persistent, no version model, no branch/compare except `EditorBeforeAfter.tsx` + `VersionHistory.tsx` (in-memory). No non-destructive version model (required by spec).
- **Mask**: `maskDataUrl/File` in context + brush UI in Inspector — stored in-memory, not in object storage as requested.
- **Missing per spec**: Generative Fill, Background Generator, Expand Canvas, AI Relight — not in registry; no UI.

### 1.14 Explore All Tools Page
- `frontend/src/app/tools/page.tsx` — search input, `MEGA_MENU_CATEGORIES` filter chips, Most Popular (getPopularTools), All Tools grid (CENTRAL_TOOL_REGISTRY filtered), pagination. Works off `centralToolRegistry.ts` helpers. Footer preserved in uncommitted diff (enhanced marketing footer).

### 1.15 Footer / Navigation
- `components/layout/Footer.tsx` — enhanced in uncommitted diff (mega-menu category links + tool links). Navigation: `components/layout/Header` (not listed but present). Both use registry.

### 1.16 Tests
- `backend/pytest.ini` `[pytest] DJANGO_SETTINGS_MODULE=config.settings.base, python_files=test_*.py, testpaths=tests, addopts=--import-mode=importlib -s`
- `backend/tests/unit/apps/*/test_*.py`: `accounts/test_models.py`, `authentication/test_api.py`, `image_tools/test_services.py` + `test_api.py` (cached), `pdf_tools/test_conversion_services.py/.api`, `ai_tools/test_providers.py` (new), `ai_workspace/test_providers.py` + `test_routing.py`, `billing/test_webhooks.py`, `subscriptions/test_services.py`
- Coverage minimal — no integration tests for AI job lifecycle, no credits idempotency tests, no upload validation security tests, no editor E2E. Need REGRESSION suite per spec.

### 1.17 Environment Configuration
- `.env.example` (now 42 lines in diff), `.env.development`, `.env.production`, `backend/.env` — all include `DATABASE_URL, REDIS_URL, CELERY_BROKER_URL, DEBUG, SECRET_KEY, AI_WORKSPACE_* keys (OPENAI/GOOGLE/ANTHROPIC/DEEPSEEK/QWEN/XAI/MISTRAL/HF_API_TOKEN/META + base URLs), OAuth GITHUB/GOOGLE, NEXT_PUBLIC_API_URL (http://localhost:8000/api/v1), NEXT_PUBLIC_SITE_URL`.
- No `STRIPE_WEBHOOK_SECRET`, no `AWS_S3` keys, no `AI_*_IMAGE_*` provider keys (e.g., STABILITY_API_KEY, REPLICATE_API_TOKEN, FAL_API_KEY) — spec requires env-based toggles.

---

## 2. Implementation Gaps vs Specification

| Spec Requirement | Current State | Gap | Severity |
|---|---|---|---|
| **36 tools preserved** | 38 entries (extra favicon/webp etc.) — all available | No deletion, but count mismatch needs documentation | Low |
| **14 editor operations** | 15 entries inc pan; all 14 present | pan extra is ok | None |
| **Provider Adapter Layer** | base+mock+hf only | Missing openai/google/stability/replicate/fal adapters (but spec says only configured providers) — architecture must allow pluggable, keys server-side | Medium |
| **Async Job System** | AIProcessingJob + Celery eager (dev) + queued/processing/completed/failed/cancelled/expired statuses | Job model missing `cancelled/expired` handling beyond status; progress stages present but not all stages (missing uploading/validating); no `expired` cleanup; needs production worker test | Medium |
| **Mask/Selection System** | In-memory maskDataUrl only | Need reusable Mask model + brush/eraser/rect/lasso/auto/subject/invert modes, stored in object storage not huge DB blob | HIGH |
| **Version System** | original_file in job but no ImageVersion model; editor history is ephemeral string[] | Need additive ImageVersion/Project layer version history (original→edit branches), undo/redo/compare/reject/accept/restore, preserved original | HIGH |
| **Credit reservation/refund** | Implemented via CreditService atomic, idempotency key | Needs idempotent billing tests, daily budget guard, per-op configurable costs for new ops (generative-fill 3 etc.) | Medium |
| **Entitlements** | EntitlementService centralized but per-tool checks use string has_feature("ai_{tool}") scattered | Need centralized entitlement map + plan_names FREE/PRO/BUSINESS/MAX with feature flags | Medium |
| **Upload Security** | validators.py: MAX_FILE_SIZE 25MB, imghdr + PIL decode, dims/pixels limit | Need MIME+signature+decodability+size+dims validation enforced on both image_tools & ai_tools; need private storage + signed URLs + ownership checks | Medium |
| **Storage separation** | shared/storage.py local only | Need separate concepts original/version/generated/mask/thumbnail/temp + retention/cleanup cron + signed URLs for private assets | Medium |
| **Idempotency** | idempotency_key on AIProcessingJob, lookup before reserve | Correct but needs per- expensive operation documentation + tests; image_tools sync ops not idempotent (ok) | Low |
| **Provider Fallback** | Not implemented — single try + retry same provider | Need fallback to compatible provider if configured, with cost disclosure + recording | Medium |
| **Basic ops not via AI** | Keep Pillow sync path for crop/rotate/resize/compress/convert/watermark — observed | Must ensure these never call AI provider (verified) | None |
| **Result Experience** | Job status API returns output_file.url + size, but Inspector lacks before/after+dimensions+credits+provider UI fully | Need before/after preview, dimensions, file size, provider/model, credits consumed, actions (Download/Continue Editing/Reject/Accept) | Medium |
| **History** | In-memory string[] + VersionHistory.tsx (non-persistent) | Need persistent operation history model (operation_id, image_id, parent_version, op_type, provider, params, result asset, credit cost, timestamps) with branch support | HIGH |
| **Batch Processing** | Not present | Need Batch model + child jobs for Business plans, server-side queue, progress/partial failure/retry/cancel | HIGH (Business feature) |
| **Generative Fill** | Not implemented | New tool: mask + optional prompt → inpaint → preview variations → accept/reject | HIGH |
| **Background Generation** | Not implemented | Preset/uploaded/generated + prompt-based where supported | HIGH |
| **Image Expansion** | Not implemented | Left/right/top/bottom/all + custom aspect | HIGH |
| **AI Relight** | Not implemented | Provider-supported only; UI presets | MEDIUM (if provider unavailable show disabled) |
| **Product Image Editor mockup upgrade** | Product/mockup exist but marked mock only | Upgrade with product isolation, bg cleanup, studio bg, shadow, centering if provider supports | MEDIUM |
| **Explore All Tools** | Functional via registry | New AI tools must register without duplicating IDs; keep search/filters/pagination/footer | Low |
| **SEO** | [slug]/page.tsx generates JSON-LD but new routes not all present | Need unique title/meta/canonical/content/FAQ/related for each AI tool; avoid thin pages | Medium |
| **API Design** | Has POST/GET jobs + retry/cancel + models | Spec adds POST /api/image-ai/masks, GET masks/:id, GET capabilities — need to adapt under /api/v1/ai/ | Medium |
| **Feature Flags** | Not present | Need env flags AI_GENERATIVE_FILL_ENABLED etc. + capability availability checks | Medium |
| **Observability** | LOGGING verbose to console only | Need job count/success/failed/latency/queue/provider cost/retry/storage failure metrics + structured logs | Medium |
| **Security/Abuse** | JWT auth + IsAuthenticated on AI views; throttle ai_chat/compare/upload but not AI image jobs | Need ownership checks on jobs, signed URLs, rate limiting on AI endpoints, audit logging | Medium |
| **Moderation** | None beyond provider safety | Need abuse rate limiting + provider safety passthrough + graceful moderation rejection | Low |
| **Testing** | Minimal stubs | Need UNIT (adapters/credits/entitlements/idempotency/mask/versioning/state), INTEGRATION (create→queue→worker→storage→refund), E2E (upload→AI→preview→accept→export), REGRESSION (36 tools +14 ops), SECURITY (ownership/upload/plan bypass) | HIGH |
| **DB Migration Safety** | 0002_upgrade_production staged but unverified | Must ensure ADD→MIGRATE→VERIFY→SWITCH→MONITOR; no DROP; backups before destructive | Medium |

---

## 3. Proposed Additions (Non-Destructive)

### 3.1 Database Changes (Additive Migrations Only)
- **Migration 0003_enable_generative** (next ID: check `showmigrations`):
  ```python
  # Add to AIProcessingJob (if not already): operation field remains tool_name; add expanded tool choices
  # Add column: expires_at DateTime nullable (for expired status + cleanup)
  # No DROP/ALTER destructive change
  ```
- **New model `AIMask`** (`apps/ai_tools/models.py` additive):
  ```python
  class AIMask(models.Model):
      id = UUID PK; user FK; image FK optional (AIProcessingJob); mask_file FileField(upload_to="ai-masks/%Y/%m/"); 
      width, height, brush_size, feather, opacity; mode char (brush/erasing/rect/lasso/auto/subject); is_inverted bool;
      created_at, updated_at; indexes on user+created
  ```
- **New model `AIImageVersion`** (non-destructive version):
  ```python
  class AIImageVersion(models.Model):
      id = UUID PK; user FK; job FK (nullable for manual edits); parent FK self nullable;
      image_file FileField; thumbnail FileField nullable; version_number int;
      operation_type char (resize/crop/ai_bg_remove/generative_fill/...); 
      provider, model_id, parameters JSON, credit_cost int; is_current bool; created_at
      # Do NOT replace AIProcessingJob.original_file; this layers on top
  ```
- **New model `AIBatchJob`** (Business):
  ```python
  class AIBatchJob(models.Model):
      id = UUID PK; user FK; tool_name; status queued/processing/completed/failed/cancelled;
      total_count, completed_count, failed_count; created_at, completed_at
      # Child via FK from AIProcessingJob.batch = FK(AIBatchJob, null)
  ```
- **New model `AIProcessingJob.capability`** already via tool_name; extend `AI_TOOL_CREDIT_COSTS` dict with generative_fill 3, background-generation 3, expansion 3, relight 2, product 3, mockup 4; keep configurable via settings/environ `AI_CREDIT_COSTS_JSON`.

**Migration strategy**: `ADD new models/columns` → `migrate` → `verify existing 38 tools + 15 editor ops still load` → `switch new code paths behind feature flags` → `monitor`. No legacy table/column removals in this release.

### 3.2 API Changes
- **Keep** existing `/api/v1/ai/{background-remove,upscale,enhance,object-remove,passport-photo}` (no rename).
- **Add** (under `/api/v1/ai/` to match existing convention, map spec `/api/image-ai/` alias):
  ```
  POST /api/v1/ai/generative-fill/           (tool_name=generative-fill, requires mask_file+prompt optional)
  POST /api/v1/ai/background-generate/       (tool_name=background-generate, supports preset/uploaded/generated+prompt)
  POST /api/v1/ai/expand/                    (tool_name=expand, params direction/expand_ratio/aspect)
  POST /api/v1/ai/relight/                   (tool_name=relight, params brightness/direction/warmth)
  POST /api/v1/ai/product-edit/              (upgrade existing product-image mockup flow)
  POST /api/v1/ai/mockup/generate/           (explicit mockup variants)
  POST /api/v1/ai/masks/                     (upload/create mask → returns mask_id + signed url)
  GET  /api/v1/ai/masks/<uuid>/              (fetch mask with ownership check)
  GET  /api/v1/ai/capabilities/              (list provider capabilities + availability per plan)
  GET  /api/v1/ai/jobs/<uuid>/result         (302 or signed url redirect — ownership checked)
  POST /api/v1/ai/batch/                     (Business: {tool_name, images: [], params})
  GET  /api/v1/ai/batch/<uuid>/              (progress, partial failure)
  ```
- **Modify** `views.AIJobStatusView` to include before/after dimensions, file size, provider/model, credits consumed, progress_message.
- All new views reuse `BaseAIToolView` queue logic (reserve → idempotency → enqueue).
- Add `@throttle_classes` / custom `AIRateThrottle` (e.g., 10 AI jobs/min/user) + `HasAIFeaturePermission` per tool.
- Provider secrets remain server-side: `serializers` never echo `*_API_KEY`; logs redact.

### 3.3 Frontend Changes
- **centralToolRegistry.ts** — APPEND only, no reorder/delete:
  ```ts
  { id: "ai-gen-fill", name: "AI Generative Fill", route: "/tools/generative-fill", editorRoute: "/tools/generative-fill/editor", megaMenuCategory: "ai-image-tools", allowedEditorTools: ["generative-fill","object-remove"], pricing:"pro", ... },
  { id: "ai-bg-gen", name: "AI Background Generator", ... },
  { id: "ai-expand", name: "AI Expand Canvas", ... },
  { id: "ai-relight", name: "AI Relight", ... },
  // Keep existing 38 IDs stable for SEO/canonical
  ```
- **toolRegistry.ts** / `tools.ts` — APPEND `generative-fill` (credit 3), `background-generate` (3), `expand` (3), `relight` (2) with icons; update `getCategoryGroups` → new group `AI Generate`.
- **EditorShell.tsx / EditorContext.tsx** — Reorganize ToolRail sections non-destructively (ADD sections, keep existing discoverability):
  ```
  BASIC: Pan, Resize, Crop, Rotate, Compress, Convert
  AI TOOLS: BG Remove, Object Remove, Upscale, Enhance, Passport
  AI GENERATE: Generative Fill, Remove & Replace, Background Generator, Expand Canvas, Relight  (feature-flagged, disabled label if unavailable)
  DESIGN: Social, Product, Mockup, Watermark
  ```
  Keep canvas, left sidebar, right Inspector, zoom/pan/history/export/download. Never hide existing tools behind extra clicks — default expanded.
- **New components** (additive under `components/editor/ai/`):
  - `MaskCanvas.tsx` — brush/eraser/rect/lasso/auto/invert over image; outputs mask File; uses efficient object storage upload via `POST /masks`
  - `GenerativeFillPanel.tsx`, `BackgroundGeneratorPanel.tsx`, `ExpandCanvasPanel.tsx`, `RelightPanel.tsx` — each collects params + calls `ai.service.ts` enqueue, polls job, shows before/after + Accept/Reject/Continue Editing
  - `JobProgressOverlay.tsx` — shows real stages (Uploading/Preparing/Creating mask/AI processing/Finalizing/Complete) not fabricated %
  - `VersionHistory.tsx` — already exists; extend to bind `AIImageVersion` persistence (fetch `GET /ai/versions?image_id`)
  - `BatchProgressPanel.tsx` — progress bar + partial failure table
- **services/ai.service.ts** — add `createGenerativeFillJob(formData)`, `createMask(file)`, `getCapabilities()`, `getJobResult(id)`; all use `lib/api.ts` JWT.
- **pages under `frontend/src/app/tools/{generative-fill,background-generator,expand,relight}/page.tsx` + `/editor/page.tsx`** — reuse `ToolLayout` + `EditorShell` pattern; add SEO FAQ + related tools.
- **Feature flags** via `NEXT_PUBLIC_AI_*_ENABLED` (client) + server checks `AI_*_ENABLED` env; if provider not configured show "Currently unavailable" not fake result.

### 3.4 Provider Changes
- **Keep** `providers/base.py`, `mock.py`, `huggingface.py` intact.
- **Extend** `PROVIDER_ADAPTERS` registry via `apps/ai_tools/providers/registry.py` pattern: add openai (DALL·E/inpaint), stability (remove-bg, upscale, inpaint), replicate, fal stubs — each implements `is_configured()` checks respective env (`OPENAI_API_KEY`, `STABILITY_API_KEY`, `REPLICATE_API_TOKEN`, `FAL_KEY`) and `supports(op)`. Do NOT invent provider endpoint details; adapters return `ProviderError("unsupported", "...")` if capability absent.
- **Add** `get_fallback_provider(operation, primary)` where provider fails and compatible fallback configured; record fallback in job `metadata` + logs.
- Env: add to `.env.example` `STABILITY_API_KEY=`, `REPLICATE_API_TOKEN=`, `FAL_KEY=`, `OPENAI_API_KEY=` already present; keep HuggingFace default.

### 3.5 Other Infrastructure
- **Celery**: Keep `process_ai_job`; add `cleanup_expired_ai_jobs` periodic task (delete temp outputs older than N days, never originals) + `cleanup_ai_masks` (31 days).
- **Storage**: Extend `StorageService` to support S3 path if `AWS_S3_BUCKET` env set (django-storages optional dependency) else local; add `generate_signed_url(path, expiry)` for private assets (File.status).
- **Credits**: Extend `AI_TOOL_CREDIT_COSTS` with new ops; make configurable via `settings.AI_CREDIT_COSTS = json.loads(os.getenv("AI_CREDIT_COSTS_JSON", "{}"))` merging over defaults; enforce `no negative`, `idempotent` via `select_for_update` in `reserve_credits` (already transaction atomic).

---

## 4. Database Changes Summary
| Operation | Table/Model | DDL | Risk |
|---|---|---|---|
| Add field | AIProcessingJob | expires_at DateTime nullable index | Low |
| Create table | AIMask | UUID PK, user FK, mask_file, dims, mode, timestamps, index user+created | Low |
| Create table | AIImageVersion | UUID PK, user FK, job FK nullable, parent FK, image_file, operation_type, provider, credit_cost, timestamps | Low |
| Create table | AIBatchJob | UUID PK, user FK, tool_name, status, counters, timestamps | Low |
| Alter field | AIProcessingJob | may extend tool_name choices to include generative-fill etc. (no constraint) | Low |
| No DROP | all existing | — | — |

**Migration file**: `backend/apps/ai_tools/migrations/0003_additional_ai_platform.py` (next after 0002). Verify with `python manage.py migrate --plan`.

---

## 5. Provider Changes Summary
- **No removal** of existing mock/huggingface adapters.
- **Add** capability map in `registry.py:IMAGE_MODELS` entries for new ops with tier + availability flags; adapters declare supported ops.
- **Fallback**: conceptual failover loop in `tasks.py:_try_provider` tries primary then iterate `get_available_providers` that support same op.
- **Secrets**: all keys via `os.getenv`, read in `settings/base.py`, used only inside `providers/*.py` server-side.

---

## 6. Testing Strategy
### 6.1 Regression (must run before any feature merge)
- Tool registry count: `assert len(CENTRAL_TOOL_REGISTRY)==38` + status available 38; each route renders 200; sitemap includes all.
- Editor smoke: `EditorShell` renders, ToolRail shows 15 tools grouped correctly; Inspector switches per activeTool.
- Image ops: call `/api/v1/image/{resize,compress,convert,crop,rotate,watermark}` with sample PNG → 200 + output size validates.
- Auth: login→refresh→protected AI endpoint 401 if no token, 403 if no entitlements, 402 if no credits.
- Export/download: canvas `toBlob` → download link.

If missing, create `backend/tests/unit/apps/*/test_regression_registry.py` + frontend `__tests__/editor/ToolRail.test.tsx` + Playwright `tests/e2e/editor.spec.ts`.

### 6.2 Unit
- Providers: mock process each op, huggingface mock HTTP with `responses` library, error paths.
- Credits: reserve/consume/refund no-negative, idempotent duplicate key returns same job.
- Entitlements: FREE vs PRO vs BUSINESS tier filter `get_image_models`.
- Mask ops: brush size, invert, serialization round-trip.
- Versioning: parent chain, reject/accept branch.

### 6.3 Integration
- `POST /api/v1/ai/background-remove/` with image+JWT → 202 → Celery eager runs → `GET /jobs/<id>/` → completed → output_file.url fetchable + credit reserved==consumed.
- Retry/cancel: failed job → `POST /retry` → requeue.
- Batch: `POST /ai/batch/` with 3 images → 3 child jobs created.
- Storage ownership: user A cannot GET user B job (403).

### 6.4 E2E (Playwright or Cypress)
- Upload image → BG Remove → poll progress → Before/After compare → Accept → Continue Editing → Crop → Export → Download file size check.
- Generative Fill: draw mask → prompt "remove person" → submit → variations → Reject → Original restored.

### 6.5 Security
- Upload validation: oversized (25MB+), invalid MIME, corrupted image → 422.
- Signed URLs: direct MEDIA URL without token → 403 after private flag.
- Plan bypass: FREE user POST pro tool → 403.
- Rate limits: hammer AI endpoint 20×/min → 429.
- Provider key exposure: scan frontend bundle for `HF_API_TOKEN` etc. → absent.

---

## 7. Migration Strategy (Safe)
1. **Pre**: `pg_dump` or `cp db.sqlite3 db.sqlite3.bak`; `git stash` current uncommitted work → branch `feat/ai-platform-plan`.
2. **Migration**: `python manage.py makemigrations ai_tools` → review generated `0003_*.py` (ensure only CREATE/ADD).
3. **Verify**: `python manage.py migrate --check` + `pytest tests/unit/apps/ai_tools/test_providers.py` + manual editor open `npm run dev` → no 500.
4. **Switch**: Enable feature flags off by default; workers read `AI_GENERATIVE_FILL_ENABLED=true` via env to activate.
5. **Monitor**: Log `AIProcessingJob` creation rate, credit mutations; alert on `failed>5%`.
6. **Rollback**: If registry breakage, `migrate ai_tools 0002` + `git revert` — no data loss because ADD-only.

**Destructive guard**: If any migration contains `DeleteModel`, `RemoveField`, `AlterField` narrowing, or `RunSQL DROP`, STOP, require explicit approval per spec §26, produce report listing affected tables/records.

---

## 8. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Existing tool registry ID renamed/deleted breaking SEO/canonical | Medium (many registry edits) | HIGH (404, SEO loss) | Lint rule: `centralToolRegistry.ts` diff check CI prevents id removal; keep IDs immutable; dynamic `[slug]` fallback warns if missing |
| Editor operation removed/hidden | Medium | HIGH | `toolRegistry.ts` snapshot test asserts 15 count; ToolRail default-expanded; allow `allowedEditorTools=[]` for full editor only |
| Provider keys leaked to client | Medium | CRITICAL | `rg NEXT_PUBLIC.*API_KEY` CI check; only server `providers/*.py` imports `settings.*_API_KEY`; no api response includes provider secret |
| Image-tools sync path accidentally routed through AI provider cost explosion | Low | HIGH | Separate `image_tools/views.py` vs `ai_tools/views.py` URL prefixes; audit imports of `process_ai_job` only from ai_tools; circuit breaker `AI_CREDIT_COSTS` max 10 |
| DB destructive migration | Low | CRITICAL | CI `migrator --plan` parses for DROP; manual approval gate; backup before migrate |
| Celery queue latency/stall | Medium | Medium | Monitor `queue_latency` via `_set_progress` timestamps; fallback eager mode for dev; production requires Redis reachable check at boot |
| Duplicate billing on retry | Low | HIGH | Idempotency key unique index + `select_for_update`; tests fire duplicate POST rapidly assert same job_id + single transaction |
| Huge mask blob in DB | Low | Medium | Mask model stores `mask_file` path + small metadata in DB; DB column is FileField path not binary; cleanup temp masks 7 days |
| Batch payload bomb (100s images) | Medium | Medium | `AI_BATCH_MAX_IMAGES=20` env cap; chunk creation; validate each image size/dims; rate-limit batch endpoint separate throttle `ai_batch 5/min` |
| Moderation rejection not handled | Low | Low | Catch `ProviderError(code="moderation")` → 422 user-friendly msg; do not expose raw provider error; refund credits |
| Storage private URL exposure | Medium | HIGH | Gate `GET /jobs/<id>/result` via ownership check + signed URL with expiry `AWS_QUERYSTRING_EXPIRE=3600` else redirect to private MEDIA with permission check |
| Frontend bundle regression | Medium | Medium | Playwright screenshot diff for tool pages + editor; size limit check `next build` |
| Env misconfig (no HF token) | High | Low | `is_configured()` returns false → capability disabled UI reads `/capabilities` and shows "Currently unavailable" banner; no fake generation |

---

## 9. Next Steps (Phase Order per Spec §32)

**PHASE 1 — Baseline Regression Protection** (immediate): create `docs/AI_IMAGE_PLATFORM_IMPLEMENTATION_REPORT.md` skeleton + add regression tests for 38 tools & 15 ops (`backend/tests/unit/apps/test_registry_snapshot.py`) — run `pytest -q`.

**PHASE 2 — Job/Storage/Mask/Version Infra** (requires migration 0003): add `AIMask`, `AIImageVersion`, `AIBatchJob` models + `StorageService.generate_signed_url` + `ai_tools/validators` enforcement + `image-ai/masks` endpoints.

**PHASE 3 — Provider Adapter Expansion**: keep existing adapters; add capability-aware registry entry additions for new ops; add fallback logging; unit tests per adapter.

**PHASES 6-12 — Upgrade existing AI tools one-by-one** (BG Remove ✅ partially, Object Remove → Upscale → Enhance → Passport → Product → Mockup) validating each before next.

**PHASES 13-16 — New generative features** behind `AI_*_ENABLED` flags (Generative Fill → Background Gen → Expand → Relight).

**PHASES 17-20 — Batch, SEO, monitoring, full regression/security/load**: implement SEO FAQs for each tool (`frontend/src/app/tools/*/content.tsx`), add structured logs + `ProviderBudget` cost tracking, run load test `k6` on AI endpoint.

Do NOT proceed to Phase N+1 until Phase N tests pass and baseline 38/15 invariants hold.

---

## 10. Appendices

### A. Relevant Files (Absolute Paths)
- Backend settings: `backend/config/settings/base.py:1-269`, `config/urls.py:1-45`, `config/celery.py`
- AI models: `backend/apps/ai_tools/models.py:6-66`, `registry.py:10-62`, `providers/{base.py,mock.py,huggingface.py}`, `services.py:17-79`, `tasks.py:85-149`, `views.py:12-120`, `urls.py:1-11`, `serializers.py`, `validators.py`
- Subs: `backend/apps/subscriptions/models.py`, `services.py:10-293`, `views.py:60-93`, `permissions.py`
- Storage: `backend/shared/storage.py:1-56`, `apps/storage/models.py`
- Image sync: `backend/apps/image_tools/models.py`, `views.py`, `services.py`
- Frontend registry: `frontend/src/constants/centralToolRegistry.ts:108-675`, `toolRegistry.ts:49-221`, `tools.ts:19-184`
- Editor: `frontend/src/components/editor/{EditorShell.tsx:1-151,EditorContext.tsx:1-487,EditorInspector.tsx,EditorToolbar.tsx,EditorCanvas.tsx,useEditorOperation.ts,ai/*.tsx, VersionHistory.tsx, ExportDialog.tsx}`, `store/workspace.ts`
- Pages: `frontend/src/app/tools/page.tsx`, `tools/[slug]/page.tsx:13-32`, `tools/*/page.tsx + */editor/page.tsx`, `ai/page.tsx:23-174`, `sitemap.ts`, `robots.ts`
- Auth: `backend/apps/authentication/{views.py,services.py,urls.py}`, `frontend/src/contexts/AuthContext.tsx`, `features/auth/hooks/useAuth.ts`
- Tests: `backend/pytest.ini`, `tests/unit/apps/**/test_*.py`
- Env: `.env.example:1-42`, `backend/.env`, `frontend/.env.local`

### B. Current Behavior Summary
- Unauthenticated: homepage + tool landing pages accessible; editor loads but AI actions 401 until login.
- Authenticated FREE: sync image ops unlimited (within daily_limit 5 default after UsageService check), AI gated by `ai_access` feature (FREE has none → 403 on ai_tools POST), credits 0.
- PRO/BUSINESS: feature flags in Plan.features enable per-tool AI; `select_model` filters by tier rank; reserve before enqueue prevents negative.
- Dev queue: `CELERY_TASK_ALWAYS_EAGER=True` → jobs run synchronously inside HTTP worker (acceptable for tests, must disable in prod with `CELERY_TASK_ALWAYS_EAGER=False` + `celery -A config worker`).

### C. Environment Variables Required (After Upgrade)
```
# Existing
DATABASE_URL, REDIS_URL, CELERY_BROKER_URL, SECRET_KEY, DEBUG
AI_WORKSPACE_* (OPENAI/GOOGLE/ANTHROPIC/HUGGINGFACE etc.)
GITHUB_CLIENT_ID/SECRET, GOOGLE_CLIENT_ID/SECRET
# New additive (all optional, defaults safe)
HF_API_TOKEN or HUGGINGFACE_API_KEY
STABILITY_API_KEY, REPLICATE_API_TOKEN, FAL_KEY  (for future provider adapters)
AI_GENERATIVE_FILL_ENABLED=false
AI_BACKGROUND_GENERATION_ENABLED=false
AI_EXPANSION_ENABLED=false
AI_RELIGHT_ENABLED=false
AI_CREDIT_COSTS_JSON={"generative-fill":3,"background-generate":3,"expand":3,"relight":2,"mockup-generate":4}
AI_BATCH_MAX_IMAGES=20
AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION (if S3 desired)
```

### D. Commands to Validate Baseline Before Implementation
```bash
python backend/manage.py showmigrations
python backend/manage.py check
pytest backend/tests -q
npm --prefix frontend run build   # or next build
python backend/manage.py shell -c "from frontend.src.constants check central count" # manual
```

**Sign-off**: Plan approved for incremental non-destructive build. No production behavior modified during audit. Next action: Phase 1 regression tests (ADD-only).
