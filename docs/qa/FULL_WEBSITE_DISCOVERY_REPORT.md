# ToolHub-AI — Full Website Discovery Report

Date: 2026-09-30 (UTC)
Scope: entire repo (`frontend/` Next.js 16 + `backend/` Django DRF). Static inspection + `tsc`, `eslint`, `vitest` runs. No live browser run in this environment — browser-dependent rows are marked `RELY_ON_RECORD` / `NEEDS_HUMAN_REVIEW`, never PASS.

## A. Frontend architecture

- Next.js 16.3.0, React 19.2.8, Tailwind v4, shadcn-style `src/components/ui/*` (27 primitives), `sonner` toasts (primary; Radix `toast.tsx` legacy present).
- Routing: App Router, 141 `page.tsx` files. No `src/app/api/**` route handlers — API proxied via `next.config.ts` rewrites (`/api/:path*`, `/media/:path*` → `BACKEND_URL` / `NEXT_PUBLIC_BACKEND_URL` / `http://backend:8000`).
- Auth edge guard: `src/proxy.ts` (Next 16 convention, not `middleware.ts`) checks `access_token` cookie; redirects unauth `/dashboard*` + private `/ai*` → `/login?next=`, authed auth-pages → `?next=` or `/ai`.
- State: `contexts/AuthContext` + `store/auth`, `hooks/useSubscription` (entitlements/credits), React Query client (`lib/query-client.ts`), `lib/api.ts` fetch wrapper (base-URL/media-URL resolution, 401 refresh mutex, backend probe).
- Editor: Fabric.js isolated to `components/editor/canvas/FabricCanvas.tsx` (only dynamic `import('fabric')` in repo). Dual path: Fabric canvas + DOM composite renderer (`LayerCanvas.tsx`), mask canvas, filter pipeline, non-destructive AI layers + `AIImageVersion` backend.
- AI planes: image plane (`apps/ai_tools`, `services/ai.service.ts`, `useEditorOperation`) + chat plane (`apps/ai_workspace`, `modelRegistry.tsx`, gateway SSE).

## B. Backend architecture

27 Django apps. Key planes:

| Plane | App(s) | Mount |
|---|---|---|
| Image AI (registry, capability matching, provider routing, async jobs, credit quote/reserve/refund) | `apps/ai_tools` | `api/v1/ai/` |
| Chat/LLM (DB model registry, gateway SSE, auto-routing, compare, projects) | `apps/ai_workspace` | `api/v1/ai-workspace/` |
| Entitlements + credit ledger (Plan/Subscription/CreditWallet/CreditTransaction/UsageRecord) | `apps/subscriptions` | `api/v1/subscriptions/`, `api/v1/pricing/` |
| Money (Payment/Invoice/Refund/Coupon, Stripe/LemonSqueezy/bKash/Nagad webhooks) | `apps/billing` | `api/v1/billing/` |
| Editor (Project/Version/History/Favorite/BatchJob) | `apps/workspace` | `api/v1/workspace/` |
| Deterministic tools | `image_tools`, `pdf_tools`, `seo_tools`, `developer_tools`, `business_tools`, `audio/video`, `processing`, `ecommerce_studio` | `api/v1/image|pdf|seo|…` |

Authoritative sources: per-op credits `apps/ai_tools/registry.py::AI_TOOL_CREDIT_COSTS` + `quote_credits_for_model()`; provider USD `VERIFIED_USD_PER_OP`; margin guards `config/settings/base.py` (`AI_USD_PER_CREDIT_BUDGET=0.0094`, spend caps); plan prices `Plan/PlanPrice` seeded by `seed_plans.py` (Free $0/0cr, Pro $9.99/500cr, Business $29.99/1500cr); chat costs `ai_workspace/cost_engine.py`. Credit lifecycle is server-side only (no direct quote/reserve HTTP endpoints) with idempotency keys per attempt.

## C–E. Route / component / layout inventory

- 141 routes total: ~23 public core/marketing, 8 auth, 11 dashboard, 6 AI workspace, ~94 tools (32 image/AI tools × landing+editor, 4 editor-only, 9 single-page, 8 PDF, 3 SEO, 4 text, index + `[slug]` fallback).
- `layout.tsx` ×10 (root, dashboard, tools, ai, (auth), admin, pricing, about, contact, help). `robots.ts`/`sitemap.ts`/`opengraph-image.tsx` metadata routes exist.
- `not-found.tsx` ×1 (global only). `loading.tsx` ×0, `error.tsx` ×0, `global-error.tsx` ×0 — gap, fixed in this audit (added).
- Components: `ui/` 27 primitives; `layout/` Header/MegaMenu/Footer/ToolLayout/PublicChromeGate/BottomStatusBar; `dashboard/` 8 (StatCard, ToolCard, QuickTools, RecentProjects/Activity, SectionHeader, LoadingState, EmptyState, CreateProjectModal); `editor/` ~60; `toolhub/` panel kit (Panel, PanelSection, ModelSelector, ModelBadge, Spinner, EmptyState); `batch/BatchEditorApp` (1418 lines) + `fileValidation`; `billing/PaymentMethodSelector`; `ai-workspace/` registry + selector + chat; `features/auth/` forms + OAuth.

## F–J. Navigation / modal / dropdown / form / button inventory

- Navigation: Header (logo→`/`, MegaMenu, GlobalSearch, ThemeToggle, UserMenu) + mobile `Sheet` nav + dashboard sidebar/topnav + editor rails; all internal nav uses `next/link` except 2 raw `<a href="/login">` in OAuth callbacks (fixed → `Link`) and intentional `window.location` for post-auth/payment full reloads.
- Modals: Radix `dialog.tsx` (ExportDialog, ShortcutsDialog, CreateProjectModal), `alert-dialog.tsx` (destructive confirms incl. billing cancel), `sheet.tsx` (mobile nav, panels). No nested-modal abuse found statically.
- Dropdowns/selects: Radix `dropdown-menu.tsx`, `select.tsx` (Batch model/format, ExportDialog, ModelSelector), custom `ThSelect` (editor inspector), `command.tsx` palettes (GlobalSearch, ConversationSidebar), `ExportPresetsPopover`. Model selectors: `ai-workspace/ModelSelector`, `editor/ModelSelector`, `toolhub/ToolHubModelSelector` — all filter `provider=='mock'`/`is_mock`/`TEST_ONLY`.
- Forms: Login/Register/Forgot/Reset/Verify + OAuth + checkout (coupon/provider/plan) + profile/settings + tool params. Validation client + server; error toasts via sonner.
- Buttons: `<Button>` used in 90 files; canonical variants in `ui/button.tsx`. AI actions use `AIActionButton` (loading/disabled/duplicate protection via `useEditorOperation` polling + abort).

## K–O. Loading / error / empty / toast / API inventory

- Loading: `ui/skeleton.tsx` + `dashboard/LoadingState` (cards/list/detail) used in 11 files; `ToolHubSpinner`; AI `AIProcessingOverlay` + job status polling (2s, abort/cancel); checkout/billing/payment-verification states. Gap was route-level `loading.tsx` (added).
- Error: page-level `error` state + retry UI (billing, dashboard, editor inspector explicitly prefers retry over fake CTA); global 404; status page; `utils/errors.ts`. Gap was segment `error.tsx`/`global-error.tsx` (added).
- Empty: `dashboard/EmptyState` + `ToolHubEmptyState` + per-page empties (projects/history/favorites/files/usage/invoices/results/no-models/no-batch-jobs).
- Toasts: `sonner` in 39 files; `Toaster` mounted in root layout; store slice `store/notifications.ts`.
- APIs: all via `fetchApi` → backend; images `ImageService`, AI `AiService/StudioService`, workspace `WorkspaceService`, billing `PaymentService/SubscriptionService`, auth `authApi/auth.service`. No frontend price/model tables (only documented offline fallbacks in `constants/plans.ts`, marked deprecated/fallback-only).

## P–Y. Route groups

- Public: `/`, `/about`, `/contact`, `/pricing`, `/tools/**` (landings + editors), `/blog`, `/blog/:slug`, `/docs`, `/guides`, `/faq`, `/help`, `/partners`, `/security`, `/status`, `/legal/*`, `/category/:slug`, `/search`, `/ai/models`, `/ai/models/:slug`, `/checkout`, `/payments/callback`, `/r/:code`.
- Auth: `/login`, `/register`, `/forgot-password`, `/reset-password`, `/verify-email`, `/auth`, `/auth/callback/google|github`.
- Dashboard (protected): `/dashboard`, `/billing`, `/usage`, `/history`, `/favorites`, `/files`, `/projects`, `/projects/:id`, `/profile`, `/settings`, `/affiliate`.
- Editor: `/tools/:tool/editor` (36 files), `/tools/batch-editor`, `/ai`, `/ai/c/:id`, `/ai/compare`, `/ai/projects`.
- Batch: `/tools/batch-editor` + `BatchEditorApp` + `workspace/batch-jobs/` API.
- Billing: `/pricing`, `/checkout`, `/payments/callback`, `/dashboard/billing`.
- Help/docs: `/help`, `/docs`, `/faq`, `/guides`, `/status`.
- Settings: `/dashboard/settings`, `/dashboard/profile`.
- AI tools/panels: 32 image/AI tool landings+editors + `/ai` workspace + compare + projects + models index.
- Provider/model selectors: 3 (chat, editor, ToolHub generic), all backend-driven.

## Z. Responsive breakpoint strategy

Tailwind default breakpoints (`sm/md/lg/xl/2xl`); Header collapses to `Sheet` mobile nav below `md`; `MegaMenu` desktop-only; containers `max-w-7xl`; editor uses focused shell + rails (desktop) — mobile editor path needs human browser verification. `prefers-reduced-motion` respected in `globals.css` + `theme.css`. No horizontal-scroll guards audited statically — marked NEEDS_HUMAN_REVIEW per viewport.

## Verification status

- `tsc --noEmit`: PASS. `vitest`: 14 files / 112 tests PASS. `eslint`: 141 errors + 90 warnings (pre-existing, mostly `no-explicit-any` in services/types) — documented, not mass-edited.
- Fake-data scan: no `lorem/TODO/fake-data` in user-visible components; `mock` hits are dev-guard filters; `placeholder=` hits are input hints; `coming soon` only for logo-watermark notice + `coming_soon` model filter tier. Dashboard explicitly gates on real data (`hasRealData`).
- Fixes applied in this audit: proxy matcher `/dashboard` root (P1), route `loading.tsx` + `error.tsx` + `global-error.tsx` (P2), OAuth callback `<a>` → `Link` (P3). See production QA report.
