# ToolHub-AI Pricing Update Audit

> READ-ONLY audit. No application source code modified, no database data changed, no pricing values changed, no fixes implemented.
> Source of truth = actual code/configuration cited per claim as `path:line-range` + symbol name.
> Labels used throughout: **VERIFIED FACT** (read in source) · **CURRENT BEHAVIOR** (traced code path) · **MISMATCH** (two sources disagree) · **ASSUMPTION / PREVIOUS WORKING MODEL** (unverified economics, never canonical) · **UNKNOWN / UNVERIFIED** (not found in repo) · **RECOMMENDATION** (direction only, not implemented).

---

## 1. Executive Summary

**Current pricing (seeded backend, VERIFIED FACT — `backend/apps/subscriptions/management/commands/seed_plans.py:53-112`):**
Free $0 · Pro $9.99/mo ($89.00/yr) · Business $29.99/mo ($299.90/yr).
Storage 5/50/500 MB · daily tool limit 5/unlimited/unlimited · batch 1/10/100 · `api_limit` 0/300/5000.

**Current credit architecture (VERIFIED FACT):**
Single working pool = `CreditWallet.ai_credits`, reserve-before-dispatch at enqueue, mark-consumed on success, refund on failure/cancel.
Renewal allocation reads `plan.features['monthly_credits']` with a **500-credit fallback** — and Pro/Business seeds **omit `monthly_credits` entirely**, so both paid plans effectively allocate **500 by accident of fallback**, not by design.
`api_credits` (wallet column) is **never consumed by any AI execution path** — it is a parallel, unwired concept.
`monthly_credits` (plan feature key) vs `api_credits` (wallet column) are **separate, unreconciled concepts**; only `monthly_credits → ai_credits` does anything at runtime.

**Current source of truth:** there isn't one. Prices live in `seed_plans.py` (stale after first seed because it uses `get_or_create` and never updates), plan/price rows in DB, feature flags in `Plan.features` JSON, credit costs in `ai_tools/registry.py` (`AI_TOOL_CREDIT_COSTS` + per-model `cost_per_operation`), display-only copies in `frontend/src/constants/plans.ts`, `toolRegistry.ts`, `tools.ts`, and hardcoded strings in `pricing/page.tsx`. No sync mechanism exists between any of these.

**Major mismatches (all VERIFIED, details in §11):**
1. Frontend `plans.ts` (Free daily 10 / Pro storage 100 MB / Pro api 1000 / Pro aiCredits 100) disagrees with seed (5 / 50 MB / 300 / 500-fallback) on 4+ values, and has no Business plan at all.
2. Pricing page "Save 20%" badge is mathematically wrong for both paid plans (actual: Pro −25.8%, Business −16.7%).
3. Pricing page comparison table is hardcoded and claims "Priority Support" checkmarks with no backend feature key, and "300/5000 Credits/mo" (api_limit) while the real AI allocation is the 500-fallback.
4. Free seed omits `ai_access`, so as seeded, Free users fail the `ai_access` gate in `enqueue_ai_job` — contradicting the UI's "AI Background Remove" Free bullet.
5. `PRO_FEATURES` omits `ai_text_to_image`, `ai_inpaint`, `ai_face_restore` although `OPERATION_REGISTRY` defines those operations — Pro as seeded cannot use text-to-image despite the registry tier saying "pro".
6. Batch endpoint enforces `settings.AI_BATCH_MAX_IMAGES` (env, default 20), never `plan.batch_limit` — Pro 10 / Business 100 limits are display-only.
7. FAQ advertises credit top-ups; no credit-pack purchase path exists (method exists, zero callers).

**Major risks:**
- Manual job retry re-executes with **no new credit reservation** (free retry loop).
- `record_provider_spend` has **zero callers** — `ProviderBudget` can never accrue, spend guard on the image path is never invoked ("Implemented but not operationally connected").
- Seed commands never update existing rows — any future pricing change deployed via re-seed silently no-ops.
- New signups get 5 AI credits but **no Subscription row is auto-created** (signals/tasks are stubs) — `enqueue_ai_job` raises "No active subscription plan" for plan-less non-QA users, so the signup bonus may be unspendable.
- QA bypass matches on email alone (`QA_USER_EMAIL` default `qa-test@toolhub.local`) in addition to the DB flag.

**What should be updated first:** establish one canonical billing source of truth (backend), make seeds idempotent-updating, wire `monthly_credits` explicitly per plan, close the retry/spend-guard leaks, enforce `batch_limit` server-side, then and only then touch the Pricing UI and recalculate plan economics.

---

## 2. Current Pricing Snapshot

VERIFIED FACT — canonical seed values (`backend/apps/subscriptions/management/commands/seed_plans.py:53-112`, `seed_plans.Command.handle()`).
DB verification status: **NOT VERIFIED AGAINST LIVE DATABASE** (no live DB read performed; values below are what the seed *would* create on a fresh DB; existing rows are unaffected by re-seed — see §4).

| | Free | Pro | Business |
|---|---|---|---|
| Code | `free` | `pro` | `business` |
| Monthly price | $0.00 (amount 0) | $9.99 (amount 999) | $29.99 (amount 2999) |
| Annual price | — (no yearly row) | $89.00 (amount 8900) | $299.90 (amount 29990) |
| Storage limit | 5 MB (`5*1024*1024`) | 50 MB | 500 MB |
| Daily tool limit | 5 | −1 (unlimited) | −1 (unlimited) |
| Batch limit | 1 | 10 | 100 |
| `api_limit` (plan column) | 0 | 300 | 5000 |
| `features.monthly_credits` | 0 (explicit) | **absent** → 500 via fallback | **absent** → 500 via fallback |
| Feature flags | `basic_tools`, `ai_background_remove`, `ai_marketplace_resize` (+monthly_credits 0) | `PRO_FEATURES` (~28 keys, §10) | `PRO_FEATURES` + `BUSINESS_EXTRA` (team_features, brand_kit, saved_presets, priority_processing, usage_analytics, ai_fashion_model, ai_ghost_mannequin) |
| `ai_access` flag | **absent (False)** | True | True |

Actual annual discount (computed, §4): Pro −25.76% · Business −16.67%. Displayed badge: "Save 20%" — **MISMATCH both**.

---

## 3. Pricing UI Audit

### 3.1 Architecture: cards are DB-driven, everything else is hardcoded

VERIFIED FACT — `frontend/src/app/pricing/page.tsx:29-53` (`PricingPage.loadPlans` → `PaymentService.getPlans()` → backend `PlanListView`, serialized by `PlanSerializer` with nested `prices`).
Card price, storage (`formatStorage`, :117-121), daily/batch/api limits (:200-203), and feature bullets (`getFeatureList`, :123-137) render from the API response. **CURRENT BEHAVIOR:** card values track the DB, not constants.

The following are **hardcoded, backend-independent** strings in the same file:
- "Save 20%" badge (:159). No calculation; static text.
- Comparison table rows (:260-301): "5 times/day", "5 MB / 50 MB / 500 MB", "1 / 10 / 100 files", "300 / 5000 Credits/mo", Priority Support and Team Features checkmarks.
- FAQ top-up/refund/expiry claims (:315-330).
- `plan.code.toLowerCase() === 'business'` renders "Contact Sales" yet still calls checkout (:213) — label/behavior contradiction.

### 3.2 UI item table

| UI Item | Current Display | Backend Source | Actual Value | Match? | Enforcement | Status | Required Update |
|---|---|---|---|---|---|---|---|
| Free price | $0.00/month | `PlanPrice` (monthly, amount 0) | 0 | ✅ | N/A | OK | None |
| Pro price | $9.99/month | `PlanPrice` (999) | $9.99 | ✅ | Stripe checkout | OK | None (value) |
| Business price | $29.99/month | `PlanPrice` (2999) | $29.99 | ✅ | Stripe checkout | OK | None (value) |
| Free upload 5 MB | dynamic `storage_limit` | seed `5*1024*1024` | 5 MB | ✅ | **UNKNOWN** — no upload-size check found on AI endpoints (`AIImageUploadSerializer`; only mask 10 MB cap at `views.py:339`) | Unverified enforcement | Verify/add server-side upload cap per plan |
| Pro upload 50 MB | dynamic | seed 50 MB | 50 MB | ✅ | Same UNKNOWN | Unverified | Same |
| Business upload 500 MB | dynamic | seed 500 MB | 500 MB | ✅ | Same UNKNOWN | Unverified | Same |
| Free "5 Tools usage limit" (card) | dynamic `daily_limit` | seed 5 | 5 | ✅ | `UsageService.check_limit` — but **no caller found on AI job path** (`enqueue_ai_job` never calls it) | Display OK, enforcement gap | Wire daily-limit check into AI enqueue or remove claim |
| Free comparison "5 times/day" | hardcoded | seed 5 | 5 | ✅ | Same as above | Same | Same |
| Pro/Business "Unlimited Tools usage" | dynamic −1 → "Unlimited" + hardcoded table | seed −1 | −1 | ✅ | Same — unlimited daily, but AI ops still credit-limited | **Misleading wording** | Reword (see §12) |
| Batch 1/10/100 | dynamic `batch_limit` + hardcoded table | seed 1/10/100 | 1/10/100 | ✅ display | **NOT enforced** — `AIBatchCreateView` enforces only `AI_BATCH_MAX_IMAGES` (default 20) | Display-only | Enforce `batch_limit` server-side |
| "300 / 5000 API credits" | dynamic `api_limit` + hardcoded table | seed 300/5000 | 300/5000 | ✅ display | **Nothing consumes `api_credits`**; AI consumes `ai_credits` | Misleading | Clarify AI credits vs API credits; wire or relabel |
| Free bullet "AI Background Remove" | dynamic `ai_background_remove` flag | seed True | True (flag) | ✅ flag | **CONTRADICTED** — `enqueue_ai_job` requires `ai_access` (absent on Free) before per-tool check | Broken as seeded | Add `ai_access` to Free or change gate |
| Pro bullets (Background Remove, Upscale, Enhance, Object Remove, Bulk, Cloud History, High Res, API Access) | `getFeatureList` subset (11 keys) | `PRO_FEATURES` | flags True | ⚠️ partial | `has_feature` gates per op | **Stale subset** — hides ~17 other granted flags | Render full granted set or curated mapping |
| Comparison "Advanced AI Tools" ✗/✓/✓ | hardcoded | multiple flags | n/a | ⚠️ | per-op gates | Vague; Free actually has 1 AI flag | Replace with per-tool matrix |
| Comparison "Priority Support" ✗/✓/✓ | hardcoded | **no backend key** | n/a | ❌ | None — no `priority_support`/`support` key anywhere | Unimplemented claim | Remove or implement + entitle |
| Comparison "Team Features" ✗/✗/✓ | hardcoded | `team_features` (Business only) | Business True | ✅ | `ecommerce_studio/views.py:152` (brand_kit/team_features gate) | OK | Keep, verify copy |
| "Save 20%" badge | hardcoded | computed −25.8%/−16.7% | wrong both | ❌ | N/A | Wrong | Compute from prices or remove |
| FAQ "easily top up credits" | hardcoded | **no pack purchase path** | nonexistent | ❌ | N/A | False claim | Remove until packs exist |
| FAQ "Unused credits may be refunded…" | hardcoded | payment refund grants `refund_amount//100` AI credits (`billing/services.py:219`) | arbitrary formula | ⚠️ | exists but formula unprincipled | Misleading | Rewrite to actual policy |
| FAQ "Monthly credits expire…" | hardcoded | **no expiry/rollover job** (signals/tasks stubs) | unknown behavior | ⚠️ | None | Unverified | Implement or soften claim |

### 3.3 Stale relative to 36-tool product — VERIFIED FACT

`getFeatureList` (`pricing/page.tsx:123-137`) renders 11 labels. `PRO_FEATURES` grants ~28 flags and `OPERATION_REGISTRY` defines 27 operations (`registry.py:720-748`); `TOOL_REGISTRY` lists ~36 tools (`frontend/src/constants/toolRegistry.ts:66-471`). Pricing presents ~5 named AI tools (Background Remove, Upscale, Enhance, Object Remove + generic "AI Access"). The other ~20 AI operations (Generative Fill, Background Generate, Expand, Relight, Text-to-Image, Product Staging/Photography, Fashion Model, Ghost Mannequin, Flat Lay, Infographic, Size Chart, Carousel, Social/Ad Creative, Shadow, Recolor, Retouch, etc.) are invisible on pricing. **MISMATCH — pricing exposes a tiny subset.**

---

## 4. Backend Plan Configuration

### 4.1 Exact values — see §2 table (source `seed_plans.py:53-112`).

Price rows (`seed_plans.py:71-73, 87-90, 104-107`): Free monthly 0 USD; Pro monthly 999 / yearly 8900 with placeholder `provider_price_id` (`price_pro_monthly`, `price_pro_yearly`); Business monthly 2999 / yearly 29990 (`price_business_monthly`, `price_business_yearly`). Whether production Stripe IDs replaced these placeholders: **UNKNOWN / UNVERIFIED (NOT VERIFIED AGAINST LIVE DATABASE).**

Model: `Plan`/`PlanPrice` — `backend/apps/subscriptions/models.py:21-64`. `api_limit` help_text "API requests limit" (:36); `features` free-form JSON (:38).

### 4.2 `monthly_credits` vs `api_credits` — VERIFIED FACT, separate concepts, partially legacy

- `monthly_credits`: a **key inside `Plan.features` JSON**. Free sets 0 (`seed_plans.py:66`). Pro/Business **do not set it**. Consumed at exactly two places, both renewal paths: `billing/services.py:172-175` (`plan.features.get('monthly_credits', 500)`) and `billing/webhooks.py:187-188` (same `.get(..., 500)`). **CURRENT BEHAVIOR:** paid renewal grants **500 AI credits by fallback default**, not by configured plan value.
- `api_credits`: a **column on `CreditWallet`** (`models.py:128`) and a **column on `Plan`** (`api_limit`, `models.py:36`, seeded 0/300/5000). No code path debits `api_credits` or `CreditType.API` during AI execution — `reserve_credits` defaults to `CreditType.AI` (`services.py:214`) and all AI callers use the default. `api_limit` is read only for display and `can_use_api` gating.
- Conclusion: they are **accidental parallel concepts**. The AI credit system consumes **`monthly_credits → wallet.ai_credits`** only. `api_credits`/`api_limit` currently gate/display "API access" but have no consumption logic. **RECOMMENDATION:** decide whether API calls consume `api_credits` per-request or retire the column; document the chosen semantic before any UI copy.

### 4.3 Seed idempotency — VERIFIED FACT, update-never

`seed_plans.Command.handle()` (`seed_plans.py:111-143`) uses `Plan.objects.get_or_create(code, defaults={...})` and `PlanPrice.objects.get_or_create(plan, interval, currency, defaults={...})`. On existing rows it writes only `"Plan X already exists"` — **no field is updated**. Rerunning the seed **does not update** prices, limits, or features. Any pricing change requires a migration, admin edit, or a new upsert command. **P0-adjacent operational risk.**

For contrast, `seed_ai_models` does upsert descriptive fields while preserving operator customizations (`seed_ai_models.py` tail, `Command.handle`) — the plans seed has no equivalent.

---

## 5. Annual Pricing Audit

Computed from seed amounts (minor units). Frontend badge: static "Save 20%" (`pricing/page.tsx:159`). **Do NOT trust it — it is wrong.**

| Plan | Monthly | 12-Month Equivalent | Annual | Actual Discount | Displayed Discount | Match? |
|---|---|---|---|---|---|---|
| Pro | $9.99 (999) | $119.88 (12×999) | $89.00 (8900) | **−25.76%** (save $30.88) | 20% | ❌ understated by ~5.8 pts |
| Business | $29.99 (2999) | $359.88 (12×2999) | $299.90 (29990) | **−16.67%** (save $59.98) | 20% | ❌ overstated by ~3.3 pts |
| Free | $0 | $0 | — (no yearly row) | n/a | n/a | n/a |

**RECOMMENDATION:** compute the badge from `monthlyPrice`/`yearlyPrice` at render time (and handle Free's missing yearly row), or remove it.

---

## 6. Credit System Audit

### 6.1 Lifecycle (ai_tools path, CURRENT BEHAVIOR — VERIFIED)

1. **Request → entitlement:** `BaseAIToolView.post` / `AIOperationView.post` (`ai_tools/views.py:31-66, 126-169`) → `enqueue_ai_job` (`ai_tools/services.py:18-106`): auth check → active-plan check (:30-32) → `ai_access` gate (:34-35) → per-tool feature gate via `OPERATION_REGISTRY.feature` (:40-44; `passport-photo` exempt) → `select_model` (:46) → `cost = model.cost_per_operation or get_credit_cost(tool)` (:50) → `enforce_provider_limits` (:56).
2. **Reservation (pre-execution):** `CreditService.reserve_credits(user, cost, ref)` inside `transaction.atomic` (:58-59) → immediate debit `USAGE` transaction (`subscriptions/services.py:214-229`, `_apply_credit_change` :264-292). There is **no separate hold/finalize split** — "reservation" is an immediate deduction; `reserved_credits` is recorded on the job (:76) for later refund accounting.
3. **Dispatch:** Celery `process_ai_job` / `process_comfyui_job` (:90-98); `ProviderLimitService.record_usage` counts provider/model/cost rows (:98).
4. **Success:** `consumed_credits = reserved_credits` (`tasks.py:150-151`, comfy `:220-221`) + `AIImageVersion` row.
5. **Failure:** both `MaxRetriesExceededError` (:174-184) and generic exception (:186-196) set FAILED and **refund full `reserved_credits`** (`REFUND` transaction). ComfyUI failure refunds identically (:302-310).
6. **Cancellation:** `AIJobCancelView` (`views.py:263-284`) allows cancel unless completed/failed/cancelled and refunds `reserved_credits` (:278-282). No-op jobs (never dispatched due to broker failure) keep the debit with job left QUEUED (:100-105) — **reconciliation sweeper referenced in comment does not exist (UNVERIFIED/UNKNOWN).**

### 6.2 Feature matrix (VERIFIED from cited lines)

| Event | Credits consumed? | Refunded? | Evidence |
|---|---|---|---|
| Enqueue (per job) | Yes, upfront debit | — | `services.py:58-59` |
| Success | kept (`consumed=reserved`) | No | `tasks.py:150` |
| Provider failure, retries left | No extra (Celery retry reuses same reservation) | No | `tasks.py:137-140` |
| Final failure / max retries | — | Full refund | `tasks.py:182, 194` |
| Cancel (queued/processing) | — | Full refund | `views.py:278-282` |
| Cancel (completed/failed/cancelled) | rejected | No | `views.py:271-272` |
| Provider fallback within one attempt | No extra charge (same reservation) | — | `tasks.py:89-97` (+ params stamp :105-106) |
| **Manual retry (user clicks retry)** | **No new reservation** | — | `views.py:233-260` never calls `reserve_credits` |
| Batch item | per-item reserve via `enqueue_ai_job` | per-item refund if that item fails | `views.py:449-466` + lifecycle above |
| Partial batch failure | only failed items refund; successes keep | Partial | same |
| Batch enqueue exception (e.g. insufficient credits mid-batch) | earlier items keep debits, later items never created | No rollback of earlier items | `views.py:451-466` (no atomic wrapper, `failed_count+1` only) |
| QA user any op | No (bypass) | n/a | `subscriptions/services.py:220-221` |
| Signup bonus | +5 AI allocation | — | `authentication/services.py:58` (+Google :156, GitHub :258) |
| Renewal | +`monthly_credits` or 500 fallback | — | `billing/services.py:174-175`; `webhooks.py:188` |
| Payment refund | +`refund_amount//100` AI credits (integer division!) | — | `billing/services.py:219` |
| Admin grant | `admin_adjust_credits` / `add_allocation` | — | `services.py:240-261` |
| Credit-pack purchase | method exists, **zero callers** | — | `services.py:248-253` |
| Expiration / rollover | **none found** | — | TransactionType enum has `EXPIRATION` but no writer; signals/tasks stubs |
| Idempotent re-POST (same idempotency_key) | returns existing job, no double charge | — | `services.py:22-25` |
| Multi-image / resolution multiplier | **none** — 1 job = 1 flat cost regardless of MP/steps/output count | — | `services.py:50`; no dimension/step fields in cost math |

### 6.3 Manual retry free-execution — VERIFIED P0

`AIJobRetryView.post` (`views.py:233-260`): increments `retry_count`, resets to QUEUED, re-dispatches Celery — **without any `reserve_credits` call**. But the original failure path **already refunded** the credits (`tasks.py:182/194`). Net effect: retry executes fully free even for users with 0 balance, and `retry_count < max_retries` permits repeated free runs (bounded only by counter). **CURRENT BEHAVIOR: manual retry = free re-execution loop (up to max_retries per job, unlimited jobs).**

### 6.4 What the wallet actually tracks

`CreditWallet` has 5 columns (`models.py:122-131`); only `ai_credits` moves in the AI flows. `image_processing/pdf_processing/api/storage` columns are written only via generic service methods with no production callers found. `CreditTransaction` ledger (`models.py:152-162`, admin-visible) records every movement with `balance_after` — audit trail exists and is sound.

---

## 7. AI Operation Credit Costs

Canonical sources: per-model `cost_per_operation` (`registry.py:10-390`) wins; operation fallback `AI_TOOL_CREDIT_COSTS` (`registry.py:441-477`); env override `settings.AI_CREDIT_COSTS` from `AI_CREDIT_COSTS_JSON` (`config/settings/base.py:371-375`, default `{}` in `.env.example:63`); resolution rule `get_credit_cost` (`registry.py:480-490`, unknown op → 2).

Charge rule (VERIFIED): `cost = selected_model.get("cost_per_operation") or get_credit_cost(tool_name)` (`services.py:50`).

| Operation (registry key) | Current Credit Cost | Source | Model-Aware? | Resolution-Aware? | Batch-Aware? | Notes |
|---|---|---|---|---|---|---|
| background-remove | 1 | model cost (all bg-remove models = 1); fallback 1 | Partial — Bria HF and local both 1 | No | No (per job) | Paid HF path costs same as free local path |
| text-to-image | 2 | model 2–3 (flux-4b 2, flux-9b 3, leonardo 3, SDXL fam 2); fallback 2 | Partial | No | No | Flat display 2 hides 3-cost models |
| upscale | 2 | model (comfy 1! vs fallback 2) — **selected model wins, so comfy upscale charges 1, local/mock charge 1** | Yes (1 vs 2) | No | No | Model-dependent 1–2; display says 2 |
| enhance | 1 | model 1; fallback 1 | No variance | No | No | Consistent |
| object-remove | 2 | model 2 (comfy-inpaint 2, cf-inpaint 2, local-det 1!) | Partial — local-det charges 1 | No | No | 1–2 by routing |
| inpaint | 2 | fallback 2 (comfy-inpaint model 2) | No variance | No | No | `ai_inpaint` missing from PRO_FEATURES (§10) |
| face-restore | 1 | model 1; fallback 1 | No | No | No | `ai_face_restore` missing from PRO_FEATURES |
| passport-photo | 1 | fallback 1 | No | No | No | Entitlement-exempt; only op skipping per-tool gate |
| generative-fill | 3 | model 3 (Qwen 3, mock 3, cf 2–3); fallback 3 | Partial | No | No | Qwen $$$ = mock 3 |
| background-generate (+alias background-generation 3) | 3 | model 3 / cf 2–3; fallback 3 | Partial | No | No | Same |
| expand (+alias image-expansion 3) | 3 | model 3; fallback 3 | No | No | No | Consistent |
| relight (+alias ai-relight 2) | 2 | model 2; fallback 2 | No | No | No | Consistent |
| product-edit (+alias product-image 3) | 3 | fallback 3 | No registry op — reachable via generic `AIOperationView` only if `is_known_operation`… **it is NOT in OPERATION_REGISTRY** → generic endpoint rejects it; dedicated FE path is Pillow sync (0 charge) | No | No | Dead backend key + unbilled FE path |
| mockup (+`mockup-generate` 4) | 2–4 | `mockup` 4 / legacy FE id `product-image`/`mockup` display 2 | **MISMATCH** FE 2 vs BE 4 | No | No | FE Pillow path charges 0 in practice |
| shadow | 2 | fallback 2 (no model has explicit shadow cost; local-exec) | No | No | No | Local-only execution, still charged 2 |
| recolor | 2 | fallback 2 | No | No | No | Same |
| retouch | 2 | fallback 2 | No | No | No | Same |
| fashion-retouch | 2 | fallback 2 | No | No | No | Same |
| marketplace-resize | 1 | fallback 1 | No | No | No | Deterministic op charged 1 via AI pipeline; preset-preview sync path 0 |
| product-staging | 3 | fallback 3 | No | No | No | Same for all models |
| product-photography | 3 | fallback 3 | No | No | No | Same |
| fashion-model | 4 | fallback 4 | No | No | No | Highest tier cost |
| ghost-mannequin | 3 | fallback 3 | No | No | No | Business-only flag, pro-cost |
| flat-lay | 2 | fallback 2 | No | No | No | — |
| infographic | 3 | fallback 3 | No | No | No | — |
| size-chart | 2 | fallback 2 | No | No | No | — |
| carousel | 4 | fallback 4 | No | No | No | — |
| social-creative | 3 | fallback 3 | No | No | No | — |
| ad-creative | 3 | fallback 3 | No | No | No | — |
| ai-product-studio (FE id) | 0 display | **no backend op** — orchestrates 9 `enqueue_ai_job` steps | n/a | No | **9× per-step charges** (1+1+2+2+3+3+1+3+3 ≈ 19) | Display "0" hides ~19 credits |

Frontend/backend cost mismatches (VERIFIED): `tools.ts:155` passport 3 vs backend 1; `toolRegistry.ts` product-image 2 vs backend `product-image` 3; mockup 2 vs backend `mockup` 4 (and backend `mockup-generate` 4 vs no FE id); `plans.ts CREDIT_COSTS` covers only 5 legacy ops (bg-remove 1, upscale 2, enhance 1, object-remove 2, passport 3 — passport contradicts `tools.ts` 3? No: plans.ts says 3? It says `passport: 3` — matches tools.ts 3, contradicts backend 1 and toolRegistry passport 1). Three frontend files disagree with each other on passport (3 vs 1). `EditorToolbar.tsx:140-146` hardcodes yet another cost map; `FloatingContextBar.tsx:206` / `GenerationPanel.tsx:218` default `?? 3` when model unknown vs backend default 2.

Deterministic/client-side (0, no credits): pan, resize, crop, social, rotate, compress, convert, watermark (`toolRegistry.ts:67-146, 227-237` `requiresAi:false, creditCost:0`) — plus `marketplace-resize` paradox (requiresAi false yet creditCost 1) and `ai-product-studio` (requiresAi true, cost 0 display, per-step backend billing).

---

## 8. Model-Aware Credit Pricing

**Answer: B with a model-cost-wins twist — `cost = selected_model.cost_per_operation OR operation fallback` (`ai_tools/services.py:50`).** The selected model's flat cost wins; the operation table is only a fallback when the model has no cost. There is no resolution/step/count multiplier and no post-execution reconciliation to the model actually used.

**CURRENT BEHAVIOR consequences (VERIFIED):**
- Expensive models routinely execute for the same price as cheap ones: Bria RMBG (paid HF) = 1 = local U2-Net free (`registry.py:22, 126`); Qwen Image Edit (paid) = 3 = mock-generative-fill 3 (`:39, 74`); flux-klein-4b = 2 vs klein-9b = 3 (only 1-credit spread for very different provider cost); Leonardo Lucid-Origin/Phoenix = 3 = SDXL-Lightning 2-cost siblings for text-to-image.
- `select_model` prefers real providers (`_PROVIDER_RANK`, `registry.py:752`; `resolve_model_for_task` same) — so when HF/CF creds exist, paid models are picked first **at the flat model cost**, with nosurcharge vs local.
- Fallback execution (`tasks.py:89-97`) runs the fallback provider **under the original reservation** — a Qwen→mock or CF→local fallback costs the customer the original (higher) price for cheaper execution; the reverse (cheap→paid) cannot overcharge the customer but burns provider margin silently.
- `preferred_model_id` lets the caller pin any visible model at its flat cost — no premium for premium models.
- ComfyUI/local/mock (zero vendor spend) still charge 1–2 credits per op — pure margin by design, but undocumented.

**Business-model risk:** without per-model USD metering, the flat 1–4 table cannot track the ~25× verified provider-cost spread (flux-4b $0.0012 → lucid-origin $0.031, see prior chain audit). **RECOMMENDATION:** introduce model-resolved cost (resolution/step-aware) as the single source of truth before fixing allowances; do NOT just raise all costs.

---

## 9. Provider Cost Metering

### 9.1 What the image (ai_tools) path records — VERIFIED

Per job: `provider`, `model_id`, `input_width/height`, `output_width/height` (`models.py:139-146`; input dims extracted at `services.py:83-88`, output at `tasks.py:100-107`). Per-job `reserved/consumed_credits` (`models.py:155-156`). `ProviderLimitService.record_usage` writes counting rows (`limits.py:113-151`): `provider:<name>` (count 1), `model:<id>` (count 1), `cloud_cost` (reserved-credit units) — **credit units, not USD**. No `request_id`, no latency, no step/output-count/input-count/MP/token fields, no USD (actual or estimated) anywhere on `AIProcessingJob`/`AIImageVersion` (which stores only `credit_cost`).

### 9.2 What the chat (ai_workspace) path records — VERIFIED

`AiUsageRecord` has `input/output_tokens`, `image_count`, audio/video durations, `latency_ms`, `time_to_first_token_ms`, `estimated_cost_usd`, `actual_cost_usd`, `capability_category` (`ai_workspace/models.py:279-311`). `UsageMeter` writes records with `estimated_cost_usd` passthrough (`usage_meter.py:32-126`). `AiWorkspaceModel` carries `estimated_cost_usd` + `cost_policy.credits_per_message` (`models.py:182, 192-194`). Gateway checks spend-guard pre-flight (`gateway.py:317-321`) and records usage post-success (`gateway.py:400-411`, compare `:514-523`) — but **never sets `actual_cost_usd`** (grep: no writer outside migrations) and **never calls `record_provider_spend`**.

### 9.3 Verdict

There is **no runtime USD cost meter on either path**. Dimensions exist (tokens, image counts, estimated USD on chat; pixel dims + credit units on image) but nothing converts an execution into actual provider USD. `actual_cost_usd` is schema without writers. **A runtime cost meter does not exist.**

---

## 10. Provider Spend / Budget Guard

**Status: "Implemented but not operationally connected."**

- `ProviderBudget` model (`ai_workspace/models.py:314-333`) + full `spend_guard.py` API (`record_provider_spend`, `check_provider_budget`, `is_provider_restricted`, `reset_monthly_spend`) — VERIFIED implemented, with warning/restriction/emergency thresholds.
- `record_provider_spend`: **zero callers** in `backend/` (grep §evidence). Spend can never accrue; restriction flags can never trip organically.
- `check_provider_budget`: called **only** from chat gateway pre-flight (`gateway.py:319`) — never from the ai_tools image path (`services.py`/`tasks.py`/`views.py` contain no spend_guard reference). The image path — the only path that spends image-provider money — is entirely unguarded by budgets.
- Read-side wiring exists (`provider_registry.py:_budget_state` surfaces budget in health snapshots), and no budget rows are seeded by any command found (**UNKNOWN whether rows exist — NOT VERIFIED AGAINST LIVE DATABASE**; with no rows every check is a silent no-op by design, `spend_guard.py:112`).
- Separate, actually-wired protection: `ProviderLimitService` (request-count/cost-unit caps, env-gated, default OFF, local providers exempt — `limits.py:49, 98-104`) IS called pre-dispatch (`services.py:56`) and IS recorded post-dispatch (`services.py:98`). It limits counts, not USD.

---

## 11. Free / Local / Mock Model Business Cost

Classification from adapter code (VERIFIED — `is_configured`/`supports`/`process`):

| Model(s) | Class | Evidence | Quota / tracking |
|---|---|---|---|
| local-deterministic, local-rmbg-u2net | **local / zero vendor spend** (CPU Pillow/rembg; infra cost only) | `local_provider.py:22-23` always configured; `rembg_provider.py:34-35`; `limits.py:49` exempt | No quota; untracked cost |
| mock-* (bg-remove, generative-fill, expand, relight) | **mock / test-only** (Pillow stubs; only 5 ops actually execute — `mock.py:15-32` raises `unsupported_operation` otherwise, despite registry advertising 11 capabilities on mock-bg-remove) | `mock.py:12-13` | No quota |
| comfyui-local-* | **local / zero vendor spend** (self-hosted ComfyUI; gated on `COMFYUI_ENABLED`, default false — `settings/base.py:385`; `.env.example:130`) | `comfyui_provider.py:40-41` | Concurrency-1 lock; untracked $ |
| hf-bria-rmbg, hf-qwen-image-edit | **paid provider** (HuggingFace inference; gated on token — `huggingface.py:65-66`) | adapter `is_configured` requires creds | Provider-side quota; app does not track HF balance |
| cf-* (9 models) | **paid provider, free-tier available** (Cloudflare Workers AI; gated on account+token — `cloudflare.py:111-112`) | adapter requires creds | CF 10k free neurons/day **shared per account** — app does not track neuron consumption; exhaustion affects all users at once |
| openai / stability adapters | **dormant** — `process()` raises not-implemented (`openai_provider.py:28-33`, `stability.py:16-19`); still selectable in theory | code | N/A |
| Official chat models (seed_ai_models) | mixed; seeded only when provider key env set | `seed_ai_models.py` gate logic | Per-provider terms — `EXTERNAL / NOT VERIFIED IN CODEBASE` |

Official provider USD pricing: **not present in the repository** — `EXTERNAL / NOT VERIFIED IN CODEBASE` (prior chain audit fetched 2026-09-20 externals; those numbers are **ASSUMPTION / PREVIOUS WORKING MODEL** until re-verified, see §17). The customer-facing credit system has no knowledge of free-tier quotas — a CF free-tier exhaustion surfaces as provider errors with credits refunded per failure, i.e., the business absorbs the outage while collecting nothing.

**Do NOT treat "free API" as zero cost:** local/comfy still consume CPU/infra; CF free tier is shared and exhaustible; HF free allowance is account-level. None is metered.

---

## 12. Frontend ↔ Backend Consistency

| Concept | Frontend Source | Backend Source | Runtime Source | Canonical? | Conflict? |
|---|---|---|---|---|---|
| Monthly prices | API-driven (DB) | `PlanPrice` rows from `seed_plans.py` | Stripe checkout `price_id` | DB (by rendering) | None on values; placeholder price IDs unverified |
| Annual prices | API-driven | `PlanPrice` yearly rows | Same | DB | "Save 20%" badge contradicts computed values |
| Monthly AI credits | `plans.ts aiCredits` (0/100, no Business) + pricing table "300/5000" (`api_limit`) | `features.monthly_credits` (0/absent/absent) + 500 fallback | renewal allocation | **None** — 3 disagreeing numbers | ❌ 100 vs 500 vs 300/5000 |
| API credits | `plans.ts limits.api` (0/1000) | `Plan.api_limit` (0/300/5000) | nothing consumes | Backend seed | ❌ 1000 vs 300 |
| Upload limits | API-driven display | seed 5/50/500 MB | no enforced check found | Seed (display) | Enforcement UNKNOWN |
| Daily usage | hardcoded table "5/Unlimited" | seed 5/−1/−1 | `UsageService` (not called on AI path) | Seed | Enforcement gap, not value conflict |
| Batch limits | API-driven + hardcoded table | seed 1/10/100 | `AI_BATCH_MAX_IMAGES`=20 env | Env (runtime) | ❌ plan limits display-only |
| Features | `getFeatureList` 11 labels | `PRO_FEATURES`+`BUSINESS_EXTRA` | `has_feature` gates | Backend flags | ❌ UI subset hides ~17 flags |
| AI tool costs | `toolRegistry` (36 ids) + `tools.ts` + `plans.ts CREDIT_COSTS` + `EditorToolbar` map + `?? 3` defaults | `AI_TOOL_CREDIT_COSTS` + model costs + `AI_CREDIT_COSTS_JSON` | `services.py:50` model-wins | Backend runtime | ❌ passport 3/1/1; mockup 2/4; product-image 2/3; default 3 vs 2 |
| Plan names/codes | `plan.code` from API | `Plan.code` unique | `get_active_plan` by status | DB | None |

**Source-of-truth RECOMMENDATION:** backend DB + `registry.py` cost rule; frontend must render API data only (cards already do; table/badges/FAQ/constants must follow).

---

## 13. Feature Access Audit

Seed flags: Free `{monthly_credits:0, basic_tools, ai_background_remove, ai_marketplace_resize}` (`seed_plans.py:65-70`); Pro `PRO_FEATURES` (`:86`); Business `PRO+BUSINESS_EXTRA` (`:103`).

| Feature/Tool (registry op → flag) | Free | Pro | Business | Backend Enforced? | Frontend Shown? | Mismatch |
|---|---|---|---|---|---|---|
| ai_access (global AI gate) | ❌ absent | ✅ | ✅ | Yes (`services.py:34`) — **blocks all Free AI incl. bg-remove** | "AI Access" shown on Pro/Business only | Free bullet contradicts gate |
| background-remove → ai_background_remove | ✅ flag | ✅ | ✅ | Yes | Free ✓ / Pro ✓ | Gate order defeats Free flag |
| text-to-image → ai_text_to_image | ❌ | ❌ **missing from PRO_FEATURES** | ❌ missing | Yes → Pro/Business **blocked** | Not shown | Registry tier "pro" unusable as seeded |
| upscale → ai_upscale | ❌ (registry tier free!) | ✅ | ✅ | Yes → Free blocked | Pro ✓ | Seed contradicts registry tier |
| enhance → ai_enhance | ❌ (tier free) | ✅ | ✅ | Yes → Free blocked | Pro ✓ | Same |
| object-remove → ai_object_remove | ❌ | ✅ | ✅ | Yes | Pro ✓ | OK |
| inpaint → ai_inpaint | ❌ | ❌ missing | ❌ missing | Yes → all blocked (generic endpoint 422-safe anyway) | Not shown | Dead op as seeded |
| face-restore → ai_face_restore | ❌ (tier free) | ❌ missing | ❌ missing | Yes → all blocked | Not shown | Dead op as seeded |
| passport-photo (exempt from per-tool gate) | ✅ effectively (any plan) | ✅ | ✅ | Only ai_access gate applies | Not on pricing | OK-ish; cost mismatch (§7) |
| marketplace-resize → ai_marketplace_resize | ✅ flag | ✅ | ✅ | Yes (generic endpoint) | Not on pricing | OK |
| shadow/recolor/retouch/flat/fashion-retouch/infographic/size-chart/carousel/social/ad/generative-fill/expand/relight/bg-generate/staging/photo | ❌ | ✅ | ✅ | Yes | Not on pricing (subset) | Pricing stale, enforcement OK |
| fashion-model / ghost-mannequin | ❌ | ❌ (Business-only) | ✅ | Yes | Not shown | OK enforcement; invisible packaging |
| bulk_processing | ❌ | ✅ | ✅ | Partial (`ecommerce views.py:87` for saved workflows; batch endpoint doesn't check) | Shown Pro/Business | Enforcement gap |
| cloud_history / high_resolution_export | ❌ | ✅ | ✅ | **No callers found** (`can_use_cloud_history`, `can_export_high_resolution` defined, never called in views) | Shown | Display-only flags |
| api_access | ❌ | ✅ | ✅ | `can_use_api` defined; no view caller found | Shown | Display-only |
| team_features / brand_kit / saved_presets / priority_processing / usage_analytics | ❌ | ❌ | ✅ | brand_kit/team checked (`ecommerce views.py:152`); rest no callers found | Only "Team Features" shown | Partially display-only |
| product-edit / mockup-generate (credit keys, no registry op) | n/a | n/a | n/a | Generic endpoint rejects (unknown op) | FE Pillow tools unbilled | Dead keys + unbilled path |

**New tools are NOT automatically included:** entitlement requires an explicit `ai_<op>` flag per plan; registry additions without seed/migration updates default-deny (except passport-photo exemption). Frontend/backend feature names also differ in form (`toolRegistry` ids use dashes like `bg-remove`; flags use `ai_background_remove`; `useSubscription.canUseAI` builds `ai_${name}` naively, which never matches underscore flags for dashed names).

---

## 14. "Unlimited Tools" Audit

**What it means in code:** `daily_limit = -1` → `UsageService.check_limit` returns True immediately (`subscriptions/services.py:312-316`); i.e., **no daily editor-operation cap**. That is the entire semantic. It does NOT mean unlimited AI: every AI job still passes `reserve_credits` against the finite `ai_credits` balance (Pro/Business ≈ 500-fallback + 5 signup). It does NOT mean unlimited batch (env cap 20) or unlimited file size.

**Enforcement trace:** daily counter (`UsageService.record`, `:319-334`) has no caller on the AI path (only `record_usage_type` for analytics-style `UsageRecord`s); the daily gate itself (`check_limit`) is likewise uncalled by `enqueue_ai_job`. So "Unlimited" is trivially true (nothing is counted), while the binding constraint on AI is credits.

**Verdict: potentially misleading customer-facing language.** A Pro user reading "Unlimited Tools usage" + FAQ "Regular tool usage remains unlimited" will not expect per-AI-op credit deductions against a ~500 pool. **RECOMMENDATION (wording only):** "Unlimited standard tools · AI tools use credits (X/mo included)" with a per-tool cost table link.

---

## 15. Batch / Retry / Fallback Billing

- **Max batch size per plan:** seeded 1/10/100 but **never read** by `AIBatchCreateView` (`ai_tools/views.py:413-471`). Runtime cap = `settings.AI_BATCH_MAX_IMAGES` (env `AI_BATCH_MAX_IMAGES`, default 20 — `settings/base.py:378`; `.env.example:99`). Free users can submit 20-image batches; Business users cannot submit 100. **MISMATCH — plan batch limits unenforced.**
- **Reservation per batch:** per-item `enqueue_ai_job` → per-item upfront debit. A 20-item batch at cost 3 reserves 30. Mid-batch exhaustion raises on later items; earlier debits stand; `failed_count` increments without refund (`views.py:464-466`).
- **Per-image charging:** yes (per job). No volume discount, no batch-level atomicity.
- **Model cost × image count:** yes implicitly (flat cost × N). No MP/step multiplier.
- **Partial failure:** failed items refund individually on terminal failure; successes keep charges. `AIBatchJob` counters (`completed/failed_count`) are informational; batch has no credit ledger of its own.
- **Retry:** auto Celery retry reuses reservation (safe); **manual retry free** (§6.3); batch children retry as single jobs under the same flaw.
- **Cancellation:** single-job cancel refunds; **no batch-level cancel** endpoint (batch detail is read-only, `views.py:474-490`); cancelling children one-by-one is the only path.
- **Fallback:** same-reservation execution, cost basis = originally selected model, never reconciled (§8).

---

## 16. Credit Packs / Overage / Rollover

- **Purchase additional credits:** NO. `CreditService.purchase_credits` exists (`services.py:248-253`, `TransactionType.PURCHASE`) with **zero production callers**; no pack model, no pack pricing, no checkout, no grant/expiry logic. Pricing FAQ "top up credits" is a **false claim**.
- **Monthly vs purchased distinction:** schema supports it (`ALLOCATION` vs `PURCHASE`), runtime never produces `PURCHASE` rows.
- **Rollover:** none found — no reset/expiry scheduled task (subscription/billing `signals.py`/`tasks.py` are stubs; no Celery beat entries for credits found); unused monthly credits neither expire (no `EXPIRATION` writer) nor roll (no carry logic). De facto behavior = **infinite accumulation** (each renewal adds; nothing subtracts except usage). Explicitly: **no rollover policy and no expiry enforcement exist.**
- **Purchased-credit expiry:** moot (no packs).
- **Overage without purchase:** impossible by construction (reserve raises `InsufficientCredits` → HTTP 402, `views.py:58-59`); except via QA bypass and manual-retry free execution.

---

## 17. Payment / Subscription Connection

- **Creation:** Stripe checkout (`BillingService.create_checkout_session`, `billing/services.py:84-115`) → `checkout.session.completed` webhook creates/updates `Subscription` + cancels prior actives (`webhooks.py:85-148`); `create_subscription_from_checkout` same pattern (`services.py:118-140`). Plan resolved via `Plan.provider_price_id == Stripe price_id` (`webhooks.py:120-124`) — placeholder IDs in seed must be replaced in prod (**UNVERIFIED**).
- **Renewal/credit timing:** `invoice.payment_succeeded` creates Payment+Invoice and allocates `monthly_credits`-or-500 (`webhooks.py:150-198`); the synchronous `record_successful_payment` path mirrors it (`services.py:143-177`).
- **Duplicate protection:** `WebhookEvent.get_or_create(event_id)` with processed-status short-circuit + payload-hash mismatch guard (`webhooks.py:42-56`) — sound. But `_handle_checkout_completed` swallows exceptions with log-only (`:146-147`), and invoice-success has **no idempotency on invoice id** — a redelivered `invoice.payment_succeeded` with a new event id would **double-allocate credits** (no dedupe on `reference sub_renewal_<invoice_id>`; reference includes invoice id but nothing checks it). **Partial duplication risk remains.**
- **Refunds:** `process_refund` requires COMPLETED, calls provider, then grants `refund_amount // 100` AI credits (`services.py:196-221`) — integer division ($9.99 → 9; $29.99 → 29), unprincipled conversion, and conceptually odd (cash refund + credit grant). No credit clawback on refund.
- **Failed payments:** `PAST_DUE` + failed Payment row (`services.py:180-193`, `webhooks.py:204-223`).
- **Cancel/expire:** `cancel_subscription` sets provider-side + `cancel_at_period_end` (`services.py:223-232`); `subscription.deleted/updated` webhooks map status (`webhooks.py:226-260`). No credit revocation on cancel/downgrade.
- **Plan change:** `upgrade_subscription`/`downgrade_subscription` swap `current.plan` immediately, no proration, no credit delta (`services.py:234-268`). Downgrade keeps previously granted credits; upgrade grants none until next renewal.
- **Annual/monthly:** distinguished only by `PlanPrice.billing_interval`; no interval-specific credit logic found.

---

## 18. QA / Test Account Behavior

Intentional test-mode exception — **not classified as a production pricing defect** as to its existence; scoping issues noted separately.

- **Detection:** `EntitlementService.is_qa` (`subscriptions/services.py:13-42`) = `user.is_qa_user` DB flag (`accounts` migration `0006`, `models.py`) OR email == `settings.QA_USER_EMAIL` (default `qa-test@toolhub.local`, `settings/base.py:231`, `.env.example:11`). Provisioned via `ensure_qa_user` command (idempotent, QA-only).
- **Credits bypassed:** yes — `reserve_credits` early-returns True (`services.py:220-221`); workspace `reserve` inherits it.
- **Tool/daily limits bypassed:** yes — `check_limit` True (`services.py:310-311`), `get_limit` −1 (`:94-95`), `has_feature`/`get_feature_value` True (`:78-90`), workspace tier MAX + unlimited daily/burst (`entitlements.py:22-23, 53-54, 65-66`), all registry models visible (`registry.py:531-532, 540`).
- **Provider costs still incurred:** yes — bypass is pre-provider; HF/CF calls execute and spend real money/quotas. No QA-specific spend accounting.
- **Usage recorded:** yes — `ProviderLimitService.record_usage` still writes `UsageRecord`s; gateway/`tasks.py` still write `AiUsageRecord`/versions. Presentational −1/∞ balances in `_qa_entitlement` (`subscriptions/views.py:97-154`) are not ledger writes, but analytics queries summing usage will include QA traffic.
- **Analytics risk:** QA usage is indistinguishable in `UsageRecord`/`AiUsageRecord` (no QA flag on rows) — production dashboards can be polluted. **RECOMMENDATION:** tag QA usage rows or exclude by user flag in analytics; narrow email-match bypass to non-production or require the DB flag.

---

## 19. Current 36-Tool Product Alignment

Counts (VERIFIED): `OPERATION_REGISTRY` = 27 ops (`registry.py:720-748`); `TOOL_REGISTRY` ≈ 36 entries (`toolRegistry.ts:66-471`); 21 image models (`registry.py:10-390`); ~45 frontend tool routes (§evidence `tools/` listing).

Pricing names 5 AI capabilities (Background Remove, Upscale, Enhance, Object Remove, "AI Access"). Unmentioned on pricing yet live behind credit gates: Generative Fill, Background Generate, Expand, Relight, Text-to-Image, Shadow, Recolor, Retouch, Marketplace Resize, Product Staging/Photography, Fashion Model, Ghost Mannequin, Flat Lay, Fashion Retouch, Infographic, Size Chart, Carousel, Social/Ad Creative, Face Restore, Inpaint, Passport Photo. **Pricing exposes roughly a fifth of the AI surface.**

Additional alignment gaps: `ai-product-studio` (flagship guided flow, 9 credit-bearing steps, ~19 credits/run) appears nowhere in pricing/packaging; `product-image`/`mockup` frontend tools run on an unbilled Pillow path while backend holds dead/expensive credit keys for the same names; `marketplace-resize` is simultaneously "no-AI" (registry flag) and credit-charged.

---

## 20. Important Business-Model Rule

The following values, wherever they appear in prior docs or this audit's math, are **ASSUMPTION / PREVIOUS WORKING MODEL** — NOT verified facts, NOT canonical pricing, NOT to be silently promoted:

- $0.02 retail value per credit; $0.0094 provider+infra budget per credit; 50% margin; assumed Stripe fees (2.9% + $0.30); assumed infra $2/user/mo; `USD_PER_CREDIT = $0.001` analytics rate (`cost_engine.py:36` — VERIFIED present in code, but its economic validity is ASSUMED).
- External provider USD figures in `PROVIDER_OPERATION_CREDIT_PRICE_CHAIN.md` (fetched 2026-09-20) — treat as point-in-time externals requiring re-verification, never as repo truth (repo holds no USD prices).
- Any Pro/Business `monthly_credits` recommendation (300/5000 dita are `api_limit`, 100 is a stale frontend constant, 500 is a code fallback) — **no final allowance is decided here**; allowances must derive from measured provider cost → model cost → operation cost → credit cost → plan margin (§22.10).

---

## 21. Previous Audit Reconciliation

Existing files (VERIFIED present): `PRICING_BUSINESS_MODEL_AUDIT.md`, `PROVIDER_MODEL_COST_LIMIT_AUDIT.md`, `PROVIDER_OPERATION_CREDIT_PRICE_CHAIN.md`, `PROJECT_CONTEXT.md`, `docs/11-payment-subscription-architecture-v2.0.md`, `frontend/AGENTS.md`.
Missing (VERIFIED absent): `RUNTIME_COST_METERING_AUDIT.md`, `FINAL_BILLING_IMPLEMENTATION_PLAN.md`, root `AGENTS.md`. (Untracked helper dumps `toolhub_pricing_cost_audit_*.txt/.md` exist but are not repo audits.)

| Previous finding | Current state | Class |
|---|---|---|
| Plans DB-driven, seed `get_or_create` never overwrites; Free 0/0cr/5MB/d5 · Pro 9.99/89 · Business 29.99/299.90 | Re-verified identical (`seed_plans.py:111-143`) | **STILL TRUE** |
| Paid allocation effectively 500 via fallback; seeds omit `monthly_credits` | Re-verified (`billing/services.py:174`, `webhooks.py:188`) | **STILL TRUE** |
| Reserve→finalize→refund lifecycle sound | Re-verified; "finalize" is mark-consumed, no two-phase hold | **STILL TRUE** (refined) |
| 21 image models, costs 1–4; zero-spend set {mock,local,rmbg,comfy} | Re-verified (`registry.py`, `limits.py:49`) | **STILL TRUE** |
| No USD provider prices in repo | Re-verified (none found) | **STILL TRUE** |
| Frontend `product-image` 2 vs BE 3; `mockup` 2 vs 4; `?? 3` vs default 2 | Re-verified + extended (passport 3-way split, EditorToolbar 4th map) | **STILL TRUE** (worse) |
| QA email bypass unlimited | Re-verified (`services.py:25-41`); now with `ensure_qa_user` + DB flag as primary | **PARTIALLY FIXED** (flag primary, email fallback remains) |
| `record_provider_spend` zero callers; spend guard unwired on image path | Re-verified (no new callers) | **STILL TRUE** |
| Manual retry without reserve | Re-verified (`views.py:233-260`) | **STILL TRUE** |
| "Save 20%" badge wrong (Pro −25.8%, Business −16.7%) | Re-verified by computation | **STILL TRUE** |
| `ai_text_to_image` missing from PRO_FEATURES | Re-verified (+ `ai_inpaint`, `ai_face_restore` also missing) | **STILL TRUE** (broader) |
| Mock advertises 11 caps, executes 5; local 25 vs 22; dormant openai/stability | Re-verified (`mock.py:15-32`, `local_provider.py:25-33`) | **STILL TRUE** |
| Batch limits unenforced / batch-cap confusion | Now precisely: plan `batch_limit` unread; env cap 20 rules | **STILL TRUE** (clarified) |
| No signup bonus (prior "NOT FOUND") | **Contradicted:** +5 welcome credits found (`authentication/services.py:58,156,258`) | **NO LONGER TRUE** (bonus exists; spendability blocked by missing auto-subscription) |
| Chain-audit recommended credit costs (1–4 model-aware) | Code unchanged (flat table); recommendations never implemented | **NOT VERIFIED** as implementation (recommendations only, correctly unapplied) |
| Margin/break-even math ($0.0148/credit etc.) | No code basis; remains assumption | **ASSUMPTION / PREVIOUS WORKING MODEL** |

---

## 22. Issues by Priority

P0 = must fix before production billing changes · P1 = before public pricing update · P2 = important cleanup · P3 = optional.

| Priority | Issue | Evidence | Impact | Recommended Direction |
|---|---|---|---|---|
| P0 | Manual retry executes with no new reservation after failure already refunded | `ai_tools/views.py:233-260` (no reserve) + `tasks.py:182,194` (refund) | Free re-execution loop; balance never gates retries | Reserve (or verify balance ≥ cost) in retry endpoint before re-queue; or make failure-path refund conditional on retry |
| P0 | No-subscription users blocked despite signup credits; no auto-provisioning | `services.py:30-32` gate + stub `subscriptions/signals.py`, `tasks.py` + `authentication/services.py:58` bonus | New users cannot spend; support load; conversion dead-end | Auto-create Free subscription on signup (migration backfill for existing users) |
| P0 | Seed never updates — pricing/config changes silently no-op on deploy | `seed_plans.py:111-143` `get_or_create` + "already exists" | Stale prices/limits/features persist in prod indefinitely | Idempotent upsert (update changed fields) or versioned plan migrations |
| P0 | Provider spend unmetered; budget guard unwired on money path | `record_provider_spend` zero callers; no spend_guard import in ai_tools; `AiUsageRecord.actual_cost_usd` unwritten | Uncapped provider exposure; budgets decorative | Record actual/estimated USD per job + call spend guard pre/post on image path |
| P1 | Free `ai_access` absent blocks the one AI tool Free advertises | `seed_plans.py:65-70` vs `services.py:34-35` | Free tier AI fully broken as seeded | Add `ai_access` (+ intended free-op flags) to Free seed |
| P1 | `ai_text_to_image`/`ai_inpaint`/`ai_face_restore` missing from paid seeds | `seed_plans.py:7-46` vs `registry.py:722,726,727` | Paid users 403 on live ops; text-to-image packaged nowhere | Add missing flags to PRO_FEATURES (or consciously tier them) |
| P1 | Plan `batch_limit` unenforced; env cap 20 rules for all | `views.py:413-471` ignores `batch_limit`; `settings/base.py:378` | Free over-served; Business under-served vs promise | Enforce `min(batch_limit, AI_BATCH_MAX_IMAGES)` + per-item atomicity |
| P1 | "Save 20%" badge wrong both plans | `pricing/page.tsx:159` vs computed −25.8%/−16.7% | False advertised discount | Compute from live prices |
| P1 | `monthly_credits` absent on paid plans; 500 fallback is the real allowance | `seed_plans.py:86,103` vs `billing/services.py:174`, `webhooks.py:188` | Allowance by accident; cannot price margin deliberately | Set explicit per-plan values (after cost metering), remove fallback reliance |
| P1 | `api_credits`/`api_limit` charged nowhere; "300/5000 Credits/mo" sells AIR | No `CreditType.API` debit in ai_tools/workspace paths | Users buy numbers with no consumption semantic | Define API-credit consumption or relabel to AI credits |
| P1 | Invoice redelivery can double-allocate renewal credits | `webhooks.py:150-198` no invoice-id dedupe | Double spendable balance per redelivery | Dedupe on provider invoice id / unique reference |
| P1 | Payment-refund credit formula (`//100`) arbitrary | `billing/services.py:219` | $9.99→9cr windfall/penalty noise; refund+grant double benefit | Define refund↔credit policy (clawback vs grant vs none) |
| P1 | Upgrade/downgrade move plan with no credit adjustment | `billing/services.py:234-268` | Downgrade keeps paid credits; upgrade grants none | Prorate/grant/revoke policy + tests |
| P1 | "Unlimited Tools" + top-up FAQ mislead on credit-limited AI | `pricing/page.tsx:201,263,321` | Expectation gap; dispute risk | Reword + link per-tool cost table; remove top-up claim |
| P2 | Seven disagreeing credit-cost copies (registry, toolRegistry, tools.ts, plans.ts, EditorToolbar, `??3`, backend default 2) | §7 table | Display/charged divergence; support confusion | Single API-served cost (capabilities endpoint already returns `credit_cost`) |
| P2 | `getFeatureList` hides ~17 granted flags; comparison table hardcoded | `pricing/page.tsx:123-137, 260-301` | Paid features invisible; table drifts from DB | Render granted flags (curated labels) for cards; DB-drive table |
| P2 | Priority Support / cloud_history / high_res / api_access flags display-only | No backend key / no callers | Selling unimplemented benefits | Implement+gate or remove from UI |
| P2 | Batch partial-failure non-atomic; no batch cancel | `views.py:449-471`; no batch-cancel view | Confusing charges; no bulk abort | Atomic batch reserve or itemized preview + batch cancel with refunds |
| P2 | Broker-down jobs keep debit with no sweeper | `services.py:100-105` comment references nonexistent reconciliation | Paid-for-nothing on infra outage | Requeue sweeper or reserve-after-dispatch |
| P2 | QA email-match fallback widens bypass; QA traffic pollutes analytics | `services.py:33-41`; no QA flag on usage rows | Guessed-email free riding (if email known); dirty metrics | Flag-primary only in prod; tag QA usage rows |
| P3 | Model-cost spread too flat (paid ≈ free per op) | `registry.py` costs vs §8 | Margin leakage on expensive models | Model/resolution-aware pricing (post-metering) |
| P3 | Workspace `CREDIT_COSTS`/`cost_policy` economy separate from image economy | `cost_engine.py:21-32`, `credits_per_message` | Two credit meanings, one wallet | Unify or explicitly document dual economy |
| P3 | `USD_PER_CREDIT=$0.001` analytics rate vs $0.02 working assumption | `cost_engine.py:36` | Internal reporting inconsistency | Single documented internal rate |
| P3 | Placeholder Stripe price IDs in seed | `seed_plans.py:88-89,105-106` | Checkout mismatch if deployed unedited | Resolve/verify against Stripe dashboard |
| P3 | `product-image`/`mockup` dead backend keys + unbilled FE paths | §7, §13 | Ledger blind spots | Unify operation ids end-to-end |

---

## 23. Required Updates

### Backend
- Upsert-capable plan seed (or migration-managed plans); explicit `monthly_credits` per paid plan; add `ai_access` to Free; add `ai_text_to_image`/`ai_inpaint`/`ai_face_restore` (decision: Pro vs Business); replace placeholder Stripe price IDs (verify).
- Reserve-or-check in `AIJobRetryView`; enforce `batch_limit` (`min(plan, env)`); atomic batch reservation or itemized pre-check; batch cancel endpoint with refunds.
- Per-job provider USD recording (`actual/estimated_cost_usd`, request id, latency, steps/MP/output count) + `record_provider_spend` after success + `check_provider_budget` pre-dispatch on image path.
- Invoice-idempotent renewal allocation; refund↔credit policy (replace `//100`); upgrade/downgrade credit policy; renewal/expiry/rollover policy with scheduled job (or explicit never-expire + never-roll documented).
- Credit-pack model + checkout + grant/expiry (or remove FAQ claims); `api_credits` semantic (consume or retire).
- Auto-provision Free subscription on signup + backfill; broker-failure sweeper; QA usage tagging.
- Wire or remove display-only gates (cloud_history, high_res_export, api_access, bulk on batch, priority/usage_analytics/saved_presets).

### Frontend
- Remove/hard-fix: "Save 20%" (compute), hardcoded comparison table (DB-drive), Priority Support checks, top-up/refund/expiry FAQ claims, "Contact Sales"-that-checks-out.
- Unify cost displays to the capabilities API (`credit_cost` per op + `cost_per_operation` per model); delete `plans.ts` stale values (or regenerate from API); reconcile passport/product-image/mockup numbers; replace `?? 3` defaults with served values.
- Expand pricing feature bullets beyond 11 labels; add per-tool cost visibility; reword "Unlimited Tools usage" (§14); surface AI Studio pipeline cost (~19 credits).

### Database
- Plan/price corrections via migration (not re-seed) given update-never seed; `monthly_credits` backfill; Stripe price-id resolution (verify live rows — **NOT VERIFIED** here).
- Optional: unique constraint on renewal reference to enforce idempotency; QA flag on usage records; pack/ledger tables if packs ship.

### Credit System
- Single documented semantic: upfront-debit-as-reservation (rename or implement true hold/finalize if two-phase needed); fix retry path; define expiry/rollover/pack/overage explicitly; align `monthly_credits` vs `api_credits`; unify or document dual image/workspace economies.

### Provider Metering
- Actual-cost capture per execution on both paths; neuron/token/step/MP dimensions plumbed into cost math; `ProviderBudget` rows seeded + reset cadence; dashboard/alerting on thresholds.

### Pricing UI
- DB-driven cards (keep) + computed discount + DB-driven comparison + full (curated) feature set + cost-per-tool + honest Free tier + Studio packaging. No new prices/allowances until §24.10 completes.

### Analytics/Admin
- Exclude/tag QA traffic; surface wallet ledger + per-model cost + provider spend vs budget in admin; plan-economics dashboard (credits granted vs consumed vs provider $) before finalizing allowances.

### Tests
- Seed idempotency; renewal fallback vs explicit; retry-no-free-ride; batch-limit enforcement; fallback same-charge; cancel/refund ledger balance; webhook redelivery single-allocation; upgrade/downgrade invariants; free-gate matrix (all 27 ops × 3 plans); UI/API value parity.

---

## 24. Recommended Implementation Sequence

Do NOT implement yet. Safest order only:

1. **Establish canonical billing source of truth** — backend DB + `registry.py` cost rule; freeze frontend constants as derived, not authored.
2. **Fix runtime cost metering** — per-execution provider USD capture (image + workspace), dimensions (tokens/MP/steps/counts), `ProviderBudget` rows + reset.
3. **Fix credit/model pricing relationship** — model/resolution-aware cost resolution; reconcile dead keys (`product-edit`, `mockup` variants); unify display copies to served API.
4. **Fix retry/fallback/batching billing safety** — retry reservation, fallback reconciliation policy, `batch_limit` enforcement, atomicity, batch cancel, broker-failure sweeper.
5. **Fix plan/entitlement consistency** — Free `ai_access`, missing paid flags, display-only gates (implement or remove), auto-provision Free subscriptions, signup-bonus spendability.
6. **Fix frontend/backend pricing synchronization** — computed discounts, DB-driven table, truthful FAQ, cost-per-tool surfacing, "Unlimited" rewording, Studio packaging.
7. **Update Pricing UI** — only after 1–6 hold.
8. **Add billing tests** — ledger invariants, idempotency, gates matrix, parity checks.
9. **Recalculate plan economics** — measured provider $ → model $ → op credits → allowance → price → margin (assumptions re-verified, not inherited).
10. **Only then finalize credit allowances** — set explicit `monthly_credits` per plan; remove fallback reliance; launch packs/overage deliberately.

---

## 25. Open Questions / Unknowns

1. Live DB plan/price/feature values (NOT VERIFIED AGAINST LIVE DATABASE) — incl. whether placeholder Stripe IDs were replaced.
2. Intended Pro/Business `monthly_credits` (500 fallback vs 300/5000 `api_limit` vs 100 frontend constant — which, if any, is the business intent?).
3. Intended semantic of `api_credits`/`api_limit` (per-API-call debit? separate pool? legacy?).
4. Intended Free AI scope (which ops? is `ai_access` omission deliberate?).
5. Tiering intent for `text-to-image`/`inpaint`/`face-restore` (Pro vs Business vs free?).
6. Rollover/expiry/overage policy intent (accumulate-forever is current de facto, not a decision).
7. Credit-pack intent (denominations, pricing, expiry) — FAQ promises vs zero implementation.
8. Refund↔credit policy (grant/clawback/none) and upgrade/downgrade proration.
9. Actual provider USD per model (EXTERNAL / NOT VERIFIED IN CODEBASE) + CF neuron consumption per op + HF spend attribution.
10. Real infra $/user/mo + Stripe fee schedule (assumed inputs, unverified).
11. Upload-limit enforcement intent (no server check found — client-only?).
12. Daily-limit intent on AI path (`check_limit` unwired — deliberate?).
13. Batch accounting intent (atomic vs best-effort) + Business 100 vs env 20 conflict resolution.
14. QA email-fallback acceptability in production.
15. Workspace vs image credit-economy unification intent.
16. `USD_PER_CREDIT` $0.001 vs $0.02 working assumption — which rate governs reporting?
17. Whether `image_tools`/Pillow sync paths should enter the credit ledger.
18. AI Studio per-pipeline packaging (flat fee vs sum-of-steps vs subscription-only).

---

## 26. Final Verdict

- **Pricing UI ready?** No — cards are sound (DB-driven) but badge, comparison table, feature subset, and FAQ contain false/unverifiable claims; constants files contradict the backend.
- **Backend plans ready?** No — values exist but seeds never update, paid `monthly_credits` missing (fallback-dependent), Free/paid flag sets have blocking omissions, Stripe IDs unverified.
- **Credit system ready?** Partially — reserve/consume/refund ledger core is sound and well-instrumented, but manual retry, batch atomicity, pack/overage/rollover/expiry, and API-credit semantics are missing or broken.
- **Provider cost metering ready?** No — no runtime USD capture on either path; dimensions partial; `actual_cost_usd` unwritten.
- **Model-aware pricing ready?** No — flat model-cost-wins with no resolution/step/count awareness; expensive≈cheap per op.
- **Spend protection ready?** No — budgets implemented but never fed or consulted on the image money path; count-based limits exist but default OFF.
- **Ready to finalize customer credit allowances?** **No.** Allowances must wait for metering (sequence §24.1–24.9) and explicit business decisions (§25). No Pro/Business credit amount is set here.

---

## Audit Metadata

- **Audit date:** 2026-09-20 (UTC)
- **Git branch:** `main`
- **Git commit:** `240e08af4de071a905181d6a41f0cd84eee0e0f8`
- **Repository state:** clean except pre-existing `modified: .env.example` (not touched by this audit); untracked prior-audit dumps present (`PRICING_BUSINESS_MODEL_AUDIT.md`, `PROVIDER_MODEL_COST_LIMIT_AUDIT.md`, `PROVIDER_OPERATION_CREDIT_PRICE_CHAIN.md`, `toolhub_pricing_cost_audit_*.txt/.md`)
- **Files inspected (primary):** `frontend/src/app/pricing/page.tsx`, `frontend/src/constants/plans.ts`, `frontend/src/constants/toolRegistry.ts`, `frontend/src/constants/tools.ts`, `frontend/src/hooks/useSubscription.ts`, `frontend/src/components/editor/{EditorToolbar,FloatingContextBar,GenerationPanel}.tsx`, `backend/apps/subscriptions/{models,services,views,serializers,admin,management/commands/seed_plans}.py`, `backend/apps/ai_tools/{registry,services,tasks,views,models,limits}.py` + `providers/{mock,local_provider,rembg_provider,huggingface,cloudflare,openai_provider,stability,comfyui_provider}.py`, `backend/apps/ai_workspace/{gateway,credits,cost_engine,entitlements,spend_guard,usage_meter,provider_registry,models,management/commands/seed_ai_models}.py`, `backend/apps/billing/{models,services,webhooks}.py`, `backend/apps/authentication/services.py`, `backend/apps/ecommerce_studio/{services,views}.py`, `backend/apps/accounts/management/commands/ensure_qa_user.py`, `backend/config/settings/base.py`, `.env.example`, `PROJECT_CONTEXT.md`, `PRICING_BUSINESS_MODEL_AUDIT.md`, `PROVIDER_MODEL_COST_LIMIT_AUDIT.md`, `PROVIDER_OPERATION_CREDIT_PRICE_CHAIN.md`
- **Database verification status:** NOT VERIFIED AGAINST LIVE DATABASE (static code/config inspection only; no DB reads/writes performed)
- **External provider pricing verification status:** NOT VERIFIED (no provider docs fetched in this audit; prior chain-audit externals treated as assumptions)
- **Whether source code was modified:** NO (only `PRICING_UPDATE_AUDIT.md` created; `git status` otherwise untouched)
