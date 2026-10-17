# ToolHub-AI — Iconography & Visual Language Audit

Date: 2026-09-30 (UTC). Static inspection of `frontend/src` + regression (`tsc` clean, 112 tests pass, touched-file lint clean). Browser/viewport rendering rows are NEEDS_HUMAN_REVIEW, never PASS.

## 1. Icon system inventory — ONE primary family

- **Primary: `lucide-react` (outline, 24px viewBox, stroke-width 2, round caps)** — used in **140 files**; `optimizePackageImports: [lucide-react]` in `next.config.ts`. No competing UI icon library found (no heroicons, react-icons, feather, font-awesome).
- **Tool registry (`constants/toolRegistry.ts`): 100% lucide**, typed `LucideIcon` — every tool row renders `Icon className="w-4 h-4 shrink-0"` + text label. AI groups: Generative=`Sparkles`, Retouch=`User`, Enhance=`Wand2`, Object=`Eraser`, Advanced=`SlidersHorizontal`. Coherent, recognizable, no emoji-style tool icons.
- **Legitimate exceptions (kept):** provider/model **brand marks** (`ProviderIcons.tsx`, editor `ModelSelector` Simple-Icons CC0 paths, `getProviderIcon` with neutral `Cpu` fallback for `mock`/unknown — never a vendor brand for dev models); ToolHub **logo star**; batch shadow-direction dial (`role="img"` + `aria-label`); sticker-emoji data-URI (user canvas content, not UI); ★ in `opengraph-image` (metadata image only).

## 2. Consistency — sizes, weight, alignment

- Size scale observed: `h-4 w-4` (16px) ×191 — standard; `h-5 w-5` (20px) ×90 — toolbar; `h-3 w-3` (12px) ×59 — chevrons/locks; `h-6 w-6` (24px) ×24 — feature/status; `size-4/size-3` normalized via the canonical `Button` (`[&_svg]:size-4`, xs/sm overrides). Matches the audit standard (16 small / 18–20 toolbar / 20–22 primary / 24–32 feature). No oversized-icon abuse found.
- Stroke/weight: lucide default 2px everywhere; the removed inline duplicates also used strokeWidth 2 — visually uniform, now also code-uniform.
- Icon+label: `gap-1.5/2/2.5`, `shrink-0`, `truncate` labels, vertical centering via flex — consistent. Editor header/rail rows all pair icon + text (no ambiguous icon-only toolbar rows in the rail).

## 3. Semantics (spot-verified)

Upload 56 · Download 38 · Search 35 · Settings 16 · Trash2 13 · History 20 · Layers 15 · SlidersHorizontal 5 · Undo2 3 / Redo2 2 · ChevronDown 11 · X 58 · Menu 22 · LogOut 5 · CreditCard 8 · ZoomIn/Out 2 each · Check 32 · XCircle/AlertTriangle 3 each · Info 14 · Loader2 25 (short-action feedback). Correct metaphors throughout; AI concepts use Sparkles/Wand2/WandSparkles consistently; Layers=stacked, History=clock, Properties/Sliders sliders, Undo/Redo curved arrows.

## 4. States, tooltips, a11y

- Undo/Redo (EditorHeader): `Tooltip` (name + shortcut label) + `aria-label` + `disabled:opacity-40` + `disabled` — exemplary; active/pressed via `aria-pressed` on rail rows.
- Icon-only buttons (`size="icon"` ×42): sampled DashboardTopNav, EditorHeader, LayersPanel, ChatComposer — all carry `aria-label` (visibility toggle, layer actions, attach, mic, stop, send) and most pair `title` tooltips. No bare icon-only button found in samples; full 42-file sweep is NEEDS_HUMAN_REVIEW.
- Decorative icons: `aria-hidden` on logo marks, brand paths, thumbnails; **fixed** two decorative text glyphs (✦/→) missing `aria-hidden` in CanvasChrome info card.
- Focus: canonical Button bakes `focus-visible` ring; header menus handle Escape + outside-click; rail rows are native `<button>` with `aria-expanded`/`aria-pressed`.
- Mobile: rail rows are full-width labeled buttons (no hover dependency); icon-only toolbar actions live behind `hidden sm:` breakpoints with labeled equivalents — no hover-to-reveal critical actions found statically.

## 5. Responsive & performance

- Icons scale via Tailwind classes (no raster UI icons, no external icon fonts, no hundreds-asset packs); lucide tree-shaken + import-optimized. No icon-performance issue.
- Clipping/overlap/shrink at 390–1920px: NO_RUN here → NEEDS_HUMAN_REVIEW (note: `shrink-0` + `truncate` + `min-w-0` guards are present on audited rows).

## 6. Fixes applied (semantics-preserving, glyph-equivalent)

| File | Change |
|---|---|
| `EditorHeader.tsx` | 4 hand-rolled chevrons → `ChevronDown`; magnifier → `Search`; target → `Crosshair`; 4-grid → `LayoutGrid` (logo star kept) |
| `EditorToolRail.tsx` | hand-rolled wand → `Wand2` (already imported) |
| `AIActionButton.tsx` | hand-rolled check → `Check` |
| `AIProcessingOverlay.tsx` | local shadow `Sparkles` fn (34 lines) deleted → lucide `Sparkles` import |
| `CanvasChrome.tsx` | `aria-hidden="true"` on decorative ✦/→ glyphs |

Regression: `tsc` clean · vitest 14/112 pass · eslint 0 errors on touched files. No business logic, pricing, registry, or architecture touched.

## 7. Remaining & human-review items

- P3 note: `h-6 w-6` (24px) touch targets in dense LayersPanel rows — below the 44px guideline but standard for desktop editor density with full labels nearby; leave, verify on touch devices.
- NEEDS_HUMAN_REVIEW: full 42-file icon-only-button sweep, viewport rendering at 390/768/1024/1280/1440/1920, tooltip viewport-clipping on edge controls, "remove all labels" cohesion test per page.
