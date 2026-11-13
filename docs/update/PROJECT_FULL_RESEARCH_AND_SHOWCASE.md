# ToolHub-AI — Full System Research, Architecture & Feature Catalog
**One AI workspace. Everything you need to create.**

---

## 📌 Table of Contents
1. [Executive Summary & Product Vision](#1-executive-summary--product-vision)
2. [Verified Scale & System Metrics](#2-verified-scale--system-metrics)
3. [System Architecture & Infrastructure](#3-system-architecture--infrastructure)
4. [Exhaustive Feature Catalog](#4-exhaustive-feature-catalog)
   - [4.1 AI Multi-Model Workspace (/ai)](#41-ai-multi-model-workspace-ai)
   - [4.2 Pro Layer-Based Image Editor & AI Studio (/tools/image-editor)](#42-pro-layer-based-image-editor--ai-studio-toolsimage-editor)
   - [4.3 Central Utility Tools Suite (61 Tools)](#43-central-utility-tools-suite-61-tools)
   - [4.4 Subscription, Billing & Credit-Safe Ledger](#44-subscription-billing--credit-safe-ledger)
   - [4.5 User Dashboard, File Library & Affiliate Engine](#45-user-dashboard-file-library--affiliate-engine)
   - [4.6 Custom Streaming Markdown Engine & UX Primitives](#46-custom-streaming-markdown-engine--ux-primitives)
5. [Key Engineering Challenges & Solutions](#5-key-engineering-challenges--solutions)
6. [LinkedIn Post Version (Ready to Publish)](#6-linkedin-post-version-ready-to-publish)
7. [Portfolio Showcase & Case Study (Ready to Feature)](#7-portfolio-showcase--case-study-ready-to-feature)

---

# 1. Executive Summary & Product Vision

**ToolHub-AI** is a production-grade, enterprise-ready full-stack AI Software-as-a-Service (SaaS) platform built to solve modern digital workflow fragmentation. 

Instead of forcing creators, developers, and businesses to juggle disparate, costly monthly subscriptions across AI chat platforms (ChatGPT/Claude), image manipulation suites (Photoshop/Canva/PhotoRoom), and routine file conversion utilities (iLovePDF/TinyURL), **ToolHub-AI integrates all three pillars under a unified user account, credit-safe billing ledger, and design system**.

---

# 2. Verified Scale & System Metrics

*Metrics verified directly against the production codebase:*

| Metric / Dimension | Verified Count | Details / Notes |
|---|---|---|
| **Total Lines of Code (LOC)** | **~101,000+ lines** | Frontend (~61k lines TS/TSX) + Backend (~40k lines Python) |
| **Frontend Source Files** | **404+ files** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4 |
| **Frontend Page Routes** | **143 routes** | `/ai`, `/tools/**`, `/dashboard/**`, `/blog/**`, `/pricing`, etc. |
| **Backend Source Files** | **538+ files** | Python 3.12, Django 6.1, Django REST Framework 3.18 |
| **Django Modular Apps** | **27 apps** | `ai_workspace`, `billing`, `subscriptions`, `image_tools`, etc. |
| **Production API Endpoints** | **~191 endpoints** | Explicit `path()` routes (RESTful + Server-Sent Events) |
| **Central Registered Tools** | **61 tools** | 15 mega-menu categories (Image, PDF, SEO, Dev, Text) |
| **Editor Tool-Rail Actions** | **36 tools** | 13 Core AI tools + 13 E-Commerce studio tools + canvas transforms |
| **Supported AI Models** | **62 seeded models** | OpenAI, Anthropic, Google Gemini, DeepSeek, Meta, Qwen, etc. |
| **AI Provider Adapters** | **15 adapters** | Pluggable unified provider architecture with live verification |
| **Model Capabilities** | **17 capability keys**| Chat, Reasoning, Vision, Files, Web, Coding, Speech, Image Gen |
| **Payment Gateways** | **4 providers** | Stripe, LemonSqueezy, bKash (Tokenized API), Nagad API |
| **Docker Microservices** | **6 containers** | `frontend`, `backend`, `db`, `redis`, `celery`, `celery-beat` |

---

# 3. System Architecture & Infrastructure

```
[ Web / Mobile Browser ]
          │
          │ HTTP / Server-Sent Events (SSE)
          ▼
[ Next.js 16 Frontend (App Router, React 19, TypeScript, Tailwind CSS 4, shadcn/ui) ]
          │
          │ Reverse Proxy / API Gateway (`/api/v1/`)
          ▼
[ Django 6.1 REST API (Gunicorn Multi-Workers) ]
   ├── Authentication: SimpleJWT (Rotation + Blacklist), Google & GitHub OAuth2
   ├── AI Gateway: 15 Provider Adapters (OpenAI, Anthropic, Google, DeepSeek, etc.)
   ├── Credit Safety Engine: Atomic Reserve → Stream → Commit / Refund Ledger
   ├── Subscriptions & Entitlements: Multi-Tier Server-Side Enforcement (Free, Pro, Business)
   ├── Webhook State Machine: Cryptographically Verified Payment Webhooks
   └── Processing Engines: Pillow 12, PyPDF, rembg (U2-Net), OpenCV
          │
          ├──► [ PostgreSQL 15 ] (ACID Transactional Data, Wallets, Audit Logs)
          ├──► [ Redis 7 ] (Cache, Rate Limiting & Message Broker)
          ├──► [ Celery Worker & Beat ] (Asynchronous Heavy Jobs, Expirations)
          └──► [ ComfyUI (Local GPU) / Cloudflare Tunnel / LiteLLM ]
```

### Infrastructure Highlights:
- **Zero-Inbound Port Exposure:** Secured via Cloudflare Tunnel (`cloudflared`), shielding backend services from direct public internet scanning.
- **Asynchronous Task Offloading:** Heavy compute operations (multi-page PDF merging, bulk image resizing, background removal, renewal cycles) run out-of-band via Celery and Redis.
- **Database Partitioning & Safety:** Relational schemas with strict foreign-key cascades, atomic transactions for financial ledgers, and comprehensive admin audit logging.

---

# 4. Exhaustive Feature Catalog

## 4.1 AI Multi-Model Workspace (`/ai`)
*A unified interface to query, benchmark, and collaborate with world-leading LLMs.*

1. **15 Provider Adapters & 62 Seeded Models:**
   - **OpenAI:** GPT-4o, GPT-4o-mini, o1, o3-mini.
   - **Anthropic:** Claude 3.5 Sonnet, Claude 3.5 Haiku.
   - **Google DeepMind:** Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0 Flash.
   - **DeepSeek & Qwen:** DeepSeek V3, DeepSeek R1 (Deep Reasoning), Qwen 2.5 Coder.
   - **Meta & Open Models:** Llama 3.3 70B, Mistral Large, HuggingFace Inference Endpoints.
   - **Cloudflare Workers AI & Local Self-Hosted:** Ollama-compatible endpoints & local GPUs.
   - **17 Capability Matrix Flags:** Chat, Reasoning, Vision, File Attachment, Live Web Search, Tool Calling, Code Execution, Image Generation, Voice/TTS.

2. **Real-Time Streaming & Thinking Mode:**
   - Low-latency Server-Sent Events (SSE) gateway with custom event lifecycles (`meta` ➔ `delta*` ➔ `done`/`error`).
   - **Reasoning / Thinking Mode:** Live accordion displaying step-by-step internal reasoning thoughts for DeepSeek R1 and OpenAI o-series models.
   - **StreamingCursor & Dynamic Auto-Scroll:** Fluid UI rendering with pause-on-wheel-up intelligence.
   - **Mid-Stream Cancellation:** Immediate `AbortController` termination with server-side unconsumed token refunding.

3. **Side-by-Side Model Comparison (`/ai/compare`):**
   - Simultaneous query fan-out to up to 3 models in parallel.
   - Per-column metrics: Live response streaming, latency tracking (in milliseconds), and token consumption.
   - One-click action to promote any response into a full persistent chat session.

4. **12-Control Composer:**
   - Drag-and-drop multi-file attachments (images, PDFs, text, JSON, code) with automatic vision-capability validation.
   - Direct asset ingestion from the Central File Library (`/ai/library`).
   - Integrated Live Web Search toggle.
   - Native voice dictation via browser Web Speech API.
   - Auto-expanding textarea up to 320px with full keyboard shortcuts (Shift+Enter for newline, Enter to send).

5. **Project Hierarchies & Session Persistence:**
   - Context preservation across model switches mid-conversation.
   - Categorized project folders with conversation tagging and instant export.

---

## 4.2 Pro Layer-Based Image Editor & AI Studio (`/tools/image-editor`)
*A browser-native image composition and generative AI studio rivaling desktop software.*

1. **Canvas & Multi-Layer System (Fabric.js 7):**
   - Interactive multi-layer management (image layers, text layers, vector masks).
   - Non-destructive WebGL filter pipeline (Lena.js: brightness, contrast, saturation, blur, sepia, edge detection).
   - Infinite canvas pan, zoom controls, magnetic alignment guides, and snap-to-grid.
   - Dynamic crop tool with standard social media aspect ratios (1:1, 16:9, 4:5, 9:16).

2. **Inpainting & Generative Mask Canvas (`EditorMaskCanvas`):**
   - Brush mask mode with adjustable brush radius, smoothing, eraser, and mask inversion for pinpoint generative fill and object eradication.

3. **36 Tool-Rail Operations (Transform + 13 AI + 13 E-Commerce):**
   - **Core AI Manipulations:** AI Background Remover (`rembg` U2-Net), Generative Fill, Relighting, Shadow Generator, Object Eraser, Super-Resolution Upscaling (2x/4x), Recolor, and Text-to-Image.
   - **E-Commerce Product Studio:** AI Fashion Model generation, Ghost Mannequin extraction, Flat-Lay to live model conversion, Studio Background Staging, Infographic Builder, Product Carousel generator, and Ad Creative designer.

4. **Production Workflow & Export Pipeline:**
   - Non-destructive Version History with granular Undo/Redo snapshots.
   - Interactive Before/After split-slider comparison.
   - Customizable Export Presets (PNG, JPEG, WebP) with variable compression sliders and custom DPI presets.

---

## 4.3 Central Utility Tools Suite (61 Tools)
*A battle-tested collection of 61 standalone web utilities organized in a categorized mega-menu:*

1. **Image Utilities (22 Tools):**
   - Resizer, Compressor, WebP/AVIF Converter, Cropper, Rotator, Watermarker, Favicon Generator, Passport Photo Maker (USA, UK, EU, India, BD formats), Social Media Size Adapter, Batch Image Processor.
2. **PDF Operations Suite (8 Tools):**
   - PDF Merge, PDF Split, Lossless Compress, Rotate Pages, Password Protect, Password Unlock, PDF-to-JPG, JPG-to-PDF.
3. **Text & Content Utilities (4 Tools):**
   - Word & Character Counter, Case Converter (Camel, Snake, Pascal, Kebab, Title), Text Cleaner & Whitespace Sanitizer, Duplicate Line Remover.
4. **SEO & Web Auditing (5 Tools):**
   - Meta Tag Generator, Open Graph (OG) Tag Builder, Robots.txt Generator, XML Sitemap Generator, Live On-Page SEO Analyzer.
5. **Developer & Productivity Utilities (5+ Tools):**
   - Custom QR Code Generator (with branding/color embed), Cryptographic Password Generator, Link Shortener, Markdown Resume Builder.

---

## 4.4 Subscription, Billing & Credit-Safe Ledger

1. **Multi-Gateway Payment Integration:**
   - **Global:** Stripe (Credit Cards, Apple Pay, Google Pay) and LemonSqueezy (Merchant of Record).
   - **Regional (Bangladesh):** bKash (Tokenized Checkout API) and Nagad Payment Gateway.
2. **Credit-Safe Ledger Engine (`Reserve → Stream → Commit / Refund`):**
   - Pre-execution validation reserves expected credits from user wallet.
   - Post-stream settlement commits exact credits consumed based on actual token usage.
   - Automated refunds triggered on network disconnection, timeout, or user abort.
   - Idempotency key locks (`workspace:{msg_id}:attempt:{n}`) eliminate double-spend and race conditions.
3. **Multi-Tier Server-Side Enforcement:**
   - **Free ($0/mo):** 5 daily operations, 5 MB cloud storage, basic tools.
   - **Pro ($9.99/mo):** 500 AI credits, 50 MB storage, unlimited utility tool runs, 10 batch operations.
   - **Business ($29.99/mo):** 1,500 AI credits, 500 MB storage, priority queueing, 100 batch operations, API key access.

---

## 4.5 User Dashboard, File Library & Affiliate Engine

1. **Interactive User Dashboard (`/dashboard`):**
   - Dynamic usage meters (AI credits remaining, cloud storage breakdown, daily operation counts).
   - Recent activity logs, active asynchronous processing jobs, and favorites quick-access.
2. **Central Cloud Asset Library (`/ai/library` & `/dashboard/files`):**
   - Multi-format file storage with instantaneous previews, tagging, batch downloads, and composer reusability.
3. **Affiliate & Referral Tracking:**
   - Unique referral link generation, real-time conversion tracking, commission calculations, and payout request logs.
4. **Enterprise Authentication:**
   - SimpleJWT with 60-minute access token rotation, 1-day refresh token blacklisting, and OAuth2 social login (Google & GitHub).

---

## 4.6 Custom Streaming Markdown Engine & UX Primitives

- Specialized markdown parser engineered specifically for incomplete streaming text:
  - **Collapsible Interactive JSON Tree:** Formats raw JSON responses with syntax highlighting and collapsible nodes.
  - **Dynamic CSV to Sortable Table:** Converts live CSV output into interactive tables with one-click CSV export.
  - **Sandboxed HTML Previews:** Renders isolated HTML previews without injecting scripts or styles into the main application DOM.
  - **Syntax-Highlighted Code Blocks:** Copy-to-clipboard, language indicator, and line numbering.
  - **Theme System:** Zero-flash dark and light theme transitions powered by `next-themes` and Tailwind CSS 4 variables.

---

# 5. Key Engineering Challenges & Solutions

### 1. Zero-Discrepancy AI Credit Ledger
- **Problem:** AI APIs can terminate unexpectedly, timeout, or return rate limits mid-stream. In a naive billing architecture, users are either charged prematurely or the platform absorbs the financial loss.
- **Solution:** Implemented a two-phase commit ledger pattern with Redis-backed idempotency locks and atomic PostgreSQL transactions. Only finalized tokens are deducted; unstreamed allocations are returned immediately.

### 2. Canvas Memory & Multi-Layer Performance
- **Problem:** High-resolution image editing (4K+) in a client-side browser canvas causes memory thrashing, FPS drops, and UI freezing.
- **Solution:** Integrated off-screen HTML5 canvas buffers, offloaded filter mathematics to WebGL via Lena.js, and implemented throttled canvas state updates with debounced history snapshots.

### 3. Parallel Multi-Model Streaming Fan-Out
- **Problem:** Running simultaneous generation across 3 distinct LLMs in the comparison tool caused socket stalls and out-of-order SSE packet delivery.
- **Solution:** Built an asynchronous thread-and-queue multiplexer on the Django backend paired with independent `AbortController` fetch streams on the Next.js client, tracking individual latency metrics in isolation.

---

# 6. LinkedIn Post Version (Ready to Publish)

```markdown
🚀 Proud to announce ToolHub-AI — an enterprise-grade, full-stack AI SaaS platform unifying Generative AI and creator tools under one roof.

As developers and creators, we find ourselves juggling 4 to 5 expensive subscriptions every month: one for AI chat, another for photo editing, and separate tools for routine PDF or file conversions. 

I engineered ToolHub-AI from the ground up to eliminate this fragmentation with a unified, credit-safe ecosystem.

Here is what is running under the hood:

🤖 Multi-Provider AI Workspace (/ai)
• Integrated 15 provider adapters connecting 62+ LLMs (OpenAI, Anthropic Claude 3.5, Google Gemini, DeepSeek R1, Qwen, Meta Llama 3.3, Cloudflare Workers AI & self-hosted Ollama).
• Real-time SSE streaming with "Thinking Process" collapsible accordions, multi-modal vision parsing, and live web search.
• Side-by-Side Model Compare: Benchmark up to 3 competitive models simultaneously with real-time latency (ms) and token efficiency metrics.

🎨 Pro Layer-Based Image Editor & AI Studio (/tools/image-editor)
• Fabric.js 7 canvas engine featuring non-destructive layer management, alignment guides, and WebGL image filters.
• Inpainting canvas with interactive brush masking for generative fill and object removal.
• 36-tool rail with a specialized E-Commerce Studio (Fashion model generation, Ghost Mannequin, flat-lay staging, and product background replacement).

🧰 61 Production Utility Tools
• Comprehensive suites for Image (lossless compression, WebP/AVIF conversion, passport photo maker), PDF (merge, split, protect, compress), SEO tags, and developer utilities.

💳 Credit-Safe Financial Ledger & Multi-Gateway Billing
• Robust atomic Reserve ➔ Stream ➔ Commit/Refund ledger pattern with idempotency keys — zero credit loss on provider failure or stream cancellation.
• Multi-gateway payment support: Stripe, LemonSqueezy, plus localized mobile checkout via bKash and Nagad.

⚙️ Tech Stack & Scale:
• Frontend: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui.
• Backend: Django 6.1 REST Framework, SimpleJWT, Celery, Redis, PostgreSQL 15, Pillow, rembg.
• Infra: Dockerized microservices, Gunicorn multi-workers, Cloudflare Tunnel, ComfyUI.
• Codebase Scale: ~101,000+ lines of code across 143 pages and ~191 API endpoints.

Building this platform provided incredible hands-on experience in distributed event streaming, client-side canvas performance, and high-concurrency billing systems.

🔗 Explore the codebase & live architecture: [Insert GitHub / Live URL]

I would love to hear your thoughts and feedback! 👇

#FullStack #NextJS #Django #ArtificialIntelligence #SaaS #SystemDesign #React #Cloudflare #Docker #OpenSource #BuildInPublic #SoftwareEngineering
```

---

# 7. Portfolio Showcase & Case Study (Ready to Feature)

```markdown
## 🌟 ToolHub-AI — Enterprise Multi-Model AI & Creator Workspace

> **Tagline:** One AI workspace. Everything you need to create.
> **Role:** Lead Full-Stack Architect & Software Engineer
> **Project Type:** Production AI SaaS Platform
> **Live Demo:** [https://your-domain.com] | **Repository:** [https://github.com/your-username/ToolHub-AI]

---

### 📌 Executive Summary
ToolHub-AI is an end-to-end AI SaaS ecosystem consolidating three core digital creative paradigms into a single unified account: an enterprise Multi-LLM Chat Workspace, a professional Layer-based Image Editor with AI inpainting, and an expansive suite of 61 high-performance utility tools. Built to scale with over 101,000+ lines of robust TypeScript and Python code, the platform handles multi-provider LLM routing, real-time Server-Sent Events (SSE) streaming, and atomic credit transactions across international and regional payment providers.

---

### ⚙️ System Architecture & Technology Stack

| Layer | Technologies & Implementations |
|---|---|
| **Frontend Architecture** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Fabric.js 7, Lena.js |
| **Backend Architecture** | Django 6.1, Django REST Framework 3.18, SimpleJWT (Token Rotation), Celery 5.6, Gunicorn |
| **Data & Cache Layer** | PostgreSQL 15 (ACID Data, Wallets, Audit Logs), Redis 7 (Cache, Rate Limiting & Message Broker) |
| **AI Integration Layer** | 15 Custom Provider Adapters, LiteLLM, ComfyUI, rembg (U2-Net), OpenCV, PyPDF |
| **Infrastructure & DevOps** | Docker Compose (6 Microservices), Cloudflare Tunnel (`cloudflared`), Nginx reverse proxy |
| **Payment Gateways** | Stripe, LemonSqueezy, bKash Tokenized Checkout, Nagad API |

---

### 🚀 Key Technical Highlights & Feature Implementations

#### 1. Multi-Provider AI Gateway & Parallel Compare Engine
- **15 Integrated Providers:** Abstracted unified interface supporting 62+ LLMs across OpenAI, Anthropic, Google Gemini, DeepSeek (including R1 Deep Reasoning), Qwen, Meta Llama, Cloudflare Workers AI, and self-hosted Ollama instances.
- **Resilient SSE Streaming:** Low-latency token streaming with custom lifecycle states (`meta` ➔ `delta` ➔ `done`), client-side token refresh recovery, and mid-stream cancellation.
- **Parallel Model Comparison:** Simultaneous query fan-out across up to 3 competitive models with side-by-side latency (ms), token consumption, and response rendering.
- **Smart Streaming Markdown:** Custom parser capable of rendering interactive JSON trees, live CSV-to-sortable tables, LaTeX equations, and sandboxed HTML previews without crashing on partial streams.

#### 2. Canvas Image Editor & AI Product Studio
- **Layer & Filter Engine:** Fully reactive canvas built with Fabric.js 7, supporting non-destructive WebGL filter chains, magnetic snap guides, multi-layer transforms, and zoom/pan viewports.
- **Interactive Masking & Inpainting:** Custom brush-mask canvas for seamless object removal and generative fill.
- **E-Commerce Studio:** 13 dedicated commercial tools including AI Fashion Model generation, Ghost Mannequin extraction, flat-lay staging, lighting adjustments, and ad creative formats.
- **Non-Destructive History:** Full state snapshot tree enabling instantaneous Undo/Redo and interactive Before/After split-slider preview.

#### 3. 61 Modular Utility Tools
- Centralized tool registry routing 61 specialized tools covering image optimization, multi-page PDF operations (split, merge, encrypt), SEO meta generators, and developer utilities.

#### 4. Bulletproof Credit-Safe Ledger Architecture
- Implemented an atomic `Reserve ➔ Stream ➔ Commit / Refund` ledger pattern using PostgreSQL ACID transactions and Redis idempotency locks.
- Guarantees zero credit discrepancies: if an AI provider drops connection or the user halts generation mid-stream, unconsumed tokens are automatically refunded to the user's wallet.
- Cryptographically verified webhook state machines driving all subscription lifecycle events across Stripe, LemonSqueezy, bKash, and Nagad.

---

### 📊 Scale, Complexity & Impact
- **Codebase Scale:** 404 frontend files, 538 backend files (~101,000 LOC total).
- **Surface Area:** 143 unique frontend pages/routes and ~191 production REST/SSE endpoints across 27 Django apps.
- **Deployment Resilience:** Zero-open-port deployment leveraging Cloudflare Tunnels with isolated database, worker, and caching containers.
```
