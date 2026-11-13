# PROVIDER → OPERATION → CREDIT → PRICE CHAIN — ToolHub-AI

> Per-provider/model commercial chain: real pricing unit → estimated USD per tool operation → recommended credit cost → minimum profitable customer price.
> No code modified, no DB changed, no pricing changed. Tags: **VERIFIED** = official docs/source · **ASSUMED** = labeled estimate · **UNKNOWN** = not found, never invented.
> Prices checked 2026-09-20. Economics basis: retail anchor $0.02/credit, cost budget $0.0094/credit @50% margin (see `PRICING_BUSINESS_MODEL_AUDIT.md`); fee 2.9%+$0.30 ASSUMED; infra $2/mo ASSUMED.

## 1. Pricing units (original, per provider)

| Provider / Model | Pricing unit (original) | Rate | Source |
|---|---|---|---|
| Cloudflare Workers AI | per Neuron | **$0.011 / 1,000 Neurons**; 10,000 free/day per account (shared) | developers.cloudflare.com/workers-ai/platform/pricing (2026-09-17) |
| flux-2-klein-4b | per 512×512 tile | in $0.000059 / out $0.000287 |同上 |
| flux-2-klein-9b | per megapixel | $0.015 first MP + $0.002/extra MP + $0.002/input MP |同上 |
| leonardo lucid-origin | per tile + per step | $0.006996/tile + $0.000132/step |同上 |
| leonardo phoenix-1.0 | per tile + per step | $0.00583/tile + $0.00011/step |同上 |
| sdxl-base (CF) | per step (Beta) | $0.00 | CF model page (2026-09-20) |
| sd15-img2img / inpaint, dreamshaper-8, sdxl-lightning (CF) | per model unit | UNKNOWN (absent from pricing page) | — |
| Bria RMBG 2.0 (via fal/HF route) | per image | **$0.018** | fal.ai model page |
| Qwen-Image-Edit (via fal/HF route) | per megapixel | **$0.03/MP** (pricing page lists $0.02 — model page $0.03 governs) | fal.ai model page + fal.ai/pricing |
| HuggingFace routed | pass-through compute×hardware, no markup | varies | huggingface.co/docs/inference-providers/pricing |
| mock / local / local_rmbg / comfyui_local | n/a (own hardware) | $0 | repo adapters (`is_configured→True`) |

## 2. Estimated USD per tool operation (typical 1024×1024, single output, default steps)

| Model | Math | Est. USD / op | Confidence |
|---|---|---|---|
| flux-2-klein-4b txt2img | 4 tiles × $0.000287 | **$0.0012** | VERIFIED |
| flux-2-klein-4b edit | $0.001148 + 4 × $0.000059 | **$0.0014** | VERIFIED |
| flux-2-klein-9b txt2img | $0.015 | **$0.015** | VERIFIED |
| flux-2-klein-9b edit | $0.015 + $0.002 | **$0.017** | VERIFIED |
| lucid-origin (20 steps) | 4 × $0.006996 + 20 × $0.000132 | **$0.031** | VERIFIED |
| phoenix-1.0 (20 steps) | 4 × $0.00583 + 20 × $0.00011 | **$0.026** | VERIFIED |
| Bria RMBG 2.0 | flat | **$0.018** | VERIFIED |
| Qwen edit 1MP / 2MP | $0.03 × MP | **$0.03 / $0.06** | VERIFIED |
| sdxl-base (beta) | $0.00/step | **~$0.00** | VERIFIED ($0 — re-check invoice) |
| sd15 / dreamshaper / lightning | UNKNOWN | **UNKNOWN** (plan at $0.001–0.003 analog, ASSUMED) | UNKNOWN |
| mock / local / rmbg / comfyui | — | **$0.00** | VERIFIED (code) |

Step counts are runtime choices (klein-9b fixed 4, lightning ~4, SDXL default 20): tile+step models scale with steps — unit VERIFIED, count typical (ASSUMED).

## 3. Per-tool chain (36 tools)

Rule: `credits = ceil(USD / 0.0094)` @50% margin; single-op floor ≈ `USD / 0.47` (margin + fee share). Retail value = credits × $0.02.

| # | Tool | Cheapest live path (USD) | Expensive live path (USD) | Recommended credits (math) | Current BE ¢ | Verdict |
|---|---|---|---|---|---|---|
| 1-7 | Pan / Resize / Crop / Social / Rotate / Compress / Convert | canvas/client $0 | — | **0** | 0 | ✅ keep |
| 8 | Watermark | Pillow $0 | — | **0** | 0 | ✅ keep |
| 9 | Product Image | Pillow $0 | — | **0–2** (reconcile BE key 3 → Pillow path) | FE 2 / BE 3 | ❌ unify (mismatch) |
| 10 | Mockup | Pillow $0 | — | **0–2** (reconcile BE key 4 → Pillow path) | FE 2 / BE 4 | ❌ unify (mismatch) |
| 11 | BG Remove | local $0 | Bria $0.018 | **1 local / 2 HF** (2×0.0094=$0.0188 ≥ $0.018 ✓) | 1 | ❌ model-aware 1–2 (HF path loses at 1) |
| 12 | Passport | mock $0 | — | **1** (margin-positive by design) | 1 | ✅ keep |
| 13 | Upscale | local/comfy $0 | — (no paid cap) | **2** (ledger + infra) | 2 | ✅ keep |
| 14 | Enhance | $0 | — | **1** | 1 | ✅ keep |
| 15 | Object Remove | local/comfy $0 | CF-inpaint UNKNOWN (~$0 beta?) | **2** (confirm on CF invoice) | 2 | ✅ keep, verify |
| 16 | Generative Fill | mock/local $0 | Qwen $0.03 / flux-9b $0.017 | **model-aware 1 / 2 / 4** (Qwen: ceil(.03/.0094)=4 → $0.0376 ≥ $0.03 ✓) | flat 3 | ❌ flat 3 → 2–4 |
| 17 | BG Generate | local $0 | Qwen $0.03 | **model-aware 1 / 2 / 4** | flat 3 | ❌ flat 3 → 2–4 |
| 18 | Expand | $0 | — | **3** | 3 | ✅ keep |
| 19 | Relight | $0 | — | **2** | 2 | ✅ keep |
| 20 | Shadow | $0 (local-only) | — | **2** | 2 | ✅ keep |
| 21 | Recolor | $0 | — | **2** | 2 | ✅ keep |
| 22 | Retouch | $0 | — | **2** | 2 | ✅ keep |
| 23 | Text-to-Image | flux-4b $0.0012 | lucid $0.031 | **model-aware 1 / 2 / 4** (4b=1, 9b=2, leonardo=4; 3×0.0094=$0.0282 < $0.031 ✗) | flat 2 | ❌ flat 2 → 1–2–4 |
| 24 | Marketplace Resize | $0 | — | **1** | 1 | ✅ keep |
| 25 | Product Staging | $0 | — | **3** | 3 | ✅ keep |
| 26 | Product Photography | $0 | — | **3** | 3 | ✅ keep |
| 27 | Fashion Model | $0 | — | **4** (heavy composite ledger) | 4 | ✅ keep |
| 28 | Ghost Mannequin | $0 | — | **3** | 3 | ✅ keep |
| 29 | Flat Lay | $0 | — | **2** | 2 | ✅ keep |
| 30 | Fashion Retouch | $0 | — | **2** | 2 | ✅ keep |
| 31 | Infographic | $0 | — | **3** | 3 | ✅ keep |
| 32 | Size Chart | $0 | — | **2** | 2 | ✅ keep |
| 33 | Carousel | $0 | — | **4** | 4 | ✅ keep |
| 34 | Social Creative | $0 | — | **3** | 3 | ✅ keep |
| 35 | Ad Creative | $0 | — | **3** | 3 | ✅ keep |
| 36 | AI Studio | per-step sum | per-step sum | **sum of steps** | 0 | ✅ (steps charged) |

## 4. Minimum profitable customer price

Per single operation, floor ≈ `USD / 0.47` (50% margin + fee share). The $0.30 fixed fee makes single-op sales irrational below ~$0.50 — hence credits/packs (bundling amortizes the fee):

| Operation example | USD | Single-op floor | Credit route (retail) | Verdict |
|---|---|---|---|---|
| Bria bg-remove | $0.018 | ≈ $0.04 | 2cr ≈ $0.04 | ✅ parity |
| Qwen edit 1MP | $0.03 | ≈ $0.064 | 4cr = $0.08 | ✅ covered |
| Qwen edit 2MP | $0.06 | ≈ $0.128 | 4cr + R(2MP)=1.5× → 6cr = $0.12 | ⚠️ needs resolution multiplier |
| flux-9b txt2img | $0.015 | ≈ $0.032 | 2cr = $0.04 | ✅ covered |
| lucid txt2img | $0.031 | ≈ $0.066 | 4cr = $0.08 | ✅ covered |
| flux-4b txt2img | $0.0012 | ≈ $0.003 | 1cr = $0.02 (margin ~94%) | ✅ best margin |
| local/mock op | $0.00 | $0.00 | 1–2cr pure margin | ✅ profit engine |

Pack floors (formula `Pmin=(C·k+0.30)/(0.971−m)`, I=0 one-time): 200cr@k=$0.01 → $5.03/50% ⇒ **$4.99 only at 40%+ with k≤$0.01**; 500cr → $9.28@40% ⇒ **$11.99** safe; 1000cr → $17.87@40% ⇒ **$18.99** safe with 4cr-gate.

## 5. What changes vs today (4 items)

1. **bg-remove 1 → model-aware 1–2** (HF path loses $0.0086/op at 1cr).
2. **generative-fill / bg-generate flat 3 → model-aware 2–4** (Qwen path loses at 3cr).
3. **text-to-image flat 2 → model-aware 1–2–4** (leonardo loses $0.003–0.005/op at flat 2/3).
4. **product-image / mockup FE/BE unification** (2 vs 3, 2 vs 4) + resolution multiplier R (≤1024=1.0 / ≤2048=1.5 / >2048=2.0) for MP-priced models.

Everything else (30 tools) is correctly priced today because 25 run at $0 provider cost.

## 6. Sources & dates

- Cloudflare Workers AI pricing (per-model neuron table): developers.cloudflare.com/workers-ai/platform/pricing — 2026-09-17
- SDXL-beta $0.00/step: developers.cloudflare.com/workers-ai/models/stable-diffusion-xl-base-1.0 — 2026-09-20
- FLUX.2 klein-9b 4-step/multipart spec: developers.cloudflare.com/changelog/post/2026-01-28 — Jan 2026
- Bria RMBG $0.018: fal.ai/models/fal-ai/bria/background/remove — 2026-09-20
- Qwen edit $0.03/MP: fal.ai/models/fal-ai/qwen-image-edit-2511 — 2026-09-20 (pricing page lists $0.02 — model page governs)
- HF pass-through + $0.10/$2 credits: huggingface.co/docs/inference-providers/pricing — 2026-09-20
- Repo: `backend/apps/ai_tools/registry.py`, `services.py:50`, `frontend/src/constants/toolRegistry.ts`

## 7. Open unknowns (do not price against these until resolved)

1. CF neuron rates: sd15-img2img, sd15-inpaint, dreamshaper-8, sdxl-lightning (absent from pricing page; beta cohort likely $0 — confirm on first invoice; plan at $0.001–0.003 analog ASSUMED).
2. Per-call steps/MP actually used (not logged — needs metering code).
3. Qwen 2MP+ edits (covered by R multiplier once wired).
4. xKiro/OpenRouter-free commercial terms; vendor RPM quotas; true infra $/user/mo; Stripe fee schedule.

## 8. Addendum 2026-09-26 — model-aware display (closes §5 items 2–3)

§5 demanded model-aware pricing (flat 3 → 2–4 for generative fills, flat
2 → 1–2–4 for T2I). The charge side already was model-aware
(`cost = max(model floor, ceil(USD×R/0.0094))`); the gap was DISPLAY
(frontend static labels). Fixed: every AI selector now shows the
backend-quoted per-model cost (`onCostChange`), falling back to the static
label only before a model loads. Floors unchanged (margin protection),
except cf-flux-klein-9b 3→2 per §4 math ($0.0188 ≥ $0.015 ✓).

New-model chain rows (same $0.0094 budget): FASHN $0.075→8cr, PhotoRoom
$0.10→11cr, fal-relight/product $0.04→5cr, kontext $0.025→3cr, schnell
$0.003→floor 2, esrgan→floor 2, or-gemini ~$0.02→3cr (PARTIALLY — actuals
captured per call). Resolution multiplier R already wired in
`quote_credits_for_model` (Qwen 2MP → 6cr per §4).
