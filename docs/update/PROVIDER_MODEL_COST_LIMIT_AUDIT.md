# PROVIDER / MODEL COST & LIMIT AUDIT — ToolHub-AI

> Read-only audit. No code modified, no DB changed, no migrations, no pricing changed, no provider prices invented.
> Tags: **VERIFIED** = official docs or repo source with path · **PARTIALLY VERIFIED** = official pricing exists but a dimension is missing · **UNKNOWN** = not found · **ASSUMED** = estimate, never presented as verified.
> Dates checked: 2026-09-20. Repo paths relative to repo root unless noted.

## Critical context (applies to the whole file)

- Backend charges `cost = selected_model.cost_per_operation OR op fallback` (`backend/apps/ai_tools/services.py:50`) — **model cost wins**. Frontend `creditCost` is display-only.
- No USD provider price exists in the repo. All USD below comes from official provider docs fetched 2026-09-20 (URLs in §14); anything else is marked UNKNOWN/ASSUMED.
- Cloudflare's 10,000 free neurons/day is **per Cloudflare account (the owner's), shared across all users** — not per user.

# 1. Executive Summary

- **21 image models** in `backend/apps/ai_tools/registry.py:10-390`: 12 zero-cost (mock/local/rmbg/comfyui), 9 paid-capable (2 HuggingFace, 7 Cloudflare), 2 dormant adapters (openai/stability, `process()` raises `not_implemented`).
- **Paid spend is reachable today only via Cloudflare (with creds) and HuggingFace (with token).** Live env evidence: CF jobs complete (real spend), HF auto-routed jobs fail without token, ComfyUI-routed jobs queue forever (ComfyUI down).
- **Cheapest paid op verified: flux-2-klein-4b text-to-image ≈ $0.0012.** Most expensive verified: leonardo lucid-origin 1024² ≈ $0.031; Qwen edit 2MP ≈ $0.06.
- **Free tier that matters**: CF 10k neurons/day shared (≈ 8,700 flux-4b images or ~650 flux-9b images/day platform-wide); HF $0.10/mo free / $2/mo PRO pass-through credits.
- **Truthfulness gaps**: mock advertises 11 caps, executes 5; local advertises 25, executes 22 (truthful `supports()` hides the other 3); dormant openai/stability adapters can be selected then always fail; `cf-sd15-img2img` falls through to text-to-image dispatch.
- **Missing runtime dimensions**: per-model step counts, output counts, input-image counts/MP (CF flux path sends exactly 1 input), cached tokens (no handling anywhere), resolution multipliers — none touch pricing code today.
- **Commercial rule enforced by this report's tables**: identical credit costs are banned — cheap/local ≈ 0–1cr, moderate ≈ 2cr, expensive ≈ 3–4cr+, derived from the USD math in §11.

# 2. All Models Discovered

## 2a. Image models (21, `backend/apps/ai_tools/registry.py`)

| # | Model ID | Provider | Internal ID | Type | Tier/Credits |
|---|---|---|---|---|---|
| 1 | hf-bria-rmbg | huggingface | briaai/RMBG-2.0 | background removal | free / 1 |
| 2 | hf-qwen-image-edit | huggingface | Qwen/Qwen-Image-Edit-2511 | image editing | pro / 3 |
| 3 | mock-bg-remove | mock | mock-bg-remove-v1 | multi (11 caps) | free / 1 |
| 4 | mock-generative-fill | mock | mock-generative-fill-v1 | editing/inpaint | pro / 3 |
| 5 | mock-expand | mock | mock-expand-v1 | editing | pro / 3 |
| 6 | mock-relight | mock | mock-relight-v1 | editing | pro / 2 |
| 7 | local-rmbg-u2net | local_rmbg | local-rmbg-u2net-v1 | background removal | free / 1 |
| 8 | local-deterministic | local | local-deterministic-v1 | multi (25 caps, 22 executed) | free / 1 |
| 9 | comfyui-local-upscale | comfyui_local | comfyui-upscale-ultrasharp-4x | image generation (upscale) | free / 1 |
| 10 | comfyui-local-bg-remove | comfyui_local | comfyui-rmbg-bg-remove | background removal | free / 1 |
| 11 | comfyui-local-inpaint | comfyui_local | comfyui-inpaint-matt-lama | image editing | free / 2 |
| 12 | comfyui-local-face-restore | comfyui_local | comfyui-codeformer-face-restore | image editing | free / 1 |
| 13 | cf-flux-klein-9b | cloudflare | @cf/black-forest-labs/flux-2-klein-9b | image generation+editing | pro / 3 |
| 14 | cf-flux-klein-4b | cloudflare | @cf/black-forest-labs/flux-2-klein-4b | image generation+editing | pro / 2 |
| 15 | cf-sdxl-base | cloudflare | @cf/stabilityai/stable-diffusion-xl-base-1.0 | image generation | pro / 2 |
| 16 | cf-sd15-img2img | cloudflare | @cf/runwayml/stable-diffusion-v1-5-img2img | image editing | pro / 2 |
| 17 | cf-sd15-inpaint | cloudflare | @cf/runwayml/stable-diffusion-v1-5-inpainting | image editing | pro / 2 |
| 18 | cf-dreamshaper-8 | cloudflare | @cf/lykon/dreamshaper-8-lcm | image generation | pro / 2 |
| 19 | cf-sdxl-lightning | cloudflare | @cf/stabilityai/stable-diffusion-xl-lightning | image generation | pro / 2 |
| 20 | cf-leonardo-lucid-origin | cloudflare | @cf/leonardo/lucid-origin | image generation | pro / 3 |
| 21 | cf-leonardo-phoenix | cloudflare | @cf/leonardo/phoenix-1.0 | image generation | pro / 3 |

Capabilities, max_resolution [(4096² ×12, 2560² Qwen, 1920² flux-klein, 2048² rest)], formats (JPG/PNG/WEBP→PNG), quality/speed: `registry.py` lines per row above (agent-verified).

## 2b. Chat / LLM / other models

- **Mock (14)**: mock-light/flash/pro/frontier/reasoning/code/vision/image-gen/image-edit/stt/tts/embeddings/video/max — `backend/apps/ai_workspace/management/commands/seed_ai_models.py:5-319`, 0–3 credits/message, vision/STT/TTS/embeddings/video rows exist but gateway rejects non-chat (`gateway.py:174-182`) — seeded, NOT WIRED for their modalities.
- **Official gated (25)**: openai ×2, anthropic ×2, google ×2, deepseek ×2, meta ×1, huggingface ×6, self-hosted ×3, cloudflare ×5, xKiro ×7, openrouter ×18 — `seed_ai_models.py:326-1304`, seeded only when the provider key env is set (`:1310-1351`), manual seed only (no boot reseed).
- **Aggregators**: `xkiro_free_models.json` (7 entries, id/name/provider/is_free only — no endpoints/terms), `litellm_config.yaml` (11 aliases → `https://api.xkiro.com/v1` via `XKIRO_API_KEY`; master key placeholder). **NovitaAI: ABSENT** from app code/config (only vendored HF-hub shims mention it). **LiteLLM: config-file only**, no Python import; traffic goes direct via `openai_compatible` adapter.

# 3. Provider-by-Provider Pricing

| Provider | Pricing unit (original) | Rate (official) | Free tier | Source |
|---|---|---|---|---|
| Cloudflare Workers AI | per Neuron ($0.011/1,000); per-model unit tables | §4 rows | 10,000 neurons/day/account; some models require Paid plan ($5/mo) | developers.cloudflare.com/workers-ai/platform/pricing (2026-09-17) |
| HuggingFace Inference Providers | pass-through, per compute-time×hardware price; no HF markup | per-request compute (ex: FLUX.1-dev 10s × $0.00012/s = $0.0012) | $0.10/mo free, $2.00/mo PRO/Team-seat; overage = credit purchase | huggingface.co/docs/inference-providers/pricing |
| fal.ai (underlying HF route for bria/Qwen) | per image / per megapixel | Bria RMBG 2.0 **$0.018/image**; Qwen Image Edit **$0.03/MP** (pricing page lists Qwen $0.02/MP — model page $0.03 governs) | none (pay-per-use, no subscription) | fal.ai/models/fal-ai/bria/background/remove; fal.ai/models/fal-ai/qwen-image-edit-2511; fal.ai/pricing |
| mock/local/local_rmbg/comfyui_local | n/a (self-hosted) | $0 | unlimited (own hardware) | code: always-configured adapters |
| openai/stability (adapters) | n/a | dormant (`not_implemented`) | n/a | `openai_provider.py:28-33`, `stability.py:16-19` |
| xKiro / OpenRouter free rows | via key, per provider terms | UNKNOWN (terms not in repo) | `is_free:true` flags only | `xkiro_free_models.json`, seed rows (0 credits) |
| NovitaAI | — | ABSENT from repo | — | NOT FOUND |

# 4. Model-by-Model Pricing

## Image models (computed at 1024×1024 unless noted)

| Model | Pricing unit | Input price | Output price | Computed 1-op USD |
|---|---|---|---|---|
| hf-bria-rmbg | per image | — | $0.018/image | **$0.018** VERIFIED |
| hf-qwen-image-edit | per MP | $0.03/MP in+out | $0.03/MP | **$0.03 (1MP) / $0.06 (2MP)** VERIFIED |
| mock-*/local-*/rmbg/comfyui-* (12) | n/a | $0 | $0 | **$0.00** VERIFIED (code) |
| cf-flux-klein-4b | per 512-tile | $0.000059/tile | $0.000287/tile | **$0.0012** txt2img / **$0.0014** edit VERIFIED |
| cf-flux-klein-9b | per MP | $0.002/MP | $0.015 first MP + $0.002/MP | **$0.015** txt2img / **$0.017** edit VERIFIED |
| cf-leonardo-lucid-origin | per tile + per step | — | $0.006996/tile + $0.000132/step | **$0.031** @20 steps VERIFIED |
| cf-leonardo-phoenix | per tile + per step | — | $0.00583/tile + $0.00011/step | **$0.026** @20 steps VERIFIED |
| cf-sdxl-base | per step (Beta) | — | $0.00/step | **~$0.00** VERIFIED (model page; re-check invoice) |
| cf-sd15-img2img / inpaint / dreamshaper-8 / sdxl-lightning | per model unit | UNKNOWN | UNKNOWN | **UNKNOWN** (beta cohort — likely $0.00, VERIFY on first invoice; plan at $0.001–0.003 analog ASSUMED) |

Step counts are runtime choices (SDXL default 20, lightning ~4, klein-9b fixed 4): cost scales with steps on tile+step models — PARTIALLY VERIFIED (unit verified, count assumed typical).

## Chat/aggregator models

Per-message credits 0–4 in seed (VERIFIED); USD: `cost_engine.py` indicative table only (explicitly non-official) — official per-model USD: **UNKNOWN** for all. Vision has no surcharge key; cached input has no handling; STT/TTS/embeddings/video rows unwired.

# 5. Free Tier & Quotas

| Free tier | Quota | Temporary? | Payment method? | API users? |
|---|---|---|---|---|
| CF 10k neurons/day | per account (owner), shared platform-wide ≈ 8,700 flux-4b imgs or ~650 flux-9b imgs/day | permanent policy (subject to change) | Paid plan needed only for select models + overage | yes (owner key) VERIFIED |
| HF $0.10/mo (free acct) / $2/mo (PRO/seat) | pooled per account | monthly refresh | overage = credit purchase | yes, routed requests VERIFIED |
| xKiro `is_free` / OpenRouter `:free` rows | UNKNOWN terms | UNKNOWN | UNKNOWN | via owner key only |
| mock/local/comfyui | unlimited own-hardware | n/a | n/a | yes |
| ToolHub Free plan | 0 AI credits + daily-5 throttle | n/a | n/a | n/a (reserve blocks) VERIFIED |

"Free" badge rule: seed `tier:free` ≠ zero cost — HF free-tier rows still deduct credits and can spend vendor USD. Never treat as unlimited.

# 6. Rate Limits

- DRF: anon 10000/day, user 100000/day; scoped ai_chat 60/min, ai_compare 10/min, ai_upload 20/min (`base.py:240-252`) — no image-op scoped throttle. PARTIALLY VERIFIED (image views only import UserRateThrottle).
- Batch: ≤20 images/job (`base.py:378`, enforced `views.py:427-429`), credits reserved per image.
- ComfyUI: concurrency 1, 1h lock, 5s requeue; task soft/time 3600/3900s; retries max 3, backoff ≤60s.
- Provider env caps (daily/user/model/cost): exist in `limits.py:179-218`, default OFF.
- Vendor-side RPM/token/image limits: **UNKNOWN** (CF dashboard quotas, HF tier limits — check consoles, not in repo).

# 7. Context / Output / Image Limits

- Registry `max_resolution`: 4096² (12 models), 2560² (Qwen edit), 1920² (flux klein), 2048² (rest CF) — VERIFIED but **unenforced in code** (catalog-only).
- Formats: JPG/PNG/WEBP in, PNG out (all 21) — VERIFIED.
- klein-9b: up to 4 input images (official changelog) but repo sends exactly 1 (`cloudflare.py:279`) — PARTIALLY VERIFIED.
- Chat ctx/max-out per seed rows (§2b); vision flattened to text on anthropic/google adapters; image-count surcharge: none.

# 8. ToolHub-AI Runtime Wiring

Per class: `views.BaseAIToolView.post` (`views.py:31-50`) → `services.enqueue_ai_job` (`:18`) → `select_model` (configured + supports + tier + rank `:493-557`) → charge (`:50`) → limits (`:56`) → Celery (`:90-98`, comfy→dedicated worker) → `_try_provider` + fallback (`tasks.py:67-107`) → adapter `process()` → external API. Batch fans out per image (`views.py:452-459`).

Status per model: **A LIVE+WIRED**: local, local_rmbg, mock (5 ops), cloudflare (with creds), huggingface (with token), comfyui (if up). **C WIRED-requires-credentials**: HF + CF rows without keys (auto-skipped by `is_configured`). **D FREE/LOCAL**: 12 models. **E MOCK/TEST**: mock rows. **F DORMANT**: openai/stability adapters. **G UNKNOWN**: none (all classified).

# 9. Cost Calculation Formula Per Model

- **CF tile/step**: `tiles(ceil(w/512)×ceil(h/512)) × tile_rate + steps × step_rate` (+ input tiles/MP where applicable). Missing runtime data: actual steps used per call (not logged) — PARTIALLY VERIFIED.
- **CF per-MP (klein-9b)**: `$0.015×first + $0.002×extra_MP + $0.002×input_MP`. Missing: actual output MP per call (request width/height available in code, not persisted) — PARTIALLY VERIFIED.
- **fal/HF flat**: per image ($0.018) / per MP ($0.03) — needs output MP only. VERIFIED modulo MP.
- **HF compute-time**: `seconds × hardware $/s` — NEITHER recorded → UNKNOWN per-op (only post-hoc HF billing page).
- **Chat**: `in_tokens×p_in + out_tokens×p_out` (+ image/cached splits unhandled) — tokens recorded (`AiUsageRecord`), USD rows missing for 8/11 providers → PARTIALLY VERIFIED.
- **STT/TTS/embeddings/video**: unwired → no formula applicable.

# 10. Verified vs Partial vs Unknown Pricing

- VERIFIED: CF $0.011/K neurons + full image table + sdxl $0.00/step; fal Bria $0.018; fal Qwen $0.03/MP; HF pass-through + $0.10/$2 credits; zero-cost set; dormant adapters.
- PARTIALLY: klein-9b/flux-4b/lucid/phoenix (need runtime steps/MP per call); chat token math (missing image/cached splits + 8 provider USD rows).
- UNKNOWN: 4 CF beta image models' neuron rates; all chat per-model vendor USD; NovitaAI (absent); vendor RPM quotas; xKiro quota terms.

# 11. Raw Provider Cost Table

Per operation / per 100 / per 1,000 (typical 1MP single-output; steps=20 where step-priced):

| Model | 1 op | 100 ops | 1,000 ops |
|---|---|---|---|
| flux-2-klein-4b txt2img | $0.0012 | $0.12 | $1.15 |
| flux-2-klein-4b edit | $0.0014 | $0.14 | $1.38 |
| flux-2-klein-9b txt2img / edit | $0.015 / $0.017 | $1.50 / $1.70 | $15.00 / $17.00 |
| lucid-origin / phoenix-1.0 | $0.031 / $0.026 | $3.06 / $2.55 | $30.62 / $25.52 |
| Bria RMBG 2.0 | $0.018 | $1.80 | $18.00 |
| Qwen edit 1MP / 2MP | $0.03 / $0.06 | $3.00 / $6.00 | $30.00 / $60.00 |
| sdxl-base (beta $0) | ~$0.00 | ~$0.00 | ~$0.00 |
| local/mock/rmbg/comfyui | $0.00 | $0.00 | $0.00 |

Raw-USD equivalent of credits at $0.02 retail anchor (RAW VALUE, not price): 1=$0.02 · 10=$0.20 · 100=$2.00 · 500=$10.00 · 1000=$20.00. Provider-cost to serve N credits ranges $0.00 (all-local burn) to ~$0.03×N/… worst mix (all-Qwen-2MP ≈ $0.06/op at 3–4cr ⇒ up to ~$0.015–0.02 provider per credit — the margin boundary).

# 12. Missing Information Required Before Commercial Pricing

1. CF neuron rates for sd15-img2img/inpaint, dreamshaper-8, sdxl-lightning (or first-invoice confirmation of $0). 2. HF/Bria price changes (re-check quarterly; fal pricing drifts). 3. Actual steps + MP logged per call (code change required). 4. Vendor RPM quotas for owner keys. 5. xKiro/OpenRouter-free commercial terms. 6. Chat per-model USD (or drop chat from margin math). 7. Infra $/user/mo + Stripe fee schedule. 8. Real Stripe price IDs in prod DB.

# 13. Recommended Data Model for Provider Costs

`ProviderModelCost { provider, model_id, pricing_unit(enum), input_price_usd, output_price_usd, step_price_usd, mp_price_usd, currency, source_url, verified_at, free_quota_json }` seeded from §4, served read-only to billing; `enqueue_ai_job` computes `estimated_usd` + stores on job; worker writes `actual_usd`; `record_provider_spend(actual)` wired (currently zero callers); capabilities API returns `cost_policy{credits, estimated_usd}` so frontend shows both. Migrate `AI_TOOL_CREDIT_COSTS` values into rows; keep `AI_CREDIT_COSTS_JSON` as emergency override only.

## Final table (one row per image model; chat summarized below)

| Provider | Model ID | Model Type | Tool | API Status | Pricing Unit | Input Price | Output Price | Image In | Image Out | Free Tier | Rate Limit | Context Window | Max Output | Actual Op Cost | Confidence | Official Source | Last Verified |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| huggingface | briaai/RMBG-2.0 | bg removal | bg-remove | C (needs token) | per image | — | $0.018 | — | $0.018/img | HF $0.10/$2 shared | UNKNOWN vendor | n/a (seg) | 4096² | $0.018 | VERIFIED | fal.ai/models/fal-ai/bria/background/remove; huggingface.co/docs | 2026-09-20 |
| huggingface | Qwen/Qwen-Image-Edit-2511 | image editing | generative-fill, bg-generate | C | per MP | $0.03/MP | $0.03/MP | $0.03/MP | $0.03/MP | HF shared | UNKNOWN | n/a | 2560² | $0.03–0.06 | VERIFIED | fal.ai/models/fal-ai/qwen-image-edit-2511 | 2026-09-20 |
| mock | mock-bg-remove-v1 (+3 rows) | multi | several | D/E live-partial | n/a | $0 | $0 | $0 | $0 | unlimited own | n/a | — | 4096² | $0.00 | VERIFIED | code mock.py:15-31 | 2026-09-20 |
| local_rmbg | local-rmbg-u2net-v1 | bg removal | bg-remove | D | n/a | $0 | $0 | $0 | $0 | unlimited own | n/a | — | 4096² | $0.00 | VERIFIED | code rembg_provider.py | 2026-09-20 |
| local | local-deterministic-v1 | multi (22 exec) | 20+ tools | D | n/a | $0 | $0 | $0 | $0 | unlimited own | n/a | — | 4096² | $0.00 | VERIFIED | code local_provider.py, pil_ops | 2026-09-20 |
| comfyui_local | ultrasharp-4x / rmbg / matt-lama / codeformer | gen/remove/edit/restore | upscale, bg-remove, object-remove, face-restore | D (if up) | n/a | $0 | $0 | $0 | $0 | unlimited own | concurrency 1 (code) | — | 4096² | $0.00 | VERIFIED | code comfyui_provider.py; base.py:407-411 | 2026-09-20 |
| cloudflare | flux-2-klein-4b | gen+edit | text-to-image, generative-fill, bg-generate | C | per tile | $0.000059/tile | $0.000287/tile | $0.000236/MP | $0.001148/MP | 10k neu/day shared | UNKNOWN vendor | n/a | 1920² | $0.0012–0.0014 | VERIFIED | CF pricing page | 2026-09-17 |
| cloudflare | flux-2-klein-9b | gen+edit | same + refs(≤4) | C | per MP | $0.002/MP | $0.015+0.002/MP | $0.002/MP | $0.015–0.019 | shared | UNKNOWN | n/a | 1920² | $0.015–0.019 | VERIFIED | CF pricing page | 2026-09-17 |
| cloudflare | sdxl-base-1.0 | generation | text-to-image | C | per step (Beta) | — | $0.00 | — | ~$0 | shared | UNKNOWN | n/a | 2048² | ~$0.00 | VERIFIED ($0) | CF model page | 2026-09-20 |
| cloudflare | sd1.5-img2img / inpaint / dreamshaper-8 / sdxl-lightning | gen/edit | fill/bg-gen/inpaint/txt2img | C | per model unit | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | shared | UNKNOWN | n/a | 2048² | UNKNOWN | UNKNOWN | CF pricing (absent) | 2026-09-20 |
| cloudflare | lucid-origin / phoenix-1.0 | generation | text-to-image | C | per tile+step | — | tile+step | — | tile+step | shared | UNKNOWN | n/a | 2048² | $0.031 / $0.026 | VERIFIED | CF pricing page | 2026-09-17 |
| openai / stability | (adapters) | — | none (raises) | F dormant | — | — | — | — | — | — | — | — | — | n/a | VERIFIED | code | 2026-09-20 |
| chat aggregate | 14 mock + 25 official + 7 xKiro + 18 openrouter | chat/vision/embed/stt/tts/video | workspace chat | mixed (A–F; video/speech/embed unwired) | per message (credits) / per-token vendor | UNKNOWN vendor | UNKNOWN vendor | n/a | n/a | HF/CF shared; xKiro UNKNOWN terms | DRF + scoped chat limits | per-row ctx in §2b | per-row max | UNKNOWN (tokens recorded, USD unwritten) | PARTIALLY | seed_ai_models.py; gateway.py | 2026-09-20 |

## DATA REQUIRED TO FINALIZE TOOLHUB-AI PRICING

- **Free plan**: confirm $0 paid-compute rule + abuse throttle values (daily-5 VERIFIED) — DONE, no further data needed.
- **Pro plan**: true k (provider $/credit) from 1 month of measured `actual_usd` per job — NEEDS worker metering first.
- **Business plan**: pooled-vs-seat decision + team size distribution (product decision, not data).
- **Credit packs**: fee schedule + k — formula ready, inputs pending.
- **Per-tool credits**: adopt §11 matrix (needs only the 4 UNKNOWN CF rates confirmed or conservatively priced).
- **Per-model credits**: needs step/MP logging per call (code gap) + UNKNOWN rates above.
- **Overage pricing**: decide pack-only vs metered overage (product decision); technical path = packs (no overage code exists — VERIFIED absent).

## Addendum 2026-09-26 — new providers/models (same tags/method as above)

| Model | Provider | Pricing unit (official) | Computed 1-op USD | Credits (ceil/USD÷0.0094 vs floor) | Confidence | Source |
|---|---|---|---|---|---|---|
| fal-esrgan-upscale | fal | $0.00111/compute-sec | ~$0.005 (small-image basis) | max(2, 1) = **2** | PARTIALLY (time varies) | fal.ai/models/fal-ai/esrgan |
| fal-fashn-tryon | fal | per generation | **$0.075** | max(8, 8) = **8** | VERIFIED | fal.ai/models/fal-ai/fashn/tryon/v1.6 |
| fal-flux-kontext-edit | fal | per MP | **$0.025** (1MP) | max(3, 3) = **3** | VERIFIED | fal.ai/models/fal-ai/flux-kontext |
| fal-flux-schnell-t2i | fal | per MP | **$0.003** (1MP) | max(2, 1) = **2** | VERIFIED | fal.ai/models/fal-ai/flux/schnell |
| fal-product-photography | fal | per image | **$0.04** | max(5, 5) = **5** | VERIFIED | fal.ai/models/fal-ai/image-apps-v2/product-photography |
| fal-relight | fal | per image | **$0.04** | max(5, 5) = **5** | VERIFIED | fal.ai/models/fal-ai/image-apps-v2/relighting |
| photoroom-ghost-mannequin | photoroom | per Image Editing API call | **$0.10** | max(11, 11) = **11** | VERIFIED | docs.photoroom.com (Plus plan) |
| photoroom-flat-lay | photoroom | per Image Editing API call | **$0.10** | max(11, 11) = **11** | VERIFIED | docs.photoroom.com (Plus plan) |
| or-gemini-flash-image | openrouter | per output (~$0.01–0.04/gen) | **$0.02** ASSUMED | max(2, 3) = **3** | PARTIALLY (reported cost captured per call in job metadata) | openrouter.ai/docs + /api/v1/images/models |

Notes: (1) Model catalog is now 31 rows (was 21). (2) Selectors list every
compatible model with lock/setup flags (visibility), execution keeps the
strict live-verification gate — visibility never implies runnability.
(3) cf-flux-klein-9b floor 3→2 per chain math ($0.0188 ≥ $0.015, margin
holds). (4) Mock rows are TEST-ONLY (never production-listed); dormant
openai/stability adapters unchanged.
