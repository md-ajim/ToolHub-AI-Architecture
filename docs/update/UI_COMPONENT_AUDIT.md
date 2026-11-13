# UI_COMPONENT_AUDIT.md — ToolHub-AI Route & Component Audit (spec v2 §4–§29)

**Date:** 2026-10-02 · **Scope:** every §29 route + account surfaces + editor + AI workspace.
Legend: ✅ real & complete · ⚠️ real but gap · ❌ missing/misleading.

## 1. Account dropdowns (§4)

| Surface | Real data shown | Missing vs §4 | Actions (all real nav) |
|---|---|---|---|
| Public `Header` UserMenu | name, email, loading skeleton | ❌ plan, credits, usage; ❌ Account/Billing/Usage/Theme/Help items | Profile, AI Workspace, Dashboard, Settings, Log out |
| Mobile menu | links only | ❌ name/email/plan/credits | same destinations |
| AI workspace header | tier badge, credits (∞ if unlimited), daily messages/limit, conditional Upgrade | ❌ name/email in menu | Upgrade, Dashboard, Projects, History, Usage, Profile, Settings, Help, Log out |
| Usage-fetch failure | silently omitted | ❌ no error/empty treatment | — |

**Fix (§4):** one real-data menu contract — avatar, display name, email, plan badge, credit balance, Account, Settings, Billing, Usage, Theme, Help & Support, Sign out; every value from `/accounts/profile/` + entitlements/usage endpoints; never invented.

## 2. Dashboard surfaces

| Route | Backend calls | States | Gaps |
|---|---|---|---|
| `/dashboard/files` | listFiles, getFolders, getUsage, entitlements; upload/delete/download/move/rename-folder | loading/error+retry/empty/per-file queue% | ❌ search, sort, filter, grid/list, preview, pagination; optimistic `file_count` may drift |
| `/dashboard/projects` + `[id]` | getProjects/create/update/delete; getProject; attach/detach/upload/download | spinner/error+retry/empty/disabled actions | ❌ thumbnails (generic icon); ❌ `formatSize` KB-only (R-4); ❌ native `confirm()` on detail delete vs AlertDialog on list; ❌ no archive; ❌ 403/404 conflated |
| `/dashboard/history` | `GET /workspace/history/`, DELETE, real media links | skeletons, search, tool filter, unauth prompt, delete confirm | ❌ **R-3: no error state** (failure renders as empty); ❌ no pagination, status, thumbnails, details/retry |
| `/dashboard/settings` | `GET/PATCH /accounts/profile/`, reset-email flow | skeletons, saving states, optimistic rollback | ❌ load failure leaves blank inputs (no retry); only Profile/Security/Preferences/Notifications — no Appearance/Privacy/Connected/Billing/Usage; email read-only (correct) |

## 3. AI workspace (§10)

- Models/conversations/usage backend-driven; default = first runnable **free** chat model, Auto selectable but never silent default ✅.
- Gaps: ❌ silent Auto fallback when **no** free model exists (spec wants explicit "No free model currently available"); ❌ no skeleton/error if `listModels()` fails; starters only `aria-disabled` while loading.

## 4. Tools

| Tool | Status |
|---|---|
| favicon-generator | ✅ real ZIP extraction, per-file sizes, tab/URL/iOS previews, snippet+copy. ❌ package missing 48px PNG, maskable icons, `favicon-install.html`, `README.txt`; snippet omits android-chrome links; ❌ no shape/text-mode |
| password-generator | ✅ complete (CSPRNG, length/sets/ambiguous-exclude, presets, strength+entropy, history, copy). Nothing fake; nothing missing per §11 |
| qr-generator | ✅ all 7 modes encode for real; PNG+SVG download; copy; EC/colors/reset. ❌ no logo, no margin control (backend supports `border`), no export-size control (backend supports `box_size`) |
| resume-builder | ✅ real `jsPDF` PDF download (not HTML), 3 templates, account CRUD, validation. ❌ rasterized image-PDF while copy claims "ATS-friendly" — claims must change or export must become text-based; ❌ no page-break control (canvas slicing can cut lines) |
| pdf/merge | ✅ real validation/multi/reorder(up-down)/remove/sizes/processing/error/real download. ❌ no drag reorder (§15); ❌ KB-only sizes |
| pdf/compress | ✅ levels, honest no-estimate-before-result, real before/after sizes + incompressible hint. Display units correct here |
| PDF family | ❌ §17 shared `PdfToolShell` abstraction missing — each page hand-rolls UI |
| SEO analyzer | ✅ real DOM-derived checks, thresholds labeled as heuristics, Google preview labeled "Preview only". Correctly omits crawler-truth checks |
| SEO generators | ✅ real Blob downloads (correct MIME/filename), live social previews. ❌ robots sitemap-URL has no validation |
| MarkdownContent | ✅ code+lang, h1–h4, tables (responsive), quotes, copy, retry/regenerate/continue, streaming states. ❌ no LaTeX/HTML/JSON/CSV/YAML/XML structured views, no downloads, headings emitted as `<p>`, no task lists, h5/h6 missing |
| `/ai/library` | ✅ real list/upload/download/delete/folder/note/image-preview. ❌ favorites are localStorage-only; ❌ no PDF/text preview; ❌ grid shows generic icons (no thumbnails); ❌ no rename/move |

## 5. Editor (§19)

Sidebar/inspector exist with registry-driven tools, `InspectorPrimitives`, slim scrollbars, checkerboard, crop affordances. Gaps to close in Phase 4: verify TOOLS/RECENT/EDIT/AI-TOOLS/DESIGN/EXPORT hierarchy vs §19.1, Inspector section hierarchy vs §19.2, shared control normalization (§19.3), swatch color control (§19.4), neutral sliders with value editing (§19.5). No AI routing/capability changes.

## 6. Cross-cutting (§20–§28)

- Design tokens exist (`globals.css` + `lib/design/theme.css`); new code must use semantic tokens, not ad-hoc values.
- Motion exists (`tw-animate-css`); keep short transform/opacity + `prefers-reduced-motion` (already present).
- States standard (§22) exists on files/projects; history/settings must adopt it (R-3 + settings retry).
- Responsive: navbar + homepage + AI top bars fixed for 320px; dashboard/editor/tools still need the §26 viewport pass — no horizontal overflow, no clipped dropdowns.
- A11y (§27): dialogs/menus are Base-UI (focus-trapped, Esc-close); fix heading semantics in MarkdownContent; keep real `<button>`s, labels, visible focus.
- Icons (§28, lucide-only — no emoji found): normalize size/stroke in touched files.
