# ToolHub-AI — Complete Project Research, Feature Catalog & Showcase Kit

> এই ফাইলে তিনটা জিনিস আছে: (A) সম্পূর্ণ প্রজেক্ট গবেষণা, (B) সব ফিচারের বর্ণনা,
> (C) LinkedIn-এ পোস্ট করার ভার্সন, (D) পোর্টফোলিওতে যুক্ত করার ভার্সন।
> C ও D ইংরেজিতে, copy-paste ready। সব তথ্য কোড থেকে যাচাইকৃত।

---

# PART A — সম্পূর্ণ প্রজেক্ট গবেষণা

## 1. প্রজেক্ট পরিচিতি

**ToolHub-AI** একটি full-stack AI SaaS প্ল্যাটফর্ম — স্লোগান *"One AI workspace. Everything you need to create."*
একটাই অ্যাকাউন্টে তিনটা জগৎ: AI চ্যাট ওয়ার্কস্পেস + প্রফেশনাল ইমেজ এডিটর + ৬০+ দৈনন্দিন ইউটিলিটি টুল।

## 2. স্কেল (যাচাইকৃত সংখ্যা)

| মেট্রিক | সংখ্যা |
|---|---|
| Backend Python ফাইল | 538টি (~40,000 লাইন) |
| Frontend TS/TSX ফাইল | 404টি (~61,000 লাইন) |
| পেজ রুট (`page.tsx`) | 143টি |
| API endpoint (`path()`) | ~191টি |
| Django app | 27টি |
| সিড করা AI মডেল | 62টি, 11টি provider থেকে |
| Provider adapter (backend) | 15টি |
| Model capability | 17টি key |
| রেজিস্টার্ড টুল | 61টি (15 mega-menu ক্যাটাগরি) |
| এডিটর টুল-রেল এন্ট্রি | 36টি (13 AI + 13 product/e-commerce) |
| প্ল্যান | 3টি — Free $0, Pro $9.99, Business $29.99 |

## 3. আর্কিটেকচার

```
Browser ──► Next.js 16 (App Router · React 19 · TypeScript · Tailwind v4 · shadcn/ui)
                │  NEXT_PUBLIC_API_URL=/api/v1 · SSE স্ট্রিমিং
                ▼
Django REST Framework (Gunicorn ×2 workers)
 ├── authentication — SimpleJWT (access 60m / refresh 1d, rotation+blacklist),
 │                      Google/GitHub OAuth, password reset (1h token)
 ├── ai_workspace — 15 provider adapter → SSE gateway → credit reserve/refund
 ├── subscriptions — Plan, CreditWallet, idempotent CreditTransaction, entitlements
 ├── billing — Stripe / LemonSqueezy / bKash / Nagad (verified-webhook state machine)
 ├── ai_tools / image_tools / pdf_tools / developer_tools / seo_tools /
 │   business_tools / ecommerce_studio / workspace / storage / affiliates / …
 │                      (~191 endpoint, সব APIView+path, কোনো router নয়)
                ├──► PostgreSQL 15 · Redis 7 ──► Celery worker + beat
                └──► ComfyUI (local GPU) · rembg (U2-Net) · FAL · PhotoRoom · HuggingFace
```

**Docker services:** `db`, `redis`, `backend`, `celery`, `celery-beat`, `frontend`, `cloudflared` (optional profile — inbound port না খুলেই Cloudflare edge থেকে access)।

## 4. টেক স্ট্যাক

- **Frontend:** Next.js 16.3, React 19.2, TypeScript, Tailwind CSS 4, shadcn/ui, Fabric.js 7, Lena.js, react-advanced-cropper, next-themes (dark mode), Web Speech API
- **Backend:** Python 3.12, Django 6.1, DRF 3.18, SimpleJWT, Celery 5.6, Redis 7, PostgreSQL 15, Pillow 12, rembg, pypdf, qrcode, Stripe SDK
- **AI/Infra:** Docker Compose, Gunicorn, Cloudflare Tunnel, ComfyUI, LiteLLM config, HuggingFace Inference, Ollama-compatible self-hosted endpoint

## 5. গুরুত্বপূর্ণ ইঞ্জিনিয়ারিং সিদ্ধান্ত

1. **Credit-safety:** `reserve → stream → refund/commit` ফ্লো, idempotency key সহ (`workspace:{msg}:attempt:{n}`)। Provider fail, fallback, বা client disconnect হলে ক্রেডিট ফেরত — একটাই choke point (`CreditService`)।
2. **Server-side enforcement:** plan/tier/limit যাচাই শুধু backend-এ (402/403/429); frontend কখনো permission সিদ্ধান্ত নেয় না। QA bypass শুধু `EntitlementService.is_qa` দিয়ে।
3. **Streaming gateway:** SSE ইভেন্ট (`meta → delta* → done/error`); compare-mode-এ thread+queue fan-out; AbortController দিয়ে stop; 401-এ একবার token refresh-retry।
4. **Provider abstraction:** 15 adapter + capability registry + live-verification gate — paid selector-এ মডেল ওঠে শুধু `verify_models --live` পাস করলে। মরা provider 15 মিনিটের জন্য লুকিয়ে রাখা হয়।
5. **Custom markdown renderer:** JSON collapsible tree, CSV→table, pipe-table + CSV export, sandboxed HTML preview (app DOM-এ inject হয় না), XML validity badge, math raw-fallback — সব streaming-safe, অসমাপ্ত ব্লক plain text-এ degrade করে।
6. **Honest UX:** ভুয়া feedback বাটন নেই; model fallback হলে toast; burst/daily limit, credit banner (80%/95% threshold)।

---

# PART B — সম্পূর্ণ ফিচার ক্যাটালগ (যা যা করা হয়েছে)

## B1. AI Workspace (`/ai`)

- **New chat:** 4 starter (Write/Code/Ideas/Create), free-model default + Auto fallback, backend workflow prefill (≤6, click-to-draft), `?project=` সংযোগ
- **Conversation thread:** SSE স্ট্রিমিং, ThinkingIndicator + StreamingCursor, regenerate, "যেখানে থেমেছে সেখান থেকে continue", jump-to-latest বাটন, মাঝপথে মডেল বদল (context অটুট থাকে)
- **Composer (12 control):** ফাইল attach (image/pdf/txt/md/csv/json/code/doc, সর্বোচ্চ 5, vision-mismatch warning), Library থেকে যোগ, ModelSelector, Think toggle (reasoning মডেলে auto-switch), Web Search toggle, Tools menu (Image studio/Compare/Projects/All tools), mic dictation (locale-aware Web Speech API), voice-mode, Send/Stop, Enter-to-send, 320px পর্যন্ত auto-resize
- **Compare (`/ai/compare`):** সর্বোচ্চ 3 মডেল side-by-side, per-column queued/streaming/completed/failed + latency, copy/regenerate/open-as-chat, abort
- **Models directory (`/ai/models`):** search + capability tab + tier/health filter, tier badge, capability chip, context window, health dot
- **Projects:** create/delete/open, conversation count (`/ai?project=` দিয়ে নতুন চ্যাট লিংক)
- **Library (`/ai/library`):** 5 tab, search, grid/list view, preview dialog, upload/download/rename/star/delete, folder — composer-এর "Add from Library" ডায়ালগ একই ফাইল পুনর্ব্যবহার করে
- **Seeded মডেল (62টি):** mock 14 + official 48 — OpenAI (gpt-4o, 4o-mini), Anthropic (sonnet-4.5, haiku-4.5), Google (gemini-3-flash-preview, 3.6-flash), DeepSeek, Meta (muse-spark-1.3), HuggingFace 6, self-hosted 3 (Qwen/Gemma), Cloudflare 5, xKiro gateway 7, OpenRouter 18 (সব `:free`)
- **Capability (17):** chat, reasoning, vision, files, web, tools, coding, image_generation, image_editing, speech_to_text, text_to_speech, embeddings, video (+ alias)

## B2. Image Editor (`/tools/image-editor`)

- **Canvas:** layer system (LayersPanel, order/category), non-destructive filter pipeline (Lena.js), viewport zoom, alignment guide, cropper, brush-mask canvas (generative fill/inpaint), template preset
- **36 tool-rail:** transform (pan/resize/crop/rotate/social) + 13 AI (bg-remove, upscale, enhance, object-remove, generative-fill, background-generate, expand, relight, shadow, recolor, retouch, text-to-image…) + 13 product/e-commerce (fashion-model, ghost-mannequin, flat-lay, product-staging/photography, infographic, size-chart, carousel, ad-creative…) + export
- **Workflow:** VersionHistory (undo/redo), Before/After slider compare, keyboard shortcut dialog, UploadsPanel, ExportDialog (png/jpeg/webp, quality slider) + user-saved export preset, SmartToolRecommendations, QuickAIActions
- **Preset:** social 7, resize 8, passport 5 দেশ (usa/uk/eu/india/bd), crop aspect 6, watermark position 6, mockup frame 6, product background/lighting/shadow

## B3. Utility Tools (61টি রেজিস্টার্ড)

- **Image (22):** editor, cropper, rotator, watermark, bg-remover, object-remover, enhancer, upscaler, passport-photo, mockup-generator, product-image-editor, resizer, social-media-resizer, compressor, converter, webp/avif converter, favicon-generator, batch-editor + AI studio (generative-fill, background-generator, expand-canvas, relight, shadow, recolor, retouch, fashion-model, ghost-mannequin, flat-lay, marketplace-resize, staging, product-photography, infographic, size-chart, carousel, social/ad creative, text-to-image)
- **PDF (8):** merge, split, compress, rotate, protect, unlock, pdf-to-jpg, jpg-to-pdf
- **Text (4):** word-counter, case-converter, text-cleaner, remove-duplicate-lines
- **SEO/Web (5):** meta-tag, open-graph, robots.txt, sitemap generator, SEO analyzer
- **Developer/Utility (5+):** QR generator, password generator, link shortener, resume builder

## B4. Dashboard (`/dashboard`)

Time-greeting হোম, QuickTools/RecentProjects/RecentActivity উইজেট, UsageSummary (plan + AI credit + storage), usage টেবিল, billing (plan/subscription/invoice/payment), file manager (preview/rename/delete), project CRUD + detail, favorites, affiliate (referral code/link, commission), settings, profile, job history।

## B5. Billing ও Plan

| Plan | দাম | Credit/মাস | Storage | Daily | Batch | API |
|---|---|---|---|---|---|---|
| Free | $0 | 0 | 5 MB | 5 | 1 | 0 |
| Pro | $9.99 (বছরে $89) | 500 | 50 MB | unlimited | 10 | 300 |
| Business | $29.99 (বছরে $299.90) | 1500 | 500 MB | unlimited | 100 | 5000 |

Payment: Stripe, LemonSqueezy, bKash, Nagad — শুধু verified webhook-ই তথ্য বদলায় (state machine)।

## B6. Auth, Content, Platform

- **Auth:** email/password (login/register/forgot/reset/verify-email) + Google/GitHub OAuth callback
- **Content:** blog (+slug), guides, docs, FAQ, pricing, checkout, global search, live status checker, security, legal (privacy/terms/cookies), contact, about, partners, affiliate পেজ
- **Homepage:** hero (আসল light/dark স্ক্রিনশট, theme-aware), capability grid, model ecosystem, image-editor showcase, tools grid, workspace, pricing, trust/security, final CTA
- **Platform:** dark mode (next-themes), `Intl` locale formatting, global search + mega-menu, admin panel + audit log, contact form

---

# PART C — LinkedIn পোস্ট ভার্সন (English, copy-paste)

> 🚀 Excited to share **ToolHub-AI** — a full-stack AI SaaS platform I built: one AI workspace plus 60+ practical tools.
>
> 💬 **AI Workspace** — chat across 10+ LLM providers (OpenAI, Anthropic, Gemini, DeepSeek, Qwen, Mistral, Llama, Cloudflare, HuggingFace, self-hosted) with SSE streaming, auto model routing, side-by-side model comparison, projects, and a file library.
>
> 🎨 **Pro Image Editor** — layer-based canvas with 36 tools: AI background remove, generative fill, relight, upscale, plus e-commerce studio (fashion model, product staging, ghost mannequin), version history, and before/after compare.
>
> 🧰 **60+ Utility Tools** — image, PDF, text, SEO, QR, and developer tools, all behind one registry and mega-menu.
>
> 💳 **Billing done right** — idempotent credit reserve/refund flow, server-side plan enforcement, and payments via Stripe, LemonSqueezy, bKash, and Nagad.
>
> 🛠️ **Stack:** Next.js 16 · React 19 · TypeScript · Django REST · PostgreSQL · Redis · Celery · Docker · ~100k lines · 140+ routes · ~190 APIs
>
> #BuildInPublic #FullStack #NextJS #Django #AI #SaaS #OpenSource

---

# PART D — পোর্টফোলিও ভার্সন (English, copy-paste)

## ToolHub-AI — One AI Workspace + 60 Tools (Full-Stack SaaS)

A production-grade AI SaaS platform: multi-provider LLM chat workspace, professional image editor, and a 61-tool utility suite — Next.js 16 frontend, Django REST backend, Dockerized 6-service stack.

**What I built:**
- **AI chat gateway** — 15 provider adapters, SSE streaming (`meta → delta → done`), auto-routing with live-verification gate, 3-model compare mode, projects, file library, 62 seeded models
- **Credit-safe billing** — reserve/refund with idempotency keys, server-side entitlements (402/403/429), Stripe + LemonSqueezy + bKash + Nagad webhooks
- **Image editor** — layers, non-destructive filters, mask canvas for inpainting, 36 tool-rail (13 AI + 13 e-commerce), version history, export presets
- **Platform** — JWT + OAuth, dashboard (usage/billing/files/affiliates), blog, docs, global search, dark mode, theme-aware marketing site

**Stack:** Next.js 16 · React 19 · TypeScript · Tailwind 4 · shadcn/ui · Django 6 · DRF · PostgreSQL 15 · Redis 7 · Celery · Gunicorn · Docker · Cloudflare Tunnel · ComfyUI

**Scale:** ~100k lines · 143 routes · ~191 API endpoints · 27 Django apps · 6 Docker services
