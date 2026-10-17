# PRICING & BUSINESS MODEL AUDIT — ToolHub-AI

> Analysis + commercial design ONLY. No code modified, no DB changed, no migrations, no checkouts, no pricing changed.
> Tags: **VERIFIED** = read in source with file:line · **PARTIALLY VERIFIED** = inferred across verified points with a gap · **UNKNOWN** = not found in repo (never invented).

## VERIFIED FINDINGS (top)

- Plans are DB-driven with seed `get_or_create` (never overwrites): Free $0/0cr/5MB/daily-5 · Pro $9.99 ($89/yr)/50MB/unlimited-daily · Business $29.99 ($299.90/yr)/500MB — `backend/apps/subscriptions/management/commands/seed_plans.py:53-112`
- Effective paid allocation today is **500 credits/mo via backend fallback** — Pro/Business seeds omit `monthly_credits` (`billing/services.py:174`, `billing/webhooks.py:188`)
- Credit lifecycle is reserve-before-dispatch with finalize-on-success and refund-on-failure (`ai_tools/services.py:59`, `tasks.py:150,182,194,220`)
- 21 image models catalogued with per-op credit costs 1–4 (`ai_tools/registry.py:10-490`); zero vendor-spend set = {mock, local, local_rmbg, comfyui_local} (`limits.py:49`)
- **No USD provider prices exist anywhere in the repo** — all USD below is explicit ASSUMPTION except Stripe-style fee math inputs

## PARTIALLY VERIFIED

- Paid spend currently reachable only via Cloudflare/HuggingFace (keys required); openai/stability adapters are dormant (`process()` raises not_implemented)
- Live env (observed): no HF token, ComfyUI down → only local/mock/CF can serve; HF-auto-routed jobs fail, ComfyUI-routed jobs queue forever
- Frontend displayed costs mostly match backend, except `product-image` (2 vs 3), `mockup` (2 vs 4), `?? 3` fallbacks vs backend default 2

## UNKNOWN (inputs required before commercial launch)

- True USD cost per image for: `briaai/RMBG-2.0`, `Qwen/Qwen-Image-Edit-2511`, and all 7 `@cf/*` Workers AI models (Neurons/run)
- Intended `monthly_credits` for Pro/Business (code shows 500-fallback, 100, 300/5000 in different places)
- Whether production Stripe price IDs replaced the `price_pro_monthly`-style placeholders
- Real infrastructure $/user/mo and payment fee schedule (assumed below)

## CRITICAL BUSINESS RISKS

1. **QA email bypass = unlimited paid usage for anyone who guesses `qa-test@toolhub.local`** (`subscriptions/services.py:25-41`, default in `config/settings/base.py:231`) — P0
2. **Budget guards are inert**: `record_provider_spend` has zero callers; `ProviderBudget` can never trip; ai_tools path never calls `spend_guard` — P0
3. **Manual retry re-queues with no new reserve** (`ai_tools/views.py:236-260`) — free re-execution loop — P0/P1
4. **Pro $9.99 is underwater at heavy use**: break-even provider cost ≈ $0.0148/credit (ASSUMPTION-derived); full 500cr burn at $0.02/credit = −26% margin
5. **Unlimited daily + inert guards + free retry** = uncapped worst-case exposure formulas (see Worst-Case Exposure)

---

# Executive Summary

ToolHub-AI's platform grew from ~12 to 36 tools, but pricing still reflects the old shape: paid plans effectively get 500 credits/mo by accident of a fallback, the pricing page advertises different numbers (300/5000), and three independent spending brakes (monthly budgets, spend guard on image path, QA scoping) are either unwired or bypassable. The credit engine itself is sound (reserve → finalize → refund), and 25 of 36 tools run at zero vendor cost (local/mock/CPU). Real money only moves on HuggingFace + Cloudflare paths.

The sustainable fix is not higher prices alone: (a) close the P0 money leaks, (b) make backend per-model cost the single source of truth, (c) set Pro at ~500 credits only if provider-$/credit stays under ~$0.015, otherwise cut allocation or raise price, (d) give Business pooled/seat-aware credits instead of flat 500, (e) sell credit packs priced off a $0.02 retail anchor. Until true provider USD is measured, every margin number below carries its assumption label.

# Current Pricing

VERIFIED from `seed_plans.py:53-112` + `subscriptions/models.py:21-64`; cards DB-driven (`pricing/page.tsx:32-68`):

| | Free | Pro | Business |
|---|---|---|---|
| Monthly | $0 | $9.99 | $29.99 |
| Yearly | — | $89.00 (true −25.8%, badge says 20% — wrong) | $299.90 (true −16.7%, badge says 20% — wrong) |
| Storage | 5 MB | 50 MB | 500 MB |
| Daily tool limit | 5 | Unlimited (−1) | Unlimited (−1) |
| Batch | 1 | 10 | 100 |
| API limit | 0 | 300 | 5000 |
| Monthly AI credits | 0 | 500 (fallback, NOT seeded) | 500 (fallback, NOT seeded) |
| Feature flags | basic_tools, ai_background_remove, ai_marketplace_resize | ~29 PRO_FEATURES keys | PRO + BUSINESS_EXTRA (fashion_model, ghost_mannequin, team, brand kit, priority) |

PARTIALLY VERIFIED gaps: `ai_text_to_image` missing from PRO_FEATURES (Pro users blocked from text-to-image as seeded); `ai_upscale`/`ai_enhance` Pro-only by seed omission though registry tier says free; `mockup`/`product-image` frontend path (`/image/*`) bypasses AI credit pipeline entirely (zero charge, Pillow sync).

# Current Credit Economy

Lifecycle (all VERIFIED): grant (renewal allocation `billing/services.py:174-175`, packs `subscriptions/services.py:248-253`, admin ` :256-261`, payment-refund `:219`) → reserve at enqueue (`ai_tools/services.py:59`, atomic) → finalize on success (`tasks.py:150,220`) → refund on failure/max-retry/cancel (`tasks.py:182,194,308`, `views.py:278-280`) and workspace equivalents (`gateway.py:367-374,437-456`). No signup bonus (stub signals — NOT FOUND). No rollover found (NOT FOUND — treat as non-rollover). Retry: Celery auto-retry reuses reservation (safe); manual retry does not re-reserve (P0 leak). QA/`-1` skips reserve (`services.py:220-221`, `entitlements.py:49`).

Per-op credit costs 1–4 (`registry.py:441-477`, fallback 2 at `:490`, env override `AI_CREDIT_COSTS_JSON` at `base.py:371-375`).

# Complete Tool Cost Matrix

Charge rule VERIFIED (`services.py:50`): `cost = model.cost_per_operation OR op fallback`. Per-request; reserve→consume→refund. DRF global limits `anon 10000/day, user 100000/day` (`base.py:244-252`); provider caps env-gated, default OFF (`limits.py:98-104`).

| # | Tool | Backend op | Serving models (provider class) | BE ¢ | FE ¢ | Paid-trigger? | Plan access |
|---|---|---|---|---|---|---|---|
| 1-7 | Pan/Resize/Crop/Social/Rotate/Compress/Convert | — (canvas/client) | — | 0 | 0 | No | Free |
| 8 | Watermark | `/image/watermark/` | Pillow, zero-credit | 0 | 0 | No | Free |
| 9 | Product | `product-image` BE 3† | Pillow sync (FE path) | 3† | 2† | No (FE path) | gated by image-tool perm |
| 10 | Mockup | `mockup` BE 4† | Pillow sync (FE path) | 4† | 2† | No (FE path) | gated by image-tool perm |
| 11 | BG Remove | `background-remove` 1 | hf-bria-rmbg (paid), local-rmbg/comfy/local/mock (zero) | 1 | 1 | Yes if HF key set | Free |
| 12 | Passport | `passport-photo` 1 | mock only | 1 | 1 | No | Exempt (any active plan) |
| 13 | Upscale | `upscale` 2 | comfy/local/mock (all zero) | 2 | 2 | No | Pro as seeded |
| 14 | Enhance | `enhance` 1 | local/mock (zero) | 1 | 1 | No | Pro as seeded |
| 15 | Object Remove | `object-remove` 2 | comfy/local/mock + cf-sd15-inpaint (paid) | 2 | 2 | Yes if CF creds | Pro |
| 16 | Generative Fill | `generative-fill` 3 | hf-qwen (paid), cf-flux/sd15 (paid), mock/local | 3 | 3 | Yes | Pro |
| 17 | BG Generate | `background-generate` 3 | hf-qwen/cf (paid), local/mock | 3 | 3 | Yes | Pro |
| 18 | Expand | `expand` 3 | local/mock (zero live) | 3 | 3 | No live | Pro |
| 19 | Relight | `relight` 2 | local/mock (zero) | 2 | 2 | No | Pro |
| 20-35 | Shadow/Recolor/Retouch/Text-to-Image/Marketplace/Staging/Photo/Fashion/Ghost/Flat/FashionRetouch/Infographic/SizeChart/Carousel/Social/Ad | 1–4 (table above) | local-deterministic (zero) except text-to-image (CF-only, paid) | =BE | =FE | text-to-image Yes; rest No | Free: marketplace-resize; Biz-only: fashion-model, ghost-mannequin; rest Pro |
| 36 | AI Studio | NO backend op — `/studio/sessions/` orchestration | n/a (per-step charges) | — | 0 | via steps | studio perms |

† FE/BE mismatch that is moot on the live path (Pillow, zero charge); bites only via `/ai/product-edit/`, `/ai/mockup-generate/`.

# Complete Model/Provider Cost Matrix

21 image models (`registry.py:10-390`): **ZERO-COST** = mock-bg-remove, mock-generative-fill, mock-expand, mock-relight (1–3cr), local-rmbg-u2net (1), local-deterministic (1), comfyui-local-{upscale,bg-remove,inpaint,face-restore} (1–2). **PAID** = hf-bria-rmbg (1), hf-qwen-image-edit (3), cf-flux-klein-9b (3), cf-flux-klein-4b (2), cf-sdxl-base (2), cf-sd15-img2img (2), cf-sd15-inpaint (2), cf-dreamshaper-8 (2), cf-sdxl-lightning (2), cf-leonardo-lucid-origin (3), cf-leonardo-phoenix (3). **DORMANT** = openai/stability adapters. **SUBSIDIZED (chat only)** = xKiro 7 models (no image wiring). **All USD bases: UNKNOWN** — need HF per-request $ (2 models) + CF Neurons/run (7 models).

# Current Margin Analysis

With C=500 VERIFIED, P=$9.99 VERIFIED, fee 2.9%+$0.30 ASSUMPTION, infra $2 ASSUMPTION: break-even provider cost = **$0.0148/credit Pro monthly** ($0.0104 yearly-dragged), **$0.0536 Business**. At assumed k=$0.01/credit: Pro heavy full-burn margin +24%, at k=$0.02: −26%. Business survives to k=$0.05 (+6.1%). Free user max exposure if reserve enforced: $0 (+$2 infra ASSUMPTION).

# Problems and Inconsistencies

P0: QA email bypass; inert budgets/spend-guard; free manual retry; Pro $9.99 underwater at heavy use. P1: `product-image`/`mockup` FE/BE mismatch; `??3` vs backend 2; `ai_text_to_image` missing from PRO_FEATURES; mock advertises caps it can't execute (guaranteed-fail routing); provider-fallback re-rating absent (charged expensive, served cheap or fails). P2: Save-20% badge, 300/5000 mislabel, stale `constants/plans.ts`, FAQ 50MB, triple denominators, Contact-Sales→checkout.

# Proposed Credit Economy

- **CREDIT_VALUE_USD (retail anchor) = $0.02/credit** (rounded $9.99/500 gross — VERIFIED-derived). Pack premium/discounts move around it, never below cost floor.
- **Cost envelope = $0.0075–$0.0113/credit** provider+infra at 60–40% margin; midpoint **$0.0094 at 50%** (ASSUMPTION). Any true provider k above ~$0.0148 loses money at full Pro burn.
- Canonical source: backend `cost_per_operation` + `AI_TOOL_CREDIT_COSTS`, served live via `GET /ai/capabilities/` (`views.py:289-327`); frontend `creditCost` becomes display-only estimate. Env override `AI_CREDIT_COSTS_JSON` stays the sole hot-knob.

# Proposed Free Plan

Free = unlimited access/sessions/projects/history/local ops (canvas, resize/crop/rotate/compress/convert/social/watermark, marketplace-resize) + zero-cost models only (mock/local/rmbg) + NO paid-provider access. No monthly paid credits (keep 0, VERIFIED-safe): max provider expense per free user = **$0 by construction**. Optional later: one-time 10-credit promo wallet (non-renewing) once budgets are wired. Daily-5 stays as abuse throttle.

# Proposed Pro Plan

Keep $9.99/$89 ONLY with 500 credits AND measured k ≤ ~$0.015; otherwise choose: (a) 300 credits at $9.99 (break-even k rises to ~$0.024), or (b) $14.99 for 500 credits. Include: 50MB upload, batch-10, full AI tools except Biz-gated fashion-model/ghost-mannequin, priority queue, history, 300 API calls; no rollover (monthly reset, failed-job auto-refund stays); packs available. Annual $89 kept only if k verified ≤ $0.010 (else raise to $99).

# Proposed Business Plan

$29.99 is credit-safe (headroom to k=$0.05) but same-500-credits-for-3×-price invites heavy abuse under inert guards. Propose: 1,500 pooled credits/mo, 500MB, batch-100, 5000 API, team seats (per-seat +$12, pooled cap), commercial license, priority processing, fashion-model/ghost-mannequin included, overage ONLY via packs (no auto-burn past pool). Per-seat pooling caps the "one account, ten teammates" liability.

# Proposed Credit Packs

Anchored $0.02 (ASSUMPTION-derived floor formula `Pmin=(C·k+0.30)/(0.971−m)`, I=0 one-time): S 200cr/$4.99 ($0.0249, +51% at k=$0.01), M 500cr/$11.99 ($0.024, +15.5% even at k=$0.02), L 1000cr/$18.99+gated-4cr-ops ($0.019, +42.9% at k=$0.01). Pack credits valid 12 months, monthly plan credits never roll over. Gate 4-credit ops (mockup/fashion-model/carousel) from packs or 2× charge until k is measured.

# Tool Credit Pricing Matrix

Keep backend 1–4 skeleton (it already differentiates), with corrections: text-to-image 2→3 floor (CF-only, guaranteed spend); product-image/mockup reconcile FE to BE (3/4) or move both fully into zero-credit Pillow path and delete BE keys; passport stays 1 (mock-only, zero cost — margin-positive by design); fashion-model/carousel stay 4 (heaviest composites). Canonical = backend; frontend reads capabilities API.

# Model-Aware Pricing

Adopt `charge = max(model.cost, op.cost) × R(resolution) × N(outputs) × Q(quality)`, rounded up, computed in `enqueue_ai_job` (`services.py:50`), re-rated on provider fallback (`tasks.py:89-97`, refund-difference if downgraded). Tiers: R ≤1024=1.0 / ≤2048=1.5 / >2048=2.0 (registry max_resolution caps exist); N from new `output_count` (default 1); Q 1.5× for quality_score ≥9 premium models. Estimates already read per-model cost (`GenerationPanel.tsx:218`) — no frontend change needed.

# Revenue vs Provider Cost Simulation

(Fee 2.9%+$0.30, infra $2 — ASSUMPTION; k=$0.01 base ASSUMPTION.) Free unused: −$2.00. Pro light (50cr): +$6.90/+69%. Pro heavy full-burn (500cr): +$2.40/+24%; worst (all 4-cr @k=$0.02): −$2.60/−26%. Business light: +$25.82/+86%; heavy: +$21.82/+73%; worst (k=$0.05): +$1.82/+6%. Retry multiplier ×(1+R), R≤2 auto + unbounded manual, not in table — multiplies provider rows.

# Break-Even Analysis

`Pmin=(C·k+I+0.30)/(0.971−m)`; `Cmax=(P·(0.971−m)−0.30−I)/k`. At k=$0.01/I=$2 (ASSUMPTION): Pro-500cr needs $15.50 @50% ($12.79 @40%) vs $9.99 actual — ~55% under; max safe credits at $9.99/50% ≈ **240cr**; Business-500cr needs $15.50 vs $29.99 — covered; max safe at $29.99 ≈ 1182cr. Minimum margin: floor 40%, target 50% (fat-tail provider cost + retries + fraud + yearly drag).

# Worst-Case Exposure

Per paid user today: 125–500 ops (500/4…500/1) → provider 125·p4…500·p1; ×3 with auto-retries; +unbounded manual retries at zero credits; QA accounts fully unbounded; Free bounded at 150 ops/mo only if reserve enforced. At assumed k=$0.02, one heavy Pro = $10 provider vs $9.40 net (×3 with retries = $30).

# Canonical Pricing Architecture

Single source: backend Plan/PlanPrice rows + `AI_TOOL_CREDIT_COSTS`/model `cost_per_operation` + `AI_CREDIT_COSTS_JSON` hot-override → served via entitlements + capabilities APIs → frontend renders API values only (pricing page, usage/billing, GenerationPanel, registries become views, `constants/plans.ts` deleted or codegen'd). Copy-lint CI bans `unlimited credit*`.

# Implementation Plan

P0 (financial correctness): narrow QA bypass (`subscriptions/services.py:25-41`); wire spend-guard + `record_provider_spend` in ai_tools + seed ProviderBudget rows; reserve on manual retry (`views.py:236-260`); explicit `monthly_credits` seeds; Stripe-ID format gate; Business button behavior. P1 (consistency): comparison table from API; delete/fix `plans.ts`; FAQ/usage/billing denominators; FE/BE cost reconciliation; mock cap trimming; Contact-Sales decision. P2 (UX/polish): wording pass (`Unlimited sessions, projects & local ops · Paid generations use credits`), GenerationPanel balance display, FAQ snapshot tests. Each item: review diff first; tests: entitlement matrix, budget-block e2e, retry-charge test, cost-contract test, checkout staging test.

# Unknowns / Required Inputs

1. HF $/request: `briaai/RMBG-2.0`, `Qwen/Qwen-Image-Edit-2511`. 2. CF Neurons/run: 7 `@cf/*` image models. 3. Intended Pro/Business `monthly_credits`. 4. Real Stripe price IDs in prod DB. 5. True infra $/user/mo + fee schedule. 6. xKiro quota terms. 7. ComfyUI operating cost/capacity.

# Final Commercial Model

$0 Free (metered-zero paid compute) → $9.99 Pro (500cr only if k≤$0.015 else 300cr/$14.99) → $29.99 Business (1,500 pooled + seats) → packs 200/$4.99, 500/$11.99, 1000/$18.99 → $0.02 anchor, ~50% target margin, model-aware multipliers, backend-canonical costs, wired budget guards, narrowed QA. Owner math per user: revenue − fees − measured provider − infra = retained profit; worst cases bounded by pools, not promises.
