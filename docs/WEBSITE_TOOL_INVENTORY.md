# ToolHub-AI — Website Tool Inventory Report

**Generated:** 2026-09-27 (evidence-based, counted from source — not estimated)
**Updated:** 2026-09-27 — P0/P1 fixes applied (4 editors built, 2 PDF registry rows added, homepage expanded 8→12)
**Scope:** full website — backend tool endpoints + frontend registry + routes + AI model surfaces
**Sources:** `backend/apps/*/urls.py`, `backend/apps/ai_tools/registry.py`,
`frontend/src/constants/centralToolRegistry.ts`, `frontend/src/app/tools/**/page.tsx`,
`backend/apps/ai_workspace/management/commands/seed_ai_models.py`

---

## 1. Headline totals

| Surface | Count | Status |
|---|---|---|
| User-facing tools (central registry) | **60** | all `available` (58 + `pdf-to-jpg`, `jpg-to-pdf` added 2026-09-27) |
| Dedicated tool pages (`/tools/*`) | **56** | + 1 dynamic `[slug]` page |
| Editor sub-pages (`/tools/*/editor`) | **36** | 32 + 4 built 2026-09-27 (ai-relight, background-generator, expand-canvas, generative-fill) |
| Backend AI operations (`OPERATION_REGISTRY`) | **30** | core → phase4 |
| AI models (ai_tools matrix) | **39** | 16 READY tools |
| Batch operations (Batch Studio) | **7** | bg-remove, enhance, upscale, shadow, recolor, relight, marketplace-resize |
| AI Workspace seed models | **62** (14 mock + 48 official, 10 providers) | mocks gated by `AI_ALLOW_MOCK_MODELS` (default off) |
| Homepage showcases | **12 of 60** + live "Explore all N tools" count | curated featured/popular slice (was 8; expanded 2026-09-27) |

---

## 2. Frontend registry — 58 tools by category

`frontend/src/constants/centralToolRegistry.ts` → `CENTRAL_TOOL_REGISTRY`
(10 featured, 13 popular; every entry `status: "available"`)

| Mega-menu category | Tools |
|---|---|
| Product Photography | **13** |
| Creative Design | 6 |
| PDF Tools | 6 |
| AI Image Tools | 5 |
| Web & Developer | 5 |
| Photo Enhancement | 4 |
| Text Tools | 4 |
| SEO Tools | 4 |
| Convert | 3 |
| Background & Cutout | 2 |
| Resize & Crop | 2 |
| Compress & Optimize | 1 |
| Image Editing | 1 |
| Social Media | 1 |
| Professional Editor | 1 |

### Full tool list (id — name — route)

**Image / AI editing (core business):**
`image-editor`, `img-crop`, `img-rotate`, `img-watermark`, `ai-bg-rm` (Background Remover),
`ai-obj-rm` (Object Remover), `ai-enhance` (Photo Enhancer), `ai-upscale` (Image Upscaler),
`ai-passport`, `ai-mockup`, `ai-product` (Product Image Editor), `ai-gen-fill` (Generative Fill),
`ai-bg-gen` (Background Generator), `ai-expand` (Expand Canvas), `ai-relight` (AI Relight),
`ai-product-studio`, `ai-shadow`, `ai-recolor`, `ai-retouch`, `ai-fashion-model`,
`ai-ghost-mannequin` (Ghost Mannequin), `ai-flat-lay`, `ai-marketplace-resize`,
`ai-product-staging`, `ai-product-photography`, `ai-infographic` (Product Infographic),
`ai-size-chart`, `ai-carousel` (Product Carousel), `ai-social-creative` (Social Creative),
`ai-ad-creative` (Ad Creative), `ai-fashion-retouch` (Fashion Retouch),
`ai-text-to-image`, `batch-editor` (Batch Image Editor)

**Utility:**
`img-resize`, `social-resize` (Social Media Resizer), `img-compress`, `img-convert`,
`webp-conv`, `avif-conv`, `favicon-gen`, `link-short` (Link Shortener), `pwd-gen`,
`qr-gen`, `resume-builder`, `pdf-merge`, `pdf-compress`, `pdf-split`, `pdf-rotate`,
`pdf-protect`, `pdf-unlock`, `word-count`, `case-conv`, `text-clean`, `rm-dupes`,
`meta-gen`, `og-gen`, `robots-gen`, `sitemap-gen`

---

## 3. Backend tool endpoints by app

| App | Tool endpoints | Notes |
|---|---|---|
| `ai_tools` | 12 tool views + job/batch infra (25 paths) | bg-remove, upscale, enhance, object-remove, passport, gen-fill, bg-generate, expand, relight, product-edit, mockup + generic `AIOperationView` |
| `ai_tools` operations | **30** canonical | core(3): background-remove, text-to-image, passport-photo · phase1(7) · phase2(9) · phase3(4) · phase4(5: infographic, size-chart, carousel, social-creative, ad-creative) |
| `image_tools` | **12** ops | resize, compress, convert, crop, rotate, watermark, webp, avif, favicon, product-image, mockup, flip (+ job status/cancel) |
| `pdf_tools` | **8** | merge, split, compress, rotate, protect, unlock, to-image, from-image |
| `developer_tools` | **7** | json-format, base64 enc/dec, url enc/dec, hash, password-generate |
| `business_tools` | **2** | qr-generate, short links (+ redirect) |
| `seo_tools` | **4** | meta, open-graph, sitemap, robots |
| `ecommerce_studio` | infra (15 paths) | presets, workflows, brand-kits, sessions, exports — no standalone tool endpoints |
| `ai` (legacy) | **7** | bg-remove, upscale, enhance, object-remove, bg-replace, passport, product-bg (+ job detail) |
| `ai_workspace` | chat models API (11 paths) | models list, conversations, compare, usage — models are DB-driven |
| `audio_tools` | **0 — STUB** | app exists, `urlpatterns = []` |
| `video_tools` | **0 — STUB** | app exists, `urlpatterns = []` |
| Text tools / resume-builder | **0 — frontend-only** | no backend endpoint found (client-side tools) |

---

## 4. AI model surfaces (not tools, but user-visible)

- **AI Workspace (`/ai`)**: DB-driven via `AiWorkspaceModel`; seed = 62 entries
  (mock 14, openrouter 18, openai_compatible 7, huggingface 6, cloudflare 5,
  anthropic/google/deepseek/openai 2 each, meta 1, self_hosted 3).
  Mock provider gated by `AI_ALLOW_MOCK_MODELS` (default **off**): never listed,
  routed, or executable in production.
- **Image tools (`ai_tools`)**: 39-model capability matrix, quality-gated
  (`VERIFIED_PRODUCTION` only in selectors); 16 READY tools.
- **Batch Studio**: same backend as image tools; 7 operations, per-model costs.

---

## 5. Gaps & problems found (evidence-backed)

### P0 — ~~broken "Open Editor" links (404)~~ ✅ FIXED 2026-09-27
~~4 registry tools have **no dedicated page and no `/editor` page**; their `[slug]`
detail page still renders an **"Open Editor"** button → 404:~~
- ~~/tools/ai-relight → /tools/ai-relight/editor ❌~~ → ✅ editor built (`EditorShell initialTool="relight"`)
- ~~/tools/background-generator → /tools/background-generator/editor ❌~~ → ✅ (`initialTool="background-generate"`)
- ~~/tools/expand-canvas → `/tools/expand-canvas/editor` ❌~~ → ✅ (`initialTool="expand"`)
- ~~/tools/generative-fill → /tools/generative-fill/editor ❌~~ → ✅ (`initialTool="generative-fill"`)
Verified in production build (all 4 routes prerendered). Detail pages were
already served by `[slug]`; only the editors were missing.

### P1 — ~~PDF conversion pages invisible in listings~~ ✅ FIXED 2026-09-27
~~`/tools/pdf/from-jpg` and `/tools/pdf/to-jpg` pages **exist but have no registry
entry** → missing from `/tools` index, mega-menu, search, and `[slug]` related
lists.~~ Registry rows added (`pdf-to-jpg`, `jpg-to-pdf`);
both now appear in listings/search/related. Backend already supported it
(`pdf-to-image`, `pdf-from-image`); only registry rows were missing.

### P1 — ~~homepage shows 8 of 58 tools~~ ✅ FIXED 2026-09-27
~~`ToolsEcosystem` slices `featured || popular` to 8 cards; 50 tools (incl. the
13-strong Product Photography category — the core business) get zero homepage
presence.~~ Now shows **12** curated cards + live **"Explore all N tools"**
count button (N computed from registry, grows automatically).

### P2 — stub apps
`audio_tools` and `video_tools` ship with **empty `urlpatterns`** — dead surface
area. Either implement or remove from any navigation/docs that promise them.

### P2 — frontend-only tools have no server truth
Text tools (4) and Resume Builder run fully client-side. Fine functionally, but
they bypass entitlement/usage metering — confirm this is intended business-wise.

### P3 — legacy `ai` app overlaps `ai_tools`
7 legacy endpoints (bg-remove, upscale, enhance, object-remove, bg-replace,
passport, product-bg) duplicate `ai_tools` operations. If legacy is still
routed, consolidate; if dead, remove to avoid double maintenance.

---

## 6. Counting method (reproducible)

```bash
# registry tools + categories
grep -c 'id: "' frontend/src/constants/centralToolRegistry.ts
# tool pages vs editor pages
find frontend/src/app/tools -name page.tsx | wc -l            # 90 (incl. index)
# backend operations
grep -c '"display_name"' backend/apps/ai_tools/registry.py    # ≈30
# mock vs official seed models
grep -c '"provider": "mock"' backend/apps/ai_workspace/management/commands/seed_ai_models.py  # 14
# stub apps
cat backend/apps/audio_tools/urls.py backend/apps/video_tools/urls.py  # both empty
```

*Report localization: docs/ — complements `MODEL_CAPABILITY_MATRIX.md` (model-level)
with the tool-level view it was missing.*
