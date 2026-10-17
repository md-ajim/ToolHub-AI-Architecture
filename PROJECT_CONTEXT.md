# ToolHub-AI Project Context Document

**Generated:** 2026-09-10  
**Workspace Root:** `/run/media/md-ajim/Linux_Data/Repo/ToolHub-AI`

---

## Project Overview

ToolHub-AI is a full-stack AI-powered platform that provides an integrated workspace for AI-driven creation and a suite of practical utility tools. The platform combines:

- An **AI Workspace** for chat, reasoning, coding, and vision tasks with multi-provider model support
- **AI Image Generation & Editing** tools (background removal, generative fill, expand, relight, product editing, etc.)
- **Utility Tools** for images (resize, compress, convert, watermark, etc.), PDF (merge, split, protect, compress), text, SEO, developer utilities, and more

The platform is built with a dual-backend architecture:
- **Django REST Framework API** (backend) - Python-based server
- **Next.js Frontend** - React-based client with TypeScript

---

## Tech Stack

### Backend (Python/Django)
| Component | Version/Technology |
|-----------|-------------------|
| Language | Python 3.12 |
| Framework | Django 6.1 |
| API | Django REST Framework 3.18 |
| Auth | SimpleJWT (JWT tokens), OAuth (Google, GitHub) |
| Database | PostgreSQL (production), SQLite (local fallback) |
| Cache/Broker | Redis 7 |
| Task Queue | Celery 5.6 |
| Image Processing | Pillow 12.3, rembg (U2-Net via CPU) |
| PDF Processing | pypdf 6.15 |
| Other | qrcode 8.2, stripe 10.12, requests 2.31 |

### Frontend (TypeScript/React)
| Component | Version/Technology |
|-----------|-------------------|
| Framework | Next.js 16.3.0 (App Router) |
| Language | TypeScript |
| UI Framework | React 19.2.8, Tailwind CSS 4 |
| Component Library | shadcn/ui, lucide-react, @base-ui/react |
| State Management | React Context, Zustand store |
| Auth | Google OAuth, GitHub OAuth, Email/Password |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Docker | docker-compose.yml orchestration |
| Deployment | Cloudflare Tunnel support |
| Model Cache | Local models_cache directory (U2-Net, RMBG) |

---

## Architecture & Structure

### Backend Folder Structure
```
backend/
├── apps/                    # Django apps by feature
│   ├── accounts/            # User model & profile
│   ├── authentication/      # JWT auth, OAuth, password reset
│   ├── ai_tools/            # AI image processing tools
│   ├── ai_workspace/        # Chat/workspace models for AI conversations
│   ├── image_tools/         # Image utilities (resize, compress, etc.)
│   ├── pdf_tools/           # PDF processing utilities
│   ├── subscriptions/       # Plans, subscriptions, credits, usage
│   ├── billing/             # Stripe integration, payments, invoices
│   ├── workspace/           # Projects, folders, comments, versions
│   ├── storage/             # File storage abstraction
│   ├── business_tools/      # E-commerce studio tools
│   ├── developer_tools/     # QR codes, link shortener
│   ├── seo_tools/           # Meta tags, sitemap generators
│   ├── analytics/           # Tracking and metrics
│   ├── notifications/       # Push/email notifications
│   ├── api_keys/            # API key management
│   ├── blog/                # Blog CMS
│   ├── admin_logs/          # Audit trail
│   ├── ecommerce_studio/    # Product image generation
│   └── system/              # Health checks, metrics
├── config/                  # Project settings, URLs, Celery config
├── services/                # Domain business logic
├── shared/                  # Shared utilities (responses, validators, etc.)
├── workers/                 # Celery worker tasks
└── requirements/
    └── base.txt             # Python dependencies
```

### Frontend Folder Structure
```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── api/             # API routes
│   │   ├── auth/            # Authentication pages
│   │   ├── ai/              # AI workspace pages
│   │   ├── dashboard/       # User dashboard
│   │   ├── tools/           # Tool pages
│   │   └── ...              # Other pages
│   ├── components/          # Reusable UI components
│   │   ├── layout/          # Header, footer, navigation
│   │   ├── editor/          # Image editor components
│   │   ├── ui/              # shadcn/ui primitives
│   │   ├── marketing/       # Homepage sections
│   │   └── ...              # Other component categories
│   ├── features/            # Feature-specific logic
│   │   ├── auth/            # Authentication UI
│   │   ├── ai/              # AI workspace logic
│   │   ├── dashboard/       # Dashboard components
│   │   └── ...              # Other features
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Core utilities (api, auth, storage)
│   ├── services/            # API service clients
│   ├── store/               # Client state management
│   └── types/               # TypeScript type definitions
├── public/                   # Static assets
├── components.json          # shadcn/ui configuration
└── next.config.ts           # Next.js configuration
```

### Component Interaction Flow

```
Frontend <-> Next.js API Routes <-> Django REST API <-> Celery Workers
                                      |
                                      v
                               [PostgreSQL/Redis]
                                      |
                                      v
                            [AI Providers (OpenAI, HF, Cloudflare, etc.)]
```

---

## Core Features

### 1. AI Workspace
- Multi-provider LLM chat interface
- Vision capabilities (image understanding)
- Code generation and debugging
- Conversation history and project organization
- Support for OpenAI, Google, Anthropic, DeepSeek, Qwen, Mistral, xAI, Meta, HuggingFace, Cloudflare, Ollama

### 2. AI Image Generation & Editing (`ai_tools` app)
| Tool | Description | Provider |
|------|-------------|----------|
| Background Remove | Remove image backgrounds | RMBG, HuggingFace, ComfyUI |
| Object Remove | Remove specific objects | Cloudflare, ComfyUI, mock |
| Upscale | Enhance image resolution | Real-ESRGAN, ComfyUI, local |
| Enhance | General image enhancement | Local, mock |
| Generative Fill | Inpainting and fill | HuggingFace, Cloudflare, mock |
| Background Generate | Generate new backgrounds | HuggingFace, Cloudflare, mock |
| Expand | Expand canvas size | Local, mock |
| Relight | Adjust lighting | Local, mock |
| Product Edit | E-commerce product editing | HuggingFace, Cloudflare, mock |
| Mockup Generate | Place products in contexts | HuggingFace, Cloudflare, mock |
| Face Restore | Restore/sharp faces | ComfyUI CodeFormer |
| Passport Photo | Create passport photos | Local, mock |

### 3. Image Tools (`image_tools` app)
- **Resize, Compress, Convert, Crop, Rotate, Watermark**
- **Favicon, WebP, AVIF conversion**
- **Product Image** - Generate product shots
- **Flip** - Horizontal/vertical flip

### 4. PDF Tools (`pdf_tools` app)
- **Merge, Split, Compress**
- **Protect, Unlock, Rotate**
- **Convert to/from JPG**

### 5. Other Tools
- **SEO Tools**: Meta tags, sitemap generation
- **Developer Tools**: QR codes, link shortener
- **Business Tools**: Various e-commerce utilities
- **Text Tools**: Word counter, case converter, duplicate remover
- **Social Media Resizer**: Resize for various platforms

---

## Database/State Management

### Database Models (Django ORM)
- **User Model**: Custom UUID primary key user model with OAuth fields
- **Subscription**: Plans, pricing, Stripe integration
- **AI Processing Jobs**: Async job tracking with status, progress, retries
- **Workspace**: Projects, conversations, messages, attachments
- **Storage**: File references, versions, presets
- **Credit System**: Wallet, transactions, usage tracking

### State Management Patterns
- **Frontend**: React Context + TypeScript types, Zustand for local state
- **Backend**: Celery for background processing, Redis for caching/rate limiting
- **Real-time**: Polling-based job status (WebSocket ready for future)
- **Credits**: Reservation-based system to prevent overdrafts

### Key Models Structure

```python
# AI Processing Job (ai_tools/models.py)
AIProcessingJob:
  - id: UUID
  - user: FK to User
  - tool_name: str
  - input_file: FileField
  - output_file: FileField
  - status: queued|processing|completed|failed|cancelled
  - progress_stage, progress_percent
  - provider, model_id
  - reserved_credits, consumed_credits
  - idempotency_key for deduplication

# Workspace Models (workspace/models.py, ai_workspace/models.py)
Project -> Conversation -> Message
  - Non-destructive versioning
  - Comments with position data
  - Folders with hierarchy
  - Export presets
```

---

## AI Provider Architecture

### Provider Adapters (`backend/apps/ai_tools/providers/`)
```
ImageProviderAdapter
├── MockImageProvider (fallback, always available)
├── LocalImageProvider (Pillow transforms, free tier)
├── LocalRMBGImageProvider (U2-Net, CPU)
├── LocalComfuIImageProvider (ComfyUI integration)
├── HuggingFaceImageProvider (HF Inference API)
├── CloudflareImageProvider (Workers AI)
├── OpenAIImageProvider (GPT-image)
└── StabilityImageProvider (SDXL)
```

### Model Registry (`ai_tools/registry.py`)
- Centralized `IMAGE_MODELS` catalog with ~30+ models
- Each model has: `id`, `provider`, `capabilities`, `tier`, `cost`, `quality_score`
- Feature flags for generative operations
- Task-to-model routing with provider preference ranking

### Credit System
```
Credit Types: AI, IMAGE_PROCESSING, PDF_PROCESSING, API, STORAGE
Credit Transactions: ALLOCATION, USAGE, REFUND, PURCHASE, ADMIN_ADJUSTMENT
```

---

## Current State

### Completed/Live Features
- ✅ Full authentication (email, Google OAuth, GitHub OAuth)
- ✅ JWT-based API authentication with SimpleJWT
- ✅ Image tools (resize, compress, convert, crop, rotate, watermark, favicon, webp, avif, product-image, mockup, flip)
- ✅ PDF tools (merge, split, compress, protect, unlock, convert)
- ✅ AI image generation/editing with multiple providers
- ✅ Subscription/Plans with Stripe integration
- ✅ Credit wallet system with reservation
- ✅ Celery background job processing
- ✅ Workspace/projects for organizing work
- ✅ SEO tools, developer tools, e-commerce studio foundation

### Infrastructure Complete
- ✅ Docker Compose with PostgreSQL, Redis, Celery
- ✅ Environment configuration (`.env.example`)
- ✅ SQLite local fallback
- ✅ ComfyUI local inference integration (optional)
- ✅ Media serving configuration
- ✅ Health check endpoints

### API Endpoints (Routes)
```
/api/v1/
├── auth/          - JWT login, register, Google/GitHub OAuth
├── accounts/      - User profile management
├── image/         - Image tools and job status
├── pdf/           - PDF tools
├── seo/           - SEO utilities
├── developer/     - QR codes, link shortener
├── business/      - Business tool APIs
├── workspace/     - Projects, files, versions
├── storage/       - File storage API
├── admin/         - Admin panel access
├── ai/            - AI tools, jobs, models, batch processing
├── studio/        - E-commerce studio
├── subscriptions/ - Plans, pricing
├── billing/       - Checkout, webhooks
└── ai-workspace/  - Conversations, models, usage
```

### Frontend Features
- ✅ Homepage with marketing sections
- ✅ Authentication flow (sign in/up with Google/GitHub/email)
- ✅ Dashboard layout with navigation
- ✅ AI workspace shell
- ✅ Tool pages with editors
- ✅ Pricing page with Free/Pro/Max tiers
- ✅ Legal pages (terms, privacy, cookies)
- ✅ Contact, FAQ, docs, about pages

---

## Known Issues / Observations

1. **No TODO comments found** - The codebase appears to follow clean implementation practices without prominent TODO markers

2. **ComfyUI Local Inference**: Optional feature that requires separate Docker setup; configured via `COMFYUI_ENABLED` env var

3. **Provider Configuration**: Many AI providers (OpenAI, HuggingFace, Cloudflare, etc.) require environment variables to be set - the system handles missing credentials gracefully with mock fallback

4. **Payment Integration**: Stripe integration is set up but real webhook handling may need deployment configuration

5. **Frontend Dev Mode**: Next.js development server runs on port 3000, backend on port 8000; rewrites proxy API calls to backend service

---

## Environment Variables Summary

### Required (Backend)
- `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `SECRET_KEY`

### AI Providers (Server-side only)
- `OPENAI_API_KEY`, `GOOGLE_AI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `QWEN_API_KEY`, `XAI_API_KEY`, `MISTRAL_API_KEY`, `HUGGINGFACE_API_KEY`, `CLDFLARE_ACCOUNT_ID`, `CLDFLARE_API_TOKEN`

### OAuth
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

### Feature Flags (Backend)
- `AI_GENERATIVE_FILL_ENABLED`, `AI_BACKGROUND_GENERATION_ENABLED`, `AI_EXPANSION_ENABLED`, `AI_RELIGHT_ENABLED`, `AI_PRODUCT_EDIT_ENABLED`, `AI_MOCKUP_ENABLED`, `AI_BATCH_ENABLED`

### ComfyUI
- `COMFYUI_ENABLED`, `COMFYUI_BASE_URL`, `COMFYUI_TIMEOUT`

### Frontend (Public)
- `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_GOOGLE_CLIENT_ID`, `NEXT_PUBLIC_GITHUB_CLIENT_ID`

---

## Deployment

The project uses Docker Compose with a profile for Cloudflare Tunnel:

```bash
# Standard deployment
docker compose up -d

# With Cloudflare Tunnel (requires CLOUDFLARE_TUNNEL_TOKEN)
docker compose --profile cloudflare up -d
```

### Services
- **db**: PostgreSQL 15
- **redis**: Redis 7-alpine
- **backend**: Django + Gunicorn
- **celery**: Celery worker for background tasks
- **frontend**: Next.js application

### Management Commands
```bash
python manage.py migrate
python manage.py seed_plans  # Initialize subscription plans
```