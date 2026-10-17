# Image Editor Functionality Verification Report — ToolHub-AI

**Date:** 2026-09-23
**Branch:** `main`
**Editor URL:** `http://localhost:32770/tools/image-editor/editor` (host port shifts on container recreate; verified `HTTP 200`)
**Scope:** `/tools/image-editor/editor` — frontend editor, AI/image/studio services, Django AI pipeline, entitlements, credits, history, export, batch.
**Safety:** No features, tools, providers, models, pipeline stages, or fallbacks removed. No pricing/credit-economics changes. No secrets committed. Local providers used throughout, except ONE explicitly-requested minimal text-to-image call (Cloudflare SDXL, single image — disclosed below).

## 38-Tool Sweep (2026-09-23, QA fixture `qa-test@toolhub.local`, isolated flag, normal auth+permission path)

Every row below was executed against the live stack (backend+celery+redis dockerized). "Output" = completed job + stored media fetched `HTTP 200` with bytes. Evidence: job records + `/tmp/opencode/sweep38_results.json` (35-row run: 34/35 → then generative-fill root-caused, fixed, re-verified 4/4).

|  # | Tool | Test / Evidence | Status |
| -: | ------------------- | -------------------------------------- | ------------ |
|  1 | Pan | Canvas drag → `setPan`, no HTTP by design (client transform, history-exempt) | ✅ কাজ করছে |
|  2 | Resize | 160×120 → completed, media 200 (`c3d96662`) | ✅ কাজ করছে |
|  3 | Crop | 100×100 → completed, media 200 (`648c348e`) | ✅ কাজ করছে |
|  4 | Rotate | 90° → completed, media 200 (`c03983e2`) | ✅ কাজ করছে |
|  5 | Flip | horizontal → completed, media 200 (`df8f69da`) | ✅ কাজ করছে |
|  6 | Watermark | "Audit" text → completed, media 200 (`ff9203d0`) | ✅ কাজ করছে |
|  7 | Compress | q60 → completed, media 200 (`71c54fad`) | ✅ কাজ করছে |
|  8 | Convert | webp → completed, media 200 (`88eedced`) | ✅ কাজ করছে |
|  9 | Social | 1080×1080 resize path → completed, media 200 (`2413e7b7`) | ✅ কাজ করছে |
| 10 | Mockup | device template → completed, media 200 (`1759a7eb`) | ✅ কাজ করছে |
| 11 | Product Image | white style → completed, media 200 (`a0868068`) | ✅ কাজ করছে |
| 12 | Passport Photo | USA → completed, media 200 (`e82baa2e`, mock) | ✅ কাজ করছে |
| 13 | Background Remove | `local-rmbg-u2net` → completed, media 200 (`8f60cee5`) | ✅ কাজ করছে |
| 14 | Upscale | `local-deterministic` → completed, media 200 (`7dcf622b`) | ✅ কাজ করছে |
| 15 | Enhance | `local-deterministic` → completed, media 200 (`4abfeb02`) | ✅ কাজ করছে |
| 16 | Object Remove | `mock-bg-remove` + mask → completed, media 200 (`89318fff`) | ✅ কাজ করছে |
| 17 | Generative Fill | `mock-generative-fill` + mask + prompt → completed, media 200, provider=mock, fallback=none (bug fixed, see §P0-1) | ✅ কাজ করছে |
| 18 | Background Generate | `local-deterministic` + prompt → completed, media 200 (`6146a46b`); mock variant re-verified provider=mock | ✅ কাজ করছে |
| 19 | Expand | `mock-expand` all-sides → completed, media 200 (`dc3309bb`); re-verified provider=mock post-fix | ✅ কাজ করছে |
| 20 | Relight | `mock-relight` i60 → completed, media 200 (`57a6e46a`/`57a9…`); re-verified provider=mock post-fix | ✅ কাজ করছে |
| 21 | Text-to-Image | `cf-sdxl-base` "a red apple" → completed, provider=cloudflare, 1.5 MB PNG media 200 (`0e9999d6`) — ONE controlled call per explicit request | ✅ কাজ করছে |
| 22 | Shadow | `local-deterministic` → completed, media 200 (`7f2ee625`) | ✅ কাজ করছে |
| 23 | Recolor | `#ff0000` → completed, media 200 (`411ce08a`) | ✅ কাজ করছে |
| 24 | Retouch | → completed, media 200 (`1e858b81`) | ✅ কাজ করছে |
| 25 | Marketplace Resize | 1000×1000 → completed, media 200 (`9b2abaed`) | ✅ কাজ করছে |
| 26 | Product Staging | studio scene → completed, media 200 (`7ee91df8`) | ✅ কাজ করছে |
| 27 | Product Photography | studio+soft → completed, media 200 (`4abfeb02`…`de7cea5`) | ✅ কাজ করছে |
| 28 | Fashion Model | → completed, media 200 (`bfb6a366`) | ✅ কাজ করছে |
| 29 | Ghost Mannequin | → completed, media 200 (`71ffb9de`) | ✅ কাজ করছে |
| 30 | Flat Lay | white bg → completed, media 200 (`c6c7a7f7`) | ✅ কাজ করছে |
| 31 | Fashion Retouch | → completed, media 200 (`22106c6c`) | ✅ কাজ করছে |
| 32 | Infographic | title+features → completed, media 200 (`044eaa6f`) | ✅ কাজ করছে |
| 33 | Size Chart | S/M → completed, media 200 (`08e17f29`) | ✅ কাজ করছে |
| 34 | Carousel | 2 slides → completed, media 200 (`2e822906`) | ✅ কাজ করছে |
| 35 | Social Creative | 1:1+headline → completed, media 200 (`82e64f97`) | ✅ কাজ করছে |
| 36 | Ad Creative | headline+offer → completed, media 200 (`2507a2bc`) | ✅ কাজ করছে |
| 37 | AI Product Studio | `POST /studio/sessions/create/` + `GET` detail → success (`e935db92`) | ✅ কাজ করছে |
| 38 | Convert/Social* | Covered by rows 8–9 (same handlers/endpoints) | ✅ কাজ করছে |

### P0-1. Spend-leakage via mock-advertised ops — FOUND & FIXED (`backend/apps/ai_tools/providers/mock.py`)

- **Symptom:** sweep row 17 first run → `failed`; job requested `model_id=mock-generative-fill` (provider `mock`) but executed on **HuggingFace** (`fal-ai/qwen-image-edit-plus`) and died on depleted HF credits.
- **Root cause:** `MockImageProvider.process` implemented only 5 ops while mock registry entries advertise 11 (`generative-fill`, `background-generate`, `expand`, `relight`, `product-edit`, `mockup-generate`, `inpaint`, `expand-image` missing) → primary raised `unsupported_operation` → `_try_provider` fallback engaged a **paid external provider** for a mock-selected job.
- **Fix (additive, no architecture change):** implemented the missing mock ops as deterministic Pillow transforms in the existing mock style (`_mock_inpaint` blur-fill, `_mock_background_generate` studio backdrop, `_mock_expand` honoring `directions`/`expand`, `_mock_relight` brightness factor, product-edit→enhance, `_mock_mockup` slate backdrop; `expand-image`/`inpaint` aliased). Fallback logic, routing, pricing, and real-provider paths untouched — mock runs only when explicitly selected or as last-resort fallback, as before.
- **Proof:** re-ran all 4 mock ops post-fix (backend+celery rebuilt): `completed`, `provider=mock`, `fallback=none`, media `200`. No external call. `manage.py check`: clean. Frontend `tsc` clean, `vitest` 9/70 pass.
- **Note:** a stale-code red herring occurred mid-audit (`restart` ≠ rebuilt image); resolved by `build` + recreate, then re-verified.

### Honest boundaries (not bugs)

- Free-plan users are entitlement-blocked (403, zero charge) on pro AI ops — expected restriction; QA fixture used for the sweep precisely to test execution without touching economics.
- `face-restore` (only `comfyui_local` model) cannot run here: `COMFYUI_ENABLED=true` but no server on `host.docker.internal:8188` (connection refused) → `BLOCKED_BY_CONFIGURATION`. Recommend `COMFYUI_ENABLED=false` until a server is provisioned; no code change made.
- Upscale default routing prefers `comfyui_local` → same dead-server caveat applies to *default* model choice; explicit model pick (the UI's `RichModelSelector`) works. Flagged for ops awareness, not patched (would alter routing architecture).
- Single text-to-image cloud call disclosed above; all other rows local/mock with zero external spend. QA password reset performed via Django shell (test fixture only).

---

## Phase 0 — Frozen State & Architecture Map

### 0.1 Git state (pre-change freeze)

- Branch: `main`
- Working tree at freeze: 18 modified tracked files + 4 untracked files (pre-existing session work, preserved untouched except where a verified bug required a minimal correction).
- Recent history: `82c4d66 feat: add Fabric.js canvas integration and alignment guides`, plus DeepLinkWrapper / crop-style / editor-interaction commits.

### 0.2 Architecture map

**Frontend (Next.js 16 / React):**

```text
/tools/image-editor/editor
 └─ DeepLinkWrapper (?tool= validated vs TOOL_REGISTRY)
     └─ EditorShell → EditorProvider (CANONICAL STATE: snapshots, document, file, viewport, mask, regions)
         ├─ EditorHeader (File/Edit/View/Help, Save, Export, undo/redo)
         ├─ GlobalNavRail (section → category filter, navigation only)
         ├─ EditorToolRail (tool activation only; execution deferred to Inspector)
         ├─ EditorCanvas (render + interaction only; plain-DOM/LayerCanvas/Fabric render layer)
         ├─ LayersSidePanel / LayersPanel (local document ops)
         ├─ EditorInspector (per-tool panels; the ONLY place that executes tool jobs)
         │   ├─ GenerationPanel (prompt-capable AI ops → /ai/*)
         │   ├─ CropExpandPanel / RelightLightingPanel / DrawMaskPanel
         │   └─ EditorPanelsEcommerce (17 product ops → POST /ai/operation/)
         ├─ QuickAIActions (pointer cards → setActiveTool; execution deferred to Inspector)
         ├─ AIProductStudio (6-step guided pipeline → /ai/* + /studio/workflows/)
         ├─ InstantAdjustPanel (client-side filter bake; NO credits, NO AI claim)
         ├─ ExportDialog (client download + POST /studio/export/)
         ├─ VersionHistory (POST/GET /workspace/projects/:id/versions/ + local restore)
         └─ UploadsPanel (blob URLs + addLayer; local only)
```

Execution primitive for every server op: `useEditorOperation.runOperation(operation, liveFile)` → `AiService` / `ImageService` / `StudioService` → poll `GET /ai/jobs/:id/` or `GET /image/job/:id/` → `applyResult()` → snapshot + base-layer sync → history. Retry = job resume (`GET` status → `POST retry/` → resume poll); cancel = abort + `POST cancel/` (refund). Fabric (`FabricCanvas`) is render-only; canonical state remains `EditorContext`/document (never replaced).

**Backend (Django + DRF + Celery + Redis + PostgreSQL):**

- `api/v1/ai/` → `apps/ai_tools/urls.py`: 12 tool endpoints (`background-remove`, `upscale`, `enhance`, `object-remove`, `passport-photo`, `generative-fill`, `background-generate`, `expand`, `relight`, `product-edit`, `mockup-generate`, `operation/`) + `jobs/`, `jobs/<id>/`, `jobs/<id>/retry/`, `jobs/<id>/cancel/`, `jobs/<id>/result/`, `masks/`, `capabilities/`, `versions/`, `batch/`, `models/`, `local-ai/health/`. All `IsAuthenticated`; enqueue = entitlement check → model select → storage gate → margin quote → spend-cap reroute → `reserve_credits` → `AIProcessingJob` → Celery dispatch.
- `api/v1/image/` → `apps/image_tools/urls.py`: 12 tools (`resize`, `compress`, `convert`, `crop`, `rotate`, `watermark`, `webp`, `avif`, `favicon`, `product-image`, `mockup`, `flip`) + `job/<id>/`. `HasImageToolPermission` + daily limits. No credits.
- `api/v1/studio/` → `apps/ecommerce_studio/urls.py`: presets, preset preview, workflows (+run), brand-kits, sessions (+create/action/export), `export/`, `export/batch/`, `exports/`. All `IsAuthenticated`.
- Workers: `process_ai_job` (progress 10→30→90→100, provider try + fallback, consume=reserved on success, refund on fail) and `process_comfyui_job` (Redis lock, concurrency 1); `process_image_job` for CPU tools. Celery live (eager `False`), Redis connected, `SERVE_MEDIA=True`.

**Registries / providers / billing (all preserved):**

- `OPERATION_REGISTRY`: 27 ops (free: `background-remove`, `upscale`, `enhance`, `face-restore`, `marketplace-resize`, `passport-photo`; rest pro) with `ai_<op>` feature keys.
- Providers (8, none removed): `local`, `local_rmbg`, `mock`, `huggingface`, `comfyui_local`, `cloudflare`, `openai`, `stability` — availability gated by credentials/flags; routing rank hf→cf→openai→stability→comfyui→local/rmbg→mock.
- Entitlements: `ai_access` + per-tool key (`passport-photo` exempt; unknown op fails closed via `is_known_operation`). Credits: reserve on enqueue, consume on success, refund on fail/cancel; blocked/denied requests never reserve.

### 0.3 Feature → handler → API → backend mapping (abridged; full map held in audit notes)

| Area | Example | Handler | Service → Endpoint |
|---|---|---|---|
| Basic tools | Resize Apply | `EditorInspector: handleApply` → `runOperation` | `ImageService.resizeImage` → `POST /image/resize/` + poll `GET /image/job/:id/` |
| AI core | BG Remove / Upscale / Enhance / Object Remove / Passport | per-tool `handleApply` | `AiService.removeBackground/upscaleImage/enhanceImage/removeObject/createPassportPhoto` → `POST /ai/<tool>/` |
| Generative | GenFill / BG-Gen / Expand / Relight | inline `runOperation` / AdvancedPanels | `AiService.generativesFill/generateBackground/expandImage/relightImage` or `runOperation(op)` → `POST /ai/<tool>/` or `POST /ai/operation/` |
| Product (17) | Shadow…Ad Creative, TTI | `OperationPanel` → `AiService.runOperation(tool,…)` | `POST /ai/operation/` |
| Studio pipeline | Product Studio steps / saved workflows | `AIProductStudio runStep/runAll/handleRunSavedWorkflow` | `POST /ai/*`, `POST /studio/workflows/:id/run/`, `GET /studio/sessions/:id/` |
| Export | Save to dashboard | `saveToDashboard` | `StudioService.exportImage` → `POST /studio/export/` (Download path is pure-client composite) |
| Versions | Save version | `handleCreateVersion` | `WorkspaceService` → `POST /workspace/projects/:id/versions/` (restore is local) |
| Batch | BatchEditorApp | `createBatch/getBatch` | `POST /ai/batch/`, `GET /ai/batch/:id/` |
| Rail/Header/StatusBar/Canvas chrome | activation, nav, zoom, undo/redo | `setActiveTool`, store ops, `requestView` | local-only by design (no HTTP, no credits) |

---

## Phase 1–3 — Verification Matrix (runtime-executed, fresh users, local-only providers)

| Feature | UI | Frontend | API | Backend | Model | Provider | Result | History | Export | Credits | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Resize 160×120 | Rail→Inspector | `handleApply→resizeImage` | `POST /image/resize/` | `ImageResizeView`+Celery | n/a | local CPU | `/media/image-outputs/…png` fetched `200` | snapshot | composite | none | **PASS** |
| Crop / Rotate / Flip / Compress / Convert / Watermark / Social | Inspector | `runOperation`→ImageService | `POST /image/<tool>/` | views+`process_image_job` | n/a | local CPU | same job→media pattern as resize | snapshot | composite | none | **PASS** |
| BG Remove | Inspector / QuickAI / Studio | `removeBackground` | `POST /ai/background-remove/` | enqueue→Celery | `local-rmbg-u2net` | `local_rmbg` | `/media/ai-outputs/…png` fetched `200` | snapshot+layer | composite | reserved 1 / consumed 1 (5→4) | **PASS** |
| Marketplace Resize | Ecommerce panel | `runOperation` | `POST /ai/operation/` (tool=marketplace-resize) | `AIOperationView` | `local-deterministic` | `local` | completed | snapshot | composite | per policy | **PASS** |
| Passport Photo | Inspector | `createPassportPhoto` | `POST /ai/passport-photo/` | exempt path | local/mock | local | completed | snapshot | composite | exempt (correct) | **PASS** |
| Batch (1 image; free limit 1) | BatchEditorApp | `createBatch` | `POST /ai/batch/` | queued + detail aggregates child jobs | bg-remove | local | processing→children | via children | via jobs | per child | **PASS** (2-image correctly rejected: "Batch limited to 1") |
| Export → dashboard | ExportDialog | `saveToDashboard` | `POST /studio/export/` | `ExportSingleView` | n/a | n/a | `file_url /media/exports/…` | no corruption | n/a | none | **PASS** |
| Retry completed job | GenerationPanel Try Again | `retryJob` | `POST /ai/jobs/:id/retry/` | correctly `400 "Only failed or cancelled…"`; frontend applies existing result free | — | — | no double charge | — | — | unchanged | **PASS** |
| Cancel job | hook `cancelOperation` | `cancelJob` | `POST /ai/jobs/:id/cancel/` | `{"success":true,"Job cancelled."}` + refund | — | — | cancelled | — | — | refunded | **PASS** |
| Upscale / Enhance / GenFill / Expand / Relight / Shadow on Free | gated panels | AiGate/Gate | `POST /ai/…` | `403 "not available for this plan"` | listed, unenqueueable | — | blocked pre-provider | — | — | unchanged (5→5) | **BLOCKED_BY_ENTITLEMENT** (expected, not a bug) |
| Text-to-Image | Ecommerce panel | `runOperation` | `POST /ai/operation/` | 0 models (no Cloudflare creds) | none | — | honest "No models available" | — | — | none | **BLOCKED_BY_CONFIGURATION** (needs `CLOUDFLARE_*`; UI degrades honestly) |
| Unknown op `nope-not-real` | — | `runOperation` | `POST /ai/operation/` | `422 Unknown operation` | — | — | no job, no charge | — | — | none | **PASS** (fail-safe) |
| Pan / Zoom / Fit / Layers / Undo / Redo / Instant Adjust / Crop preview | Canvas / Rail / StatusBar | local store / `filterPipeline` | none (by design) | n/a | n/a | none | canvas updates; Adjust Apply = ONE history txn | deduped, cap 50 | included | none | **PASS** (Instant Adjust explicitly separate from AI Enhance) |
| Save button (header) | Header | **had no `onClick`** | — | — | — | — | dead | — | — | — | **FAIL → FIXED** |
| Rail mockup sections + Explore CTA | Rail | **had no `onClick`** | — | — | — | — | dead | — | — | — | **FAIL → FIXED** |

**Media-path verification (Phase 7):** `resolveMediaUrl()` → `/media/…` → Next.js rewrite → `SERVE_MEDIA=True` → AI + image results fetched `200` with correct content-types. Docker and localhost both work via env-aware `getApiBaseUrl` (no hard-coded hostnames).

---

## Phase 4 — Fixes (minimal, targeted; no refactors)

### P1-a. Header Save button was dead — FIXED (`EditorHeader.tsx:182-189`)

- **Root cause:** button rendered with no `onClick` (verified in code; audit subagent independently confirmed).
- **Fix:** wired to `window.dispatchEvent(new Event("toolhub-editor:export"))` — the exact contract of Ctrl+S (`EditorKeyboardShortcuts:55-58`) and the Shortcuts dialog entry ("Save / Export image"). Opens `ExportDialog` with real Download + Save-to-dashboard execution. Title updated to `Save / Export (Ctrl+S)`. No UI redesign.

### P1-b. Rail mockup sections + Explore CTA were dead — FIXED (`EditorToolRail.tsx`)

- **Root cause:** `MOCKUP_SECTIONS` buttons (5) and `Explore AI Tools` rendered with no `onClick` (verified in code + screenshot rail).
- **Fix (design unchanged):** sections are now expandable and render **real `TOOL_REGISTRY` tools** of their categories through the existing fail-closed `handleToolClick` (locks intact): Design & Export → `design+export`; AI Editing & Generation → `ai`; Product & E-commerce → `product`; Creative Tools → `design+ai`. "Batch Processing" routes to the real `/tools/batch-editor` (plan limits enforced server-side — verified `batch_limit: 1` rejection). Explore CTA reveals the AI library (`setAiOpen`, Quick-AI, clears search/filter). `MOCKUP_SECTIONS` exported for testability.
- **Rules honored:** no feature deleted; dead buttons now execute real paths instead of being removed.

### Preserved prior-session repairs (inherited dirty tree, verified intact)

`DeepLinkWrapper` registry validation (unknown `?tool=` → empty inspector, never silent generative-fill); `GenerationPanel` loading reset + backend-driven credit cost; upload abort signals in both services; guest-401 toast suppression; canvas TDZ/ref fixes.

### Deliberately NOT changed

Reference-image bytes (only `reference_count/names` sent — documented extension point; sending bytes would need an API/provider-spend change); text-to-image model gap (needs provider credentials, not a code bug); entitlement denials (expected restrictions with correct messages and zero charges).

---

## Phase 8 — Regression Suite

| Check | Result |
|---|---|
| `tsc --noEmit` | clean |
| ESLint (touched files) | clean |
| `vitest` | **9 files / 70 tests pass** (incl. new `EditorToolRail.sections.test.ts`: every section has tools or a route; batch routes to `/tools/batch-editor`) |
| `next build` | succeeds |
| Rebuilt frontend container | editor `HTTP 200`, API rewrite → backend auth guard correct |
| Runtime E2E (fresh users) | resize, bg-remove (+media fetch), marketplace-resize, passport, batch-1, export, retry-reject, cancel-refund, entitlement-403-no-charge, unknown-op-422 — all as tabulated |

**Manual QA still suggested:** open editor → upload → expand rail sections → run BG Remove → undo/redo → export → Quick AI card → `/tools/batch-editor` with 1 image → confirm header credit decrement.

---

## Phase 9 — No-Feature-Regression Comparison

- **BEFORE feature count:** 60 editor files; 27 registry ops; 8 providers; 12 AI endpoints; 12 image endpoints; full studio/batch/export/history surface (per Phase-0 inventory).
- **AFTER feature count:** identical (no removals).
- **Removed:** 0 tools, 0 providers, 0 models, 0 endpoints, 0 pipeline stages, 0 fallbacks.
- **Modified:** `EditorHeader.tsx` (Save wired), `EditorToolRail.tsx` (sections wired + export for tests).
- **New:** `EditorToolRail.sections.test.ts` (dead-button regression guard).
- **Fixed:** 2 verified dead-UI failures (Save, rail sections/CTA). **Broken remaining:** 0 verified.

## Remaining risks & notes

1. Host port is ephemeral (`32768→32769→32770` across rebuilds) — always read `docker port toolhub-ai-frontend-1`.
2. Batch child completion is async; detail may read `processing` for seconds — poll, not a failure.
3. Cloudflare/HF-gated models need real credentials for full generative coverage; local paths cover Free-tier verification without spend.
4. No migrations, no new env vars required.
