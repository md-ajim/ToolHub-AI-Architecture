# ToolHub-AI — Model Capability & Compatibility Matrix

> Machine-readable source: `docs/model-capability-matrix.json` (generated
> from live code — backend is the source of truth).

## 0. Two visibility rules (both enforced)

1. **Selector = visible by design.** `/ai/models/` returns EVERY
   capability-compatible model (never test mocks), each with honest flags:
   `locked` + `requires_plan` ("Pro"/"Business" — unlocks on plan upgrade),
   `available` (runnable right now), `configured`, `unavailability_reason`.
   Premium models are shown locked — never hidden.
2. **Execution = strict gate.** `enqueue_ai_job` still requires a runnable
   model: locked → `MODEL_TIER_LOCKED` (403, upgrade CTA); compatible but
   not runnable → `MODEL_UNAVAILABLE` (403); incompatible →
   `MODEL_CAPABILITY_MISMATCH` (422). Visibility never implies runnability.
> Canonical contracts: `backend/apps/ai_tools/capabilities.py`.
> Eligibility: `backend/apps/ai_tools/eligibility.py`.
> Live-verification store: `backend/apps/ai_tools/live_verification.json`
> (written ONLY by `manage.py verify_models --live` after real inference).
> Gate: `AI_REQUIRE_LIVE_VERIFICATION` (default True).

## 0. Status semantics (enforced)

| Status | Meaning | Selector-eligible |
|---|---|---|
| VERIFIED_PRODUCTION | live inference succeeded + output + op-validation passed (recorded) | YES — the only eligible state |
| PENDING_LIVE_VERIFICATION | assessed production-grade, NO live proof yet | NO |
| REACHABLE_UNVERIFIED | configured + reachable, inference not yet run (transient verify_models label) | NO |
| BETA | provider-real but unverified/unstable pricing or quality | NO |
| DISABLED / UNKNOWN | never selectable | NO |
| TEST_ONLY | unit-test mocks + local-deterministic-as-AI | NO (tests only, `include_test_only=True`) |

Assessed quality (`MODEL_QUALITY`) without a live record is NEVER exposed
as VERIFIED. `quality_status_for_model()` returns the static assessment;
`live_status.effective_quality_status()` applies the gate; the registry,
`/ai/models/`, capabilities view, routing, and fallback all consume the
effective status.

## 1. Live verification results (2026-09-26, Docker root .env)

Command: `python manage.py verify_models` (checks) and
`verify_models --live --models ...` (inference, owner budget).

> Correction note: an earlier round tested `backend/.env` placeholders and
> wrongly reported HF/CF tokens invalid. Docker Compose injects ROOT `.env`
> into backend+worker; re-verification below uses those real values.

| Model | Provider | Configured | Reachable | Inference | Output | Op-check | Status |
|---|---|---|---|---|---|---|---|
| local-rmbg-u2net | local_rmbg | yes | yes | pass (45.5s CPU) | pass RGBA 128×128 | pass alpha=(0,255) | VERIFIED_PRODUCTION |
| cf-flux-klein-4b | cloudflare | yes | yes (Workers AI catalog) | pass | pass | pass T2I | VERIFIED_PRODUCTION |
| cf-flux-klein-9b | cloudflare | yes | yes | pass | pass | pass T2I | VERIFIED_PRODUCTION |
| photoroom-ghost-mannequin | photoroom | yes | yes (quota: 10 imgs) | pass (11.9s) | pass 1024×1024 RGBA | pass transformed | VERIFIED_PRODUCTION |
| photoroom-flat-lay | photoroom | yes | yes | pass (9.8s) | pass 1024×1024 RGBA | pass transformed | VERIFIED_PRODUCTION |
| photoroom-shadow | photoroom | yes | yes | pass (1.1s) | pass RGBA | pass transformed | VERIFIED_PRODUCTION |
| hf-bria-rmbg | huggingface | yes (token valid, whoami 200) | yes | BLOCKED — account inference credits depleted | — | — | REACHABLE_UNVERIFIED (owner: fund HF / PRO) |
| or-gemini-flash-image | openrouter | yes (key valid) | yes | BLOCKED — balance exhausted (402, integration path proven) | — | — | REACHABLE_UNVERIFIED (owner: top up) |
| fal-* (8: esrgan/fashn/kontext/schnell/product/relight/qwen-inpaint/outpaint) | fal | yes (key valid format) | yes | BLOCKED — **account locked, TOP_UP required** (403) | — | — | REACHABLE_UNVERIFIED (owner: fund fal.ai) |
| hf-qwen-image-edit | huggingface | flag ON, token valid | yes | not attempted (same billing block as bria) | — | — | PENDING |
| comfyui-local-* (4) | comfyui_local | enabled | NO — service unreachable here | — | — | — | PENDING |
| cf BETA family (6) | cloudflare | yes | yes | not attempted (BETA hidden by design) | — | — | BETA |
| fal-* (6), photoroom-* (2) | fal/photoroom | NO key in any env | no | — | — | — | PENDING (owner: fund + key) |
| mock-* (5), local-det-as-AI | mock/local | n/a | n/a | never attempted | n/a | n/a | TEST_ONLY |

No user credits were charged (verification calls adapters directly,
bypassing `CreditService`). Cloud spend: ~$0.02 total (2× FLUX T2I + probes).

## 2. Tool → capability → compatible production models (effective, today)

16 of 30 operations READY (5 more are deterministic utilities, always on):

| Tool | Compatible (effective) | Recommended |
|---|---|---|
| background-remove, passport-photo | local-rmbg-u2net | local-rmbg-u2net |
| text-to-image, generative-fill, background-generate, product-edit, mockup-generate | cf-flux-klein-9b, cf-flux-klein-4b | cf-flux-klein-9b |
| shadow | photoroom-shadow | photoroom-shadow |
| ghost-mannequin | photoroom-ghost-mannequin | photoroom-ghost-mannequin |
| flat-lay | photoroom-flat-lay | photoroom-flat-lay |
| marketplace-resize (NON-AI utility) | local-deterministic | local-deterministic |
| infographic, size-chart, carousel, social-creative, ad-creative (NON-AI deterministic compositors, no AI selector, 1cr) | local-creative-compose | local-creative-compose |
| all other AI operations | — none runnable — (compatible models VISIBLE with lock/setup badges) | none |

When HF is funded / ComfyUI reachable / fal+PhotoRoom+OpenRouter funded,
their models promote automatically with NO code change.

## 3. Removed from production (TEST-ONLY, unit tests only)

`mock-bg-remove`, `mock-generative-fill`, `mock-expand`, `mock-relight`,
`mock-text-to-image` (`is_mock=true`, `production_available=false`) and
`local-deterministic` as an AI model (22 fake AI caps stripped →
`["marketplace-resize"]`). `MockImageProvider` source kept for tests;
`get_fallback_provider()` and `TASK_MODEL_ROUTES` cannot reach
`mock`/`local`; spend-cap reroute targets $0 production only
(comfyui_local/local_rmbg).

## 4. Credential-gated availability

- **`fal` (INTEGRATED, awaiting key — code-complete):** `fal-esrgan-upscale`
  (upscale, free-tier, 2cr), `fal-fashn-tryon` (fashion-model, max-tier, 8cr,
  garment reference required), `fal-flux-kontext-edit` (background-generate,
  product-edit, mockup-generate, pro, 3cr), `fal-flux-schnell-t2i`
  (text-to-image, pro, 2cr), `fal-product-photography` (product-photography
  + product-staging, pro, 5cr), `fal-relight` (relight, pro, 5cr,
  style presets: natural/studio/golden_hour/…/ambient). Set `FAL_KEY`, fund
  the fal account, run `verify_models --live --models fal-...` → auto-promote.
- **`photoroom` (INTEGRATED, awaiting key — code-complete):**
  `photoroom-ghost-mannequin` (dedicated endpoint, max-tier, 11cr),
  `photoroom-flat-lay` (dedicated endpoint, pro, 11cr). $0.10/Image Editing
  API call. Set `PHOTOROOM_API_KEY` → `verify_models --live` → auto-promote.
  Sandbox mode is never used (watermark risk).
- **`openrouter` (INTEGRATED, key valid, balance exhausted):**
  `or-gemini-flash-image` (text-to-image, background-generate, product-edit,
  mockup-generate, pro, 2cr) via dedicated `/api/v1/images` API (OpenAPI
  verified). Live run reached the provider and got a clean 402 —
  integration path proven; top up OpenRouter balance → re-run `--live` →
  auto-promote. Reported per-call cost is captured in job metadata.
- `huggingface`: token VALID (whoami 200), flags ON in root `.env`, but the
  HF account's inference credits are depleted → fund HF (or PRO) → re-run
  `--live` → `hf-bria-rmbg` / `hf-qwen-image-edit` promote.
- `cloudflare`: hidden until valid account+token AND live record. BETA
  family (sdxl-base, sd15-*, dreamshaper, lightning, leonardo) stays hidden
  until promoted with evidence.
- `comfyui_local`: hidden until `COMFYUI_ENABLED=true` + reachable service
  + live record.
- `openai` / `stability` image adapters: `supports()=False` — never listed.
- `local_rmbg` (U²-Net): VERIFIED live; quality below BRIA-2.0/BiRefNet —
  superseded automatically once those verify (recommended-first ordering).
