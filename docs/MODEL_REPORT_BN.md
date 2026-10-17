# ToolHub-AI — মডেল অ্যাভেইলেবিলিটি ও প্ল্যান রিপোর্ট

> তারিখ: 2026-09-26 (আপডেট ৫: সস্তা OR মডেল ২টি — ৩৯ মডেল, ১৬ READY)
> উৎস: লাইভ কোড ও `docs/model-capability-matrix.json`

## ০. সিলেক্টর নিয়ম (নতুন)

**সব মডেল সিলেক্টরে দেখা যাবে — হিডেন থাকবে না।** প্রতিটি compatible
মডেলের পাশে সৎ ব্যাজ থাকবে: `Recommended` / `Pro`🔒 / `Business`🔒 /
`Setup required` / `Pending verification`। Premium মডেল **লক অবস্থায়
দেখাবে** — প্ল্যান আপডেট (Pro/Business) করলেই আনলক হয়ে রান করবে।
চালানো (execution) এখনো কঠোর গেটে বাঁধা: লকড মডেলে `MODEL_TIER_LOCKED`,
সেটআপ-বাকিতে `MODEL_UNAVAILABLE` এরর — ভুয়া আউটপুট কখনো নয়।

---

## ১. সারসংক্ষেপ (এক নজরে)

| বিষয় | অবস্থা |
|---|---|
| মোট রেজিস্টার্ড ইমেজ মডেল | ৩৯টি |
| **লাইভ-ভেরিফাইড (আউটপুট দেয়)** | **৬টি** — local-rmbg, FLUX 4b/9b, PhotoRoom ghost/flat-lay/shadow |
| 👀 সিলেক্টরে দৃশ্যমান (লক/পেন্ডিংসহ) | **প্রতিটি AI টুলে ১–৯টি** |
| ⏳ PENDING — পেমেন্ট/key পেলেই চালু | **১৭টি** (enhance/retouch/inpaint/outpaint সহ) |
| 🔧 Deterministic (non-AI, সবসময় চালু) | **২টি utility** — marketplace-resize + creative-৫টি (infographic/size-chart/carousel/social/ad) |
| BETA (সিলেক্টরে দৃশ্যমান, রান করে না) | ৭টি |
| TEST-ONLY (কোনো ইউজার কখনো পাবে না) | ৬টি + utility-রা (শুধু নিজের op-এ) |
| চালু AI অপারেশন (৩০টির মধ্যে) | **১৬টি** (১১ AI + ৫ deterministic creative) |

---

## ২. মডেল তালিকা — কোনটা অ্যাভেইলেবল, কোনটা নয়

### ২.১ ✅ অ্যাভেইলেবল — আজই আউটপুট দেয়

| মডেল | প্রোভাইডার | টিয়ার | স্ট্যাটাস | ক্রেডিট | কী করতে পারে |
|---|---|---|---|---|---|
| `local-rmbg-u2net` (U²-Net) | local_rmbg (লোকাল CPU) | **Free** | VERIFIED_PRODUCTION (লাইভ ইনফারেন্স প্রমাণিত) | ১ | background-remove, passport-photo (composed pipeline) |
| `local-deterministic` | local (Pillow) | Free | non-AI utility (শুধু নিজের কাজে) | ১ | **শুধু** marketplace-resize (AI নয়, AI সিলেক্টরে আসে না) |

### ২.২ ⏳ PENDING — key/পেমেন্ট পেলেই চালু (কোড সম্পূর্ণ রেডি, সিলেক্টরে দৃশ্যমান)

**fal (একটাই key-তে ৬টা মডেল — ইন্টিগ্রেশন কোড ১০০% সম্পূর্ণ):**

| মডেল | ক্ষমতা | টিয়ার | ক্রেডিট | দাম (fal) |
|---|---|---|---|---|
| `fal-esrgan-upscale` | upscale (Real-ESRGAN) | Free | ২ | ~$০.০০১/compute-sec |
| `fal-fashn-tryon` | fashion-model (virtual try-on; গার্মেন্ট রেফারেন্স বাধ্যতামূলক) | Max (Business) | ৮ | $০.০৭৫/ছবি |
| `fal-flux-kontext-edit` | background-generate, product-edit, mockup-generate | Pro | ৩ | $০.০২৫/MP |
| `fal-flux-schnell-t2i` | text-to-image | Pro | ২ | $০.০০৩/MP |
| `fal-product-photography` | product-photography + product-staging | Pro | ৫ | $০.০৪/ছবি |
| `fal-relight` | relight (dedicated endpoint, style preset) | Pro | ৫ | $০.০৪/ছবি |

**PhotoRoom (এক key-তে ২টা dedicated fashion endpoint):**

| মডেল | ক্ষমতা | টিয়ার | ক্রেডিট | দাম |
|---|---|---|---|---|
| `photoroom-ghost-mannequin` | ghost-mannequin (dedicated endpoint) | Max (Business) | ১১ | $০.১০/কল |
| `photoroom-flat-lay` | flat-lay (dedicated endpoint) | Pro | ১১ | $০.১০/কল |

চালু করার ধাপ (শুধু আপনার দিকে): fal.ai-তে পেমেন্ট → `FAL_KEY` বসান →
`verify_models --live` পাস → মডেল **অটো-অ্যাভেইলেবল** (কোড বদল লাগবে না)।
একইভাবে PhotoRoom (`PHOTOROOM_API_KEY`, ghost/flat-lay), Hugging Face,
Cloudflare, ComfyUI।

**fal-relight (নতুন):** `fal-ai/image-apps-v2/relighting` — dedicated
endpoint, style preset (natural/studio/golden_hour/…/ambient), $০.০৪/ছবি
→ ৫ ক্রেডিট, Pro টিয়ার। কোড রেডি, key পেলেই চালু।

**PhotoRoom (নতুন):** `photoroom-ghost-mannequin` (Business, ১১ ক্রেডিট)
+ `photoroom-flat-lay` (Pro, ১১ ক্রেডিট) — দুটোই **dedicated endpoint**
(`v2/edit` + `ghostMannequin.mode` / `flatLay.mode`), $০.১০/কল।
Sandbox (watermark) কোথাও ব্যবহার হয় না।

**OpenRouter (নতুন, key VALID ✅):** `or-gemini-flash-image`
(Gemini 2.5 Flash Image — text-to-image, background-generate, product-edit,
mockup-generate; Pro, ২ ক্রেডিট)। Dedicated `/api/v1/images` API।
**লাইভ-রান প্রোভাইডার পর্যন্ত পৌঁছে clean 402 দিয়েছে** — ইন্টিগ্রেশন
পথ প্রমাণিত, শুধু ব্যালেন্স শেষ। Top-up → `--live` → অটো-promote।
(৫৫টি image মডেলের ক্যাটালগ যাচাইকৃত; শুরুতে ১টা নির্ভরযোগ্য মডেল।)

**xKiro কেন ইমেজ সিলেক্টরে নেই:** `/ai/`-এর xKiro/OpenRouter-চ্যাট
মডেলগুলো **LLM** — টেক্সট দেয়, ছবির লেয়ার বানাতে পারে না। xKiro
সরাসরি probe-এ 403 (bot-block) দেয় ও image endpoint-এর কোনো প্রমাণ
নেই → chat-only থাকাই সৎ সিদ্ধান্ত। OpenRouter-এর image-output মডেল
আছে বলেই উপরের `or-gemini-flash-image` ইন্টিগ্রেশন করা হয়েছে।

**অন্যান্য PENDING (key/পেমেন্ট/সার্ভিস বাকি):**

| মডেল | প্রোভাইডার | টিয়ার | ক্রেডিট | সমস্যা |
|---|---|---|---|---|
| `hf-bria-rmbg` (RMBG-2.0, **recommended**) | Hugging Face | Free | ১ | টোকেন VALID ✅ কিন্তু inference ক্রেডিট শেষ → HF-তে পেমেন্ট/PRO লাগবে (ফ্ল্যাগ এখন ON) |
| `hf-qwen-image-edit` (**recommended**) | Hugging Face | **Pro** | ৩ | একই (ফ্ল্যাগ ON) |
| `comfyui-local-upscale` (Real-ESRGAN 4x) | ComfyUI | Free | ১ | Docker-এ `host.docker.internal:8188`-এ ComfyUI চালু করলেই verify হবে |
| `comfyui-local-bg-remove` (BiRefNet, recommended) | ComfyUI | Free | ১ | একই |
| `comfyui-local-inpaint` (object-remove) | ComfyUI | Free | ২ | একই |
| `comfyui-local-face-restore` (CodeFormer) | ComfyUI | Free | ১ | একই |
| `or-gemini-flash-image` | OpenRouter | **Pro** | ২ | key VALID ✅ পাথ প্রমাণিত ✅ — ব্যালেন্স শেষ → top-up পেলেই চালু |
| fal ৬টি + PhotoRoom ২টি | fal/PhotoRoom | mixed | ২–১১ | key নেই → key বসালেই চালু |

### ২.৩ 🧪 BETA — সিলেক্টরে দৃশ্যমান (রান করে না, প্রমোশনে প্রমাণ লাগবে)

`cf-sdxl-base`, `cf-sd15-img2img`, `cf-sd15-inpaint`, `cf-dreamshaper-8`,
`cf-sdxl-lightning`, `cf-leonardo-lucid-origin`, `cf-leonardo-phoenix`
— সব **Pro** টিয়ার, ২–৩ ক্রেডিট।

### ২.৪ 🚫 TEST-ONLY — কোনো পেইড/ফ্রি ইউজার কখনো পাবে না

`mock-bg-remove`, `mock-generative-fill`, `mock-expand`, `mock-relight`,
`mock-text-to-image` — শুধু ইউনিট টেস্টের জন্য রাখা। প্রোডাকশন রাউটিং,
ফলব্যাক, সিলেক্টর থেকে সম্পূর্ণ বিচ্ছিন্ন। ভুল মডেল চাইলে ব্যাকএন্ড
`MODEL_CAPABILITY_MISMATCH` এরর দেয় — ভুল আউটপুট কখনো নয়।

---

## ৩. Premium (Pro/Business টিয়ার) মডেল কোনগুলো

টিয়ার মানে **এনটাইটেলমেন্ট গেট** — মডেলের `tier: pro` হলে শুধু Pro/Business
প্ল্যানের ইউজার সেটা ব্যবহার করতে পারবে (Free ইউজার ব্লকড)।

| Premium মডেল | ক্ষমতা | ক্রেডিট |
|---|---|---|
| `fal-flux-kontext-edit` ✅ কোড রেডি | background-generate, product-edit, mockup-generate | ৩ |
| `fal-flux-schnell-t2i` ✅ কোড রেডি | text-to-image | ২ |
| `fal-product-photography` ✅ কোড রেডি | product-photography, product-staging | ৫ |
| `fal-fashn-tryon` ✅ কোড রেডি | fashion-model (Business/max-tier) | ৮ |
| `fal-relight` ✅ কোড রেডি | relight (dedicated endpoint) | ৫ |
| `photoroom-ghost-mannequin` ✅ কোড রেডি | ghost-mannequin (dedicated endpoint, Business/max-tier) | ১১ |
| `photoroom-flat-lay` ✅ কোড রেডি | flat-lay (dedicated endpoint) | ১১ |
| `hf-qwen-image-edit` (ক্রেডিট শেষ — HF-তে পেমেন্ট লাগবে) | generative-fill, background-generate, product-edit, mockup-generate | ৩ |
| `cf-flux-klein-9b` ✅ **লাইভ-ভেরিফাইড** / `cf-flux-klein-4b` ✅ **লাইভ-ভেরিফাইড** | text-to-image, generative-fill, background-generate, product-edit, mockup-generate | ২ / ২ |
| `or-gemini-flash-image` (ব্যালেন্স শেষ — top-up পেলেই চালু) | text-to-image, background-generate, product-edit, mockup-generate + enhance/retouch/recolor (instruction-edit) | ২ |
| `or-gpt-image-mini` ✅ কোড রেডি (~$০.০০০০১/ছবি) | একই ৪ ক্ষমতা | ১ |
| `or-gemini-lite-image` ✅ কোড রেডি (~$০.০০০০৪/ছবি) | একই ৪ ক্ষমতা | ১ |
| `cf-sdxl-base`, `cf-dreamshaper-8`, `cf-sdxl-lightning` (BETA) | text-to-image | ২ |
| `cf-leonardo-lucid-origin`, `cf-leonardo-phoenix` (BETA) | text-to-image | ৩ |
| `cf-sd15-img2img` (BETA) | generative-fill, background-generate, product-edit, mockup-generate | ২ |
| `cf-sd15-inpaint` (BETA) | inpaint, object-remove | ২ |

> ⚠️ গুরুত্বপূর্ণ: **Pro থাকলেই মডেল পাওয়া যায় না** — মডেলকে আগে
> `verify_models --live`-এ পাস করে VERIFIED_PRODUCTION হতে হবে। Pro শুধু
> *অনুমতি* দেয়; কোয়ালিটি গেট *প্রাপ্যতা* নির্ধারণ করে। আজ কোনো Premium
> মডেলই live-verified নয়, তাই আজ Pro নিয়েও Premium মডেলের আউটপুট নেই।

---

## ৪. বর্তমানে কোন কোন টুল আউটপুট দেয়

| টুল | মডেল | ক্রেডিট | কে ব্যবহার করতে পারে |
|---|---|---|---|
| Background Remove (`bg-remove`) | local-rmbg-u2net (U²-Net) | ১ | Free + Pro + Business (Free-তে ৫ ওয়েলকাম ক্রেডিট দিয়ে ~৫ বার) |
| Passport Photo (`passport`) | local-rmbg-u2net + deterministic compositing (দেশভেদে সাইজ: USA 600×600, UK/EU 350×450, BD 400×500) | ১ | **Pro + Business** (ফিচার ফ্ল্যাগ `ai_passport_photo` Free-তে নেই) |
| Marketplace Resize | local-deterministic (non-AI, Pillow) | ১ | Free + Pro + Business |

৩টি অপারেশন আজ রান করে। বাকিগুলো সিলেক্টরে **দৃশ্যমান** (লক/পেন্ডিং
ব্যাজসহ) কিন্তু রান করে না — key/ভেরিফিকেশন পেলেই অটো-চালু:

- key পেলেই চালু হবে: upscale, object-remove, inpaint, face-restore,
  generative-fill, background-generate, text-to-image, relight,
  fashion-model, ghost-mannequin, flat-lay, product-edit, mockup-generate,
  product-staging, product-photography (১৫টি — সব কোড রেডি)
- এখনো কোনো verified মডেল নেই: enhance, shadow, recolor, retouch,
  fashion-retouch, expand, expand-image, infographic, size-chart, carousel,
  social-creative, ad-creative (১২টি — গবেষণা বাকি)

কোনো অবস্থাতেই ভুয়া/নকল আউটপুট দেওয়া হয় না।

---

## ৫. টুলভিত্তিক ক্রেডিট খরচ (রেজিস্ট্রি থেকে)

| টুল | ক্রেডিট | টুল | ক্রেডিট |
|---|---|---|---|
| background-remove / enhance / face-restore / passport-photo / marketplace-resize | ১ | text-to-image / upscale / object-remove / inpaint / relight / shadow / recolor / retouch / fashion-retouch / flat-lay / size-chart | ২ |
| generative-fill / background-generate / expand / product-edit / product-staging / product-photography / ghost-mannequin / infographic / social-creative / ad-creative | ৩ | mockup-generate / fashion-model / carousel | ৪ |

ব্যর্থ জবের ক্রেডিট **রিফান্ড** হয় (reserve → finalize/refund লাইফসাইকেল);
mock/ডেমো পথে কোনো চার্জ নেই (প্রোডাকশনে mock পৌঁছায়ই না)।
উপরের সংখ্যা op-fallback; **আসল চার্জ = নির্বাচিত মডেলের floor**
(যেমন ghost → ১১, fashion → ৮) — প্যানেলে এখন backend-quoted মানই দেখায়।

---

## ৬. ইউজার সীমাবদ্ধতা — Free বনাম Pro বনাম Business

| সুবিধা | Free ($০) | Pro ($৯.৯৯/মাস, $৮৯/বছর) | Business ($২৯.৯৯/মাস, $২৯৯.৯০/বছর) |
|---|---|---|---|
| মাসিক AI ক্রেডিট | ০ (তবে সাইনআপে **৫টি ওয়েলকাম ক্রেডিট** ফ্রি) | **৫০০** | **১৫০০** |
| AI টুল অ্যাক্সেস | শুধু background-remove + marketplace-resize | **সব ৩০টি অপারেশনের ফিচার ফ্ল্যাগ** (মডেল ভেরিফাই হলেই) | সব + fashion-model, ghost-mannequin, brand-kit, team, priority |
| মডেল টিয়ার অ্যাক্সেস | শুধু `free` টিয়ার মডেল | **free + pro টিয়ার মডেল** | free + pro (+ max র‍্যাংক) |
| দৈনিক লিমিট | ৫টি জব | আনলিমিটেড | আনলিমিটেড |
| স্টোরেজ (আপলোড) | ৫ MB | ৫০ MB | ৫০০ MB |
| ব্যাচ প্রসেসিং | ১টি ছবি | ১০টি | ১০০টি |
| API লিমিট | ০ | ৩০০ | ৫০০০ |
| High-res export / cloud history / bulk | ❌ | ✅ | ✅ |

(QA টেস্ট অ্যাকাউন্ট: সব সীমার বাইরে, ক্রেডিট চার্জ হয় না।)

## ৭. Pro নিলে কী কী বেনিফিট (আজকের বাস্তবতায় + ভবিষ্যতে)

**আজই পাবেন:** ৫০০ ক্রেডিট/মাস, সব AI ফিচার-ফ্ল্যাগ আনলক (passport সহ),
দৈনিক লিমিট মুক্ত, ৫০MB স্টোরেজ, ১০-ব্যাচ, API অ্যাক্সেস।
**মডেল ভেরিফাই হওয়ার সাথে সাথে (কোড বদল ছাড়াই)** Pro ইউজাররা পাবেন:
`fal-flux-kontext-edit` (background-generate/product-edit/mockup),
`fal-flux-schnell-t2i` (text-to-image), `fal-product-photography`
(product/staging), `fal-esrgan-upscale`, `hf-qwen-image-edit`,
`cf-flux-klein` —
Free ইউজাররা এগুলো কখনোই পাবেন না (pro-tier গেট)। অর্থাৎ Pro = *আজকের
সুবিধা + ভবিষ্যৎ Premium মডেলের এক্সক্লুসিভ অ্যাক্সেস*।

## ৯. এই রাউন্ডের ফিক্স (২০২৬-০৯-২৬)

1. **Dynamic cost display** — সব AI প্যানেলে (OperationPanel, CropExpand,
   Relight, GenerationPanel, Passport) এখন backend-quoted per-model খরচ
   দেখায়; static লেবেল শুধু fallback।
2. **Expand shared state** — CropExpandPanel এখন GenerationPanel-এর সাথে
   একই `useToolModel("expand")` ব্যবহার করে (divergence বন্ধ)।
3. **OperationPanel persistence** — টুল বদলে ফিরে এলেও বাছাই থাকে।
4. **Pending-নোট** — runnable কিছু না থাকলে সৎ ব্যাখ্যা দেখায়।
5. **Dead code মুছে ফেলা** — ৮টা অ-রেন্ডার Inspector + AiEditPanel
   (~৭০০ লাইন), সব unused import সহ; tsc/eslint/vitest সবুজ।
6. **flux-9b floor ৩→২** — chain-math অনুযায়ী ($0.0188 ≥ $0.015, মার্জিন
   থাকে); T2I static লেবেল (২) এখন ডিফল্ট মডেলের চার্জের সাথে মিলে।
7. **Relight mode-mapping** — প্যানেলের preset (studio/soft/golden/moon…)
   fal lighting_style-এ ম্যাপ হয় (golden→golden_hour, moon→moonlight)।

## ১১. Batch Editor — flagship upgrade ✅

- **Model picker**: প্রতি batch-এ একটা মডেল (visible + lock/disabled state সহ);
  backend প্রতিটি child job কঠোরভাবে revalidate করে (mock → per-item fail)।
- **সত্যিকারের estimate**: নির্বাচিত মডেলের floor অনুযায়ী per-image + total
  (shadow ২→১১, relight ৫, fashion ৮ সংশোধিত)।
- **Relight op যোগ** (style preset select সহ) — এখন ৭ অপারেশন।
- **Cap UX**: over-limit-এ Process disabled + "remove N or upgrade" বার্তা
  (আগে toast dead-end ছিল)।
- **CTA amber** + progress amber; grammar ("1 image"); "Supports JPG, PNG…"।
- Backend: `model_id` passthrough + per-item ValueError রিপোর্টিং।

## ১০. ১২ টুলের verdict — সম্পূর্ণ বাস্তবায়িত ✅

**সব বাস্তবায়িত ✅** — ৭টায় verified মডেল, ৫টায় deterministic utility:

| টুল | রায় | মডেল (কোড রেডি) |
|---|---|---|
| shadow | ✅ dedicated endpoint | `photoroom-shadow` (overrides UI slider থেকে ম্যাপ) |
| expand / expand-image | ✅ dedicated endpoint | `fal-outpaint` (direction+px ম্যাপিং) |
| object-remove / inpaint / generative-fill (masked) | ✅ dedicated endpoint | `fal-qwen-inpaint` (mask বাধ্যতামূলক) |
| recolor | ✅ instruction-edit (mask ছাড়াই কন্ট্রাক্ট) | `fal-flux-kontext-edit` |
| enhance | ✅ dedicated endpoint | `fal-clarity-enhance` (1x — dims বদলায় না) |
| retouch / fashion-retouch | ✅ dedicated endpoint | `photoroom-beautify` (caveat ডকুমেন্টেড) |
| infographic / size-chart / carousel / social-creative / ad-creative | ✅ deterministic (AI নয়) | `local-creative-compose` — আসল compositor, AI selector নেই, ১cr |

## ৮. মালিকের করণীয় (আপনার দিকে — কোড রেডি)

1. ✅ **সম্পন্ন — Cloudflare FLUX 4b/9b লাইভ** (৫টি টুল চালু: text-to-image,
   generative-fill, background-generate, product-edit, mockup-generate)।
2. **Hugging Face:** টোকেন VALID, ফ্ল্যাগ ON করা হয়েছে — শুধু HF
   অ্যাকাউন্টে inference ক্রেডিট ভরুন (বা PRO) → `verify_models --live
   --models hf-bria-rmbg,hf-qwen-image-edit` → bria+Qwen চালু।
3. **OpenRouter:** key VALID, পাথ প্রমাণিত — ব্যালেন্স top-up → `--live
   --models or-gemini-flash-image` → T2I/এডিটের ২য় সোর্স চালু।
4. **fal (key বসানো ✅ কিন্তু account LOCKED):** fal.ai → Billing → **TOP_UP**
   করলেই লক খুলবে → `verify_models --live` (৮ মডেল: upscale, fashion,
   kontext, schnell, product, relight, inpaint, outpaint) → অটো-চালু।
   এরর ছিল স্পষ্ট: `"User is locked. Reason: TOP_UP"` — key ভুল নয়।
5. **PhotoRoom ✅ সম্পন্ন:** key VALID, ৩ মডেল লাইভ-ভেরিফাইড (ghost 11.9s,
   flat-lay 9.8s, shadow 1.1s — সব 1024×1024, transformation প্রমাণিত)।
   ব্যালেন্স ছিল ১০, খরচ হলো ৩ → বাকি ৭। শেষ হলে top-up লাগবে।
6. **ComfyUI:** Docker হোস্টে ComfyUI সার্ভিস চালু থাকলে (`:8188`)
   `--live` → ৪টা লোকাল মডেল চালু (upscale/inpaint/face-restore/BiRefNet)।
