# Credit Pricing Safety Analysis — ToolHub-AI

> তারিখ: 2026-09-21 · সিদ্ধান্ত-সহায়ক বিশ্লেষণ, কোড/DB-এ কোনো পরিবর্তন নয়।
> Tags: **VERIFIED** = repo বা official pricing source থেকে নেওয়া · **ASSUMED** = লেবেলসহ অনুমান · **UNKNOWN** = পাওয়া যায়নি, বানানো হয়নি।
> Sources: `PROVIDER_OPERATION_CREDIT_PRICE_CHAIN.md` (rates verified 2026-09-20), `PRICING_BUSINESS_MODEL_AUDIT.md`, `backend/apps/ai_tools/registry.py`, `seed_plans.py`।

## 0. Economics basis

| Input | Value | Status |
|---|---|---|
| Retail anchor | $0.02 / credit ($9.99 ≈ 500cr) | VERIFIED-derived |
| Cost budget @50% margin | $0.0094 / credit | ASSUMED (audit midpoint) |
| Stripe fee | 2.9% + $0.30 | ASSUMED |
| Infra | $2 / user / mo | ASSUMED |
| Break-even formula | `Cmax = (P·(0.971−m) − 0.30 − I) / k` | audit §Break-Even |
| Net revenue (fee বাদে) | Pro **$9.40**, Business **$28.82** | গণনা |
| Provider-এর জন্য থাকে (infra বাদে) | Pro **$7.40**, Business **$26.82** | গণনা |

## 1. Pro $9.99 → সর্বোচ্চ নিরাপদ credits

Blended provider cost k = $0.01 ধরে (audit base assumption):

| Margin target | Max credits |
|---|---|
| 50% (target) | **~240 cr** |
| 40% (floor) | **~340 cr** |
| 0% (break-even, k=$0.0148 পর্যন্ত) | **~740 cr** |

**বর্তমান সিদ্ধান্ত (500 cr):** k=$0.01-এ margin **+24% (+$2.40)** — নিরাপদ, যতক্ষণ blended k **$0.0148**-এর নিচে থাকে। বাস্তবে ২৫/৩৬টি operation $0-তে serve হয়, তাই normal mix-এ blended k ≈ $0.001–0.003 → 500 খুবই নিরাপদ। ঝুঁকি শুধু Qwen/Bria concentration (§4)।

## 2. Business $29.99 → সর্বোচ্চ নিরাপদ credits

| Margin target | Max credits (k=$0.01) |
|---|---|
| 50% | **~1,180 cr** |
| 40% | **~1,480 cr** |
| break-even (k=$0.018 পর্যন্ত) | ~2,680 cr |

**বর্তমান সিদ্ধান্ত (1500 cr):** 50%-লাইনের সামান্য উপরে, 40%-লাইনের ভেতরে। k=$0.01-এ margin ≈ **+38% (+$11.80)**। নিরাপদ — একই শর্তে (ভারী Qwen concentration না হলে)।

## 3. প্রতিটি model → minimum safe credit cost

নিয়ম: `min_credits = ceil(USD_per_op / 0.0094)`। USD typical 1024×1024, single output (CHAIN-doc §2, VERIFIED):

| Model | Provider USD/op | Min safe | বর্তমান চার্জ | অবস্থা |
|---|---|---|---|---|
| hf-bria-rmbg (Bria RMBG 2.0) | $0.018 | **2** | 1 | 🔴 −$0.0086/op loss |
| hf-qwen-image-edit, 1MP | $0.030 | **4** | 3 | 🔴 loss |
| hf-qwen-image-edit, 2MP | $0.060 | **7** | 3 | 🔴🔴 বড় loss — resolution multiplier লাগবে |
| cf-flux-klein-4b (txt2img/edit) | $0.0012–0.0014 | **1** | 2 | 🟢 |
| cf-flux-klein-9b (txt2img/edit) | $0.015–0.017 | **2** | 2–3 | 🟢 |
| cf-sdxl-base (beta) | ~$0.00 | 1 | 2 | 🟢 |
| cf-sd15-img2img / inpaint, dreamshaper-8, sdxl-lightning | UNKNOWN (সম্ভবত $0) | 2 — প্রথম invoice-এ verify | 2 | 🟡 |
| cf-leonardo-lucid-origin (20 steps) | $0.031 | **4** | 3 | 🔴 −$0.003/op |
| cf-leonardo-phoenix-1.0 (20 steps) | $0.026 | **3** | 3 | 🟢 সমান-সমান |
| local / local-rmbg / comfyui_local / mock | $0.00 (own hardware) | যেকোনো | 1–4 | 🟢 pure margin |

## 4. প্রতিটি operation → কোন model serve করে → কত credits

Routing অগ্রাধিকার (configured থাকলে): **huggingface → cloudflare → comfyui_local → local → mock** (`registry.py: _PROVIDER_RANK`)। চার্জ = serving model-এর `cost_per_operation` (model cost না থাকলে operation fallback)।

| Operation | Serve করে (সস্তা → দামী) | চার্জ | Provider খরচ |
|---|---|---|---|
| background-remove | local-rmbg / comfy / local / mock ($0 🟢) · **HF bria $0.018 (1cr 🔴)** | 1 | $0 – $0.018 |
| upscale | comfy / local / mock ($0) | 1–2 | $0 🟢 |
| enhance | local / mock ($0) | 1 | $0 🟢 |
| object-remove / inpaint | comfy / local / mock ($0) · cf-sd15-inpaint (UNKNOWN 🟡) | 1–3 | $0 – ? |
| generative-fill | local/mock ($0) · cf-flux/sd15 (2–3cr) · **qwen $0.03+ (3cr 🔴)** | 1–3 | $0 – $0.06 |
| background-generate | local ($0) · cf (2–3cr) · **qwen $0.03+ (3cr 🔴)** | 1–3 | $0 – $0.06 |
| expand | mock / local ($0) | 1–3 | $0 🟢 |
| relight | mock / local ($0) | 1–2 | $0 🟢 |
| text-to-image | sdxl $0 · flux-4b $0.0012 (2cr 🟢) · flux-9b $0.015 (3cr 🟢) · **lucid $0.031 (3cr 🔴)** | 2–3 | $0 – $0.031 |
| face-restore | comfy ($0) | 1 | $0 🟢 |
| passport-photo | mock ($0, backend-exempt) | 1 | $0 🟢 |
| shadow / recolor / retouch / fashion / flat-lay / infographic / size-chart / carousel / social / ad / staging / photography / ghost / marketplace-resize | local-deterministic ($0) | 1–4 | $0 🟢 pure profit |
| product-edit / mockup-generate (legacy, registry-বহির্ভূত) | mock (1cr) · cf-flux/sd15 (2–3cr, paid/UNKNOWN) | 1–3 | $0 – ? |

## 5. Worst-case user → pocket loss?

Adversarial full-burn (সব credits সবচেয়ে দামী path-এ), rollover ছাড়া এক মাসে:

| Scenario | Provider খরচ | Net-এর বিপরীতে | Infra সহ loss |
|---|---|---|---|
| Pro 500cr → Qwen 2MP @3cr (166 ops × $0.06) | $9.96 | $9.40 | **−$2.56 / mo** |
| Pro 500cr → Bria @1cr (500 ops × $0.018) | $9.00 | $9.40 | **−$1.60 / mo** |
| Pro 500cr → lucid @3cr (166 ops × $0.031) | $5.15 | $9.40 | +$2.25 (thin profit) |
| Business 1500cr → Qwen 2MP (500 ops × $0.06) | $30.00 | $28.82 | **−$2.18 / mo** |
| উপরের যেকোনোটি ×3 auto-retry (credit ১বার, provider ৩বার) | ×3 | — | Pro ≈ **−$22**, Biz ≈ **−$63** |

Amplifier (মনে রাখুন):
- **Rollover + no-expiry** — user মাসের পর মাস জমিয়ে একবারে পোড়াতে পারে; মাসিক allowance liability-cap নয়। N মাস জমালে এক মাসে N× loss সম্ভব।
- **QA bypass** unbounded (শুধু flag-ধারী; QA email গোপন রাখুন)।
- Manual-retry free-reuse leak **বন্ধ করা হয়েছে** (এখন re-reserve হয়)।

## 6. Best/normal-case user → expected profit?

Typical mix — 70% $0-local (avg 1.5cr), 20% সস্তা-CF (~$0.001, 2cr), 10% HF/Qwen (~$0.03, 3cr):

| Plan | Provider খরচ | Profit | Margin |
|---|---|---|---|
| Pro 500cr | ≈ $0.54 (350cr×$0 + 50 ops×$0.0012 + 16 ops×$0.03) | **+$6.86** | **~69%** |
| Business 1500cr (একই mix ×3) | ≈ $1.62 | **+$25.20** | **~87%** |

Normal user-এ margin চমৎকার — loss শুধু adversarial concentration-এ।

## 7. সুপারিশ (kochāno fix, CHAIN-doc §5)

1. **bg-remove: HF serve করলে 2cr** (local path-এ 1cr থাকবে) — সবচেয়ে জরুরি।
2. **Qwen: 4cr + resolution multiplier** (≤1024px ×1 · ≤2048px ×1.5 · বড় ×2)।
3. **Leonardo lucid/phoenix: 4cr**।
4. sd15 / dreamshaper / lightning: প্রথম invoice-এ আসল $0 কিনা verify।
5. (ভবিষ্যৎ) Rollover cap — যেমন balance ≤ 2× allowance — নইলে hoard-and-burn liability বাড়তেই থাকবে।

## 8. Open unknowns (দাম বসানোর আগে যাচাই করুন)

1. sd15-img2img / inpaint, dreamshaper-8, sdxl-lightning-এর আসল CF neuron rate (pricing page-এ নেই)।
2. Runtime-এ আসল steps / megapixel (metering কোড নেই — `provider_cost_usd` ফাঁকা থাকতে পারে)।
3. xKiro/OpenRouter-free মডেলের commercial terms ও quota।
4. আসল infra $/user/mo ও Stripe fee schedule (এখানে $2 ও 2.9%+$0.30 ধরা)।
5. Production Stripe price ID বসেছে কিনা।

## 9. Margin Protection System (implemented 2026-09-21)

দাম বাড়লে বা ভবিষ্যতে দামী মডেল এলেও loss না হওয়ার জন্য ৩-স্তরের স্বয়ংক্রিয় সুরক্ষা — ভবিষ্যতের মডেল/দাম নিয়ে ভাবতে হবে না, সিস্টেম নিজেই সামলাবে:

**স্তর ১ — Quote floor (চার্জ কখনো cost-এর নিচে নয়):** `registry.quote_credits_for_model()` প্রতিটি dispatch-এ `max(registry floor, ceil(est_usd × R / budget))` চার্জ করে (`AI_USD_PER_CREDIT_BUDGET` default $0.0094)। VERIFIED USD আছে ৭টি মডেলে (`VERIFIED_USD_PER_OP`); অজানা cloud মডেলে conservative $0.003 analog + unverified flag; $0 provider-এ floor-ই থাকে। R = resolution multiplier (≤1MP ×1 · ≤4MP ×1.5 · বড় ×2)। ফলে: Bria আজ থেকে স্বয়ংক্রিয়ভাবে **2cr**, Qwen 1MP **4cr**, 2MP+ **5–7cr** — কোডে হাত না দিয়েই।

**স্তর ২ — Spend cap (worst-case loss-এর হার্ড সীমা):** প্রতি user, প্রতি billing cycle-এ measured provider spend (reported USD, না থাকলে dispatch-time estimate — কখনো শূন্য ধরা হয় না) যোগ হয়। Cap = `monthly_credits × budget × multiplier` (Pro $4.70 · Business $14.10 · Free $0.25 default; QA বাদ)। Cap পার হলে job **fail করে না** — স্বয়ংক্রিয়ভাবে $0 মডেলে (local/mock/comfy) reroute হয়, customer-এর quoted charge অপরিবর্তিত থাকে। Provider রাতারাতি ১০× দাম বাড়ালেও এক user-এর এক মাসের loss cap-এর মধ্যে বাঁধা। Env: `AI_SPEND_CAP_MULTIPLIER`, `AI_FREE_SPEND_CAP_USD`।

**স্তর ৩ — Drift alarm (দাম বাড়ার সিগন্যাল):** success-এ provider REPORTED cost quoted basis-এর 20%+ বেশি হলে `MARGIN DRIFT` warning log হয় (customer charge বদলায় না)। `python manage.py margin_health --days 30` per-model measured-vs-estimate টেবিল দেখায় — STALE / UNVERIFIED মডেল চিহ্নিত করে। নতুন মডেল যোগ করার নিয়ম: registry entry + `VERIFIED_USD_PER_OP`-এ আসল দাম (না জানলে analog default-ই fail-safe), tier ঠিক রাখা — বাকিটা সিস্টেমের কাজ।

**যা এখনো বাকি (স্বীকৃত সীমা):** provider-reported USD আজ প্রায় কোনো adapter-ই set করে না — drift alarm পুরো সক্রিয় হতে adapter-দের result-এ আসল cost বসাতে হবে; AI workspace chat মডেল এই cap-এর বাইরে (নিজস্ব bridge); rollover hoarding-এ cap (balance ≤ 2× allowance) ভবিষ্যৎ বিবেচনা।
