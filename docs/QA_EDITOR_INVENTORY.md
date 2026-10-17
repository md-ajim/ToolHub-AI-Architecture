# QA Editor Inventory — ToolHub-AI AI Image Editor

**Date:** 2026-09-28 · **Agent:** Production AI Editor QA · **Phase:** 1 Discovery (read-only)
**Rule:** nothing below is estimated. `UNVERIFIED` means not yet verified in this QA cycle.

Sources (all read from repo, Sep 2026 state):
`backend/apps/ai_tools/registry.py` (OPERATION_REGISTRY, 30 ops),
`backend/apps/ai_tools/capabilities.py`, `eligibility.py`, `live_status.py`,
`live_verification.json` (10 records), `docs/model-capability-matrix.json`
(39 models, 16 READY tools), `frontend/src/components/editor/*`,
`frontend/src/constants/toolRegistry.ts`, `src/app/tools/*/editor/page.tsx`.

---

## 1. SHARED PIPELINE (identical for every tool — verified in code)

| Stage | Contract |
|---|---|
| API | `POST /ai/operation/` (generic) + legacy per-tool POSTs (`/ai/background-remove/`, `/upscale/`, `/enhance/`, `/object-remove/`, `/passport-photo/`, `/generative-fill/`, `/background-generate/`, `/expand/`, `/relight/`); models via `GET /ai/models/?tool_name=<op>` |
| JOB_FLOW | enqueue → `job_id` → poll `GET /ai/jobs/{id}/` every 2s, max 180 (~6 min) → `completed`/`failed`; per-item retry `POST /ai/jobs/{id}/retry/`; cancel `POST /ai/jobs/{id}/cancel/`; Celery worker executes; batch reuses same per-item enqueue |
| CREDIT_FLOW | backend quote `max(model_floor, ceil(est_USD × R / 0.0094))` → reserve on enqueue → success consumes (`consumed=reserved`, no second debit) → failure/cancel/expire refunds automatically; QA accounts bypass (reserve 0). Frontend never prices (display-only `cost_per_operation`) |
| LAYER | `applyResult(fileData, {mode: replace\|layer})` — result lands as new layer or replaces; non-destructive layer stack preserved |
| HISTORY | snapshot history, cap 50, undo/redo/restore; server project versions separate |
| EXPORT | Export dialog (format presets); download/Save per result |
| SELECTOR | 6 execution groups; `locked` (plan) / `available` / `configured` / `unavailability_reason` flags; execution revalidated server-side (`MODEL_TIER_LOCKED` 403, `MODEL_UNAVAILABLE` 403, `MODEL_CAPABILITY_MISMATCH` 422); no compatible model → explicit unavailable state (never silent) |

## 2. PROVIDER ACCESS STATE (verified 2026-09-28)

| Provider | State | Evidence |
|---|---|---|
| cloudflare | LIVE (2 models verified 2026-09-26) | `cf-flux-klein-9b` 2.7s 1024×1024; `cf-flux-klein-4b` 33.1s |
| local_rmbg | LIVE (local CPU, $0) | `local-rmbg-u2net` verified |
| photoroom | LIVE per record 2026-09-26 (paid calls — NOT re-run in this cycle) | flat-lay, ghost-mannequin, shadow records |
| local (deterministic) | LIVE infra, $0 | `local-deterministic`, `local-creative-compose` (TEST_ONLY status) |
| fal | DOWN — key rejected (HTTP 403) | `fal-esrgan-upscale`, `fal-flux-schnell-t2i` failed |
| huggingface | UNFUNDED — HTTP 402 Payment Required | `hf-bria-rmbg` failed |
| openrouter | EXHAUSTED — balance exhausted | `or-gemini-flash-image` failed |
| comfyui_local | DOWN — no server on :8188 | configured but unreachable; models unverifiable |
| mock / TEST_ONLY | GATED — never listed/runnable (`AI_ALLOW_MOCK_MODELS` default off) | — |
| openai | configured (per matrix provider list); no live record in cycle | UNVERIFIED |

**Cost policy for this cycle:** execute via $0 paths (local_rmbg, local deterministic)
for pipeline proof; paid providers are NOT re-run (their 2026-09-26 live records
stand; re-running spends owner funds). This is stated per-tool below.

## 3. PER-TOOL INVENTORY (30 operations)

Legend — MODELS/PROVIDER: production-compatible only. STATUS: READY (runnable
model exists) / UNAVAILABLE (no production model — UI must show explicit
unavailable state). EXEC in this cycle: LIVE_RUN (will execute $0 path) /
RELY_ON_RECORD (paid, record stands) / NO_RUN (no runnable model; UI-state only).

| TOOL | CANONICAL_OPERATION | MODELS (id · provider · cost) | INPUT_REQUIREMENTS | API/JOB/CREDIT | OUTPUT | LAYER/HISTORY/EXPORT | STATUS / EXEC | KNOWN_LIMITATIONS |
|---|---|---|---|---|---|---|---|---|
| Background Remove | background-remove | local-rmbg-u2net · local_rmbg · 1cr, VERIFIED_PRODUCTION | image file | shared | RGBA w/ transparency | shared | READY / LIVE_RUN | — |
| Text to Image | text-to-image | cf-flux-klein-9b · cloudflare · 2cr REC; cf-flux-klein-4b · cloudflare | **prompt required** (+aspect/resolution per UI) | shared | generated RGB image | shared | READY / RELY_ON_RECORD | paid; not re-run (cost) |
| Upscale | upscale | none | image file | shared | — | shared | UNAVAILABLE / NO_RUN | fal-esrgan 403; comfyui down |
| Enhance | enhance | none | image file | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Object Remove | object-remove | none | image + **mask** (required for listed providers) | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Inpaint | inpaint | none | image + **mask** | shared | — | shared | UNAVAILABLE / NO_RUN | fal-qwen-inpaint hard-requires mask_url (code-verified, unrunnable: fal 403) |
| Face Restore | face-restore | none | image file | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| AI Shadow | shadow | photoroom-shadow · photoroom · 11cr REC | image + strength/opacity params | shared | shadowed product | shared | READY / RELY_ON_RECORD | paid; record 2026-09-26 |
| Background Generate | background-generate | cf-flux-klein-9b/4b · cloudflare | image (+prompt per UI) | shared | restaged image | shared | READY / RELY_ON_RECORD | paid |
| Marketplace Resize | marketplace-resize | local-deterministic · local · TEST_ONLY | image + marketplace preset | shared | resized to preset dims | shared | READY / DETERMINISTIC_RUN | non-AI deterministic path; pixel-exact assertions only, no AI claim |
| Product Staging | product-staging | none | UNVERIFIED (params per UI) | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Product Photography | product-photography | none | UNVERIFIED (params per UI) | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Expand | expand | none | image (+direction per UI) | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Relight | relight | none | image + lighting style | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Recolor | recolor | none | image + target color | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Retouch | retouch | none | image file | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Fashion Model | fashion-model | none | garment image (params UNVERIFIED) | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Ghost Mannequin | ghost-mannequin | photoroom-ghost-mannequin · photoroom REC | garment image | shared | mannequin render | shared | READY / RELY_ON_RECORD | paid; record 2026-09-26 |
| Flat Lay | flat-lay | photoroom-flat-lay · photoroom REC | garment image | shared | flat-lay render | shared | READY / RELY_ON_RECORD | paid; record 2026-09-26 |
| Fashion Retouch | fashion-retouch | none | image file | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Infographic | infographic | local-creative-compose · local · TEST_ONLY | product image | shared | composed creative | shared | READY / DETERMINISTIC_RUN | deterministic path only |
| Size Chart | size-chart | local-creative-compose · local · TEST_ONLY | product image | shared | composed chart | shared | READY / DETERMINISTIC_RUN | deterministic path only |
| Carousel | carousel | local-creative-compose · local · TEST_ONLY | product image(s) | shared | composed set | shared | READY / DETERMINISTIC_RUN | deterministic path only |
| Social Creative | social-creative | local-creative-compose · local · TEST_ONLY | product image | shared | composed creative | shared | READY / DETERMINISTIC_RUN | deterministic path only |
| Ad Creative | ad-creative | local-creative-compose · local · TEST_ONLY | product image | shared | composed creative | shared | READY / DETERMINISTIC_RUN | deterministic path only |
| Generative Fill | generative-fill | cf-flux-klein-9b/4b · cloudflare | image + mask + **prompt required** | shared | filled region | shared layer mode | READY / RELY_ON_RECORD | paid |
| Product Edit | product-edit | cf-flux-klein-9b/4b · cloudflare | image + **prompt required** | shared | edited image | shared | READY / RELY_ON_RECORD | paid |
| Mockup Generate | mockup-generate | cf-flux-klein-9b/4b · cloudflare | image + **prompt required** | shared | mockup scene | shared | READY / RELY_ON_RECORD | paid |
| Expand Image | expand-image | none | image file | shared | — | shared | UNAVAILABLE / NO_RUN | no production model |
| Passport Photo | passport-photo | local-rmbg-u2net · local_rmbg | portrait image | shared | composed doc photo | shared | READY / LIVE_RUN | uses bg-remove model in pipeline |

## 4. FIXTURES / ENV FOR EXECUTION PHASES

- Fixtures: `backend/ai-inputs/*.png` (product shots, logos, screenshots).
- QA principal: `qa-test@toolhub.local` (unlimited bypass; provider spend still real → $0 paths only).
- Services: backend :8000 OK, frontend :32768 HTTP 200, db/redis/celery up; ComfyUI :8188 DOWN.
- Browser: playwright-core (/tmp/qa) + system Chrome/Chromium (headless).
- Allowed to execute: `local-rmbg-u2net`, `local-deterministic`, `local-creative-compose`
  (deterministic contract only). NEVER: mock/*, *-mock-*, TEST_ONLY-as-AI-proof,
  fal/* (403), hf-bria-rmbg (402), or-gemini-flash-image (exhausted),
  comfyui/* (down), any model whose live check fails at runtime.

## 5. OPEN ITEMS FOR LATER PHASES
- Paid re-runs (cloudflare/photoroom): owner approval + budget cap required.
- ComfyUI: start service to unlock upscale/enhance/inpaint/object-remove verification.
- 14 UNAVAILABLE tools: UI-state verification only until providers funded.
- Fal key (403), HF funding (402), OpenRouter top-up: owner actions.
