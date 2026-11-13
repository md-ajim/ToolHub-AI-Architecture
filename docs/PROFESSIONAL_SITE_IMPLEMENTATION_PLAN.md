# ToolHub-AI — Professional Website Implementation Plan

**Date:** 2026-10-01
**Scope:** Full audit of reported issues across editor, dashboard, and utility tools + concrete implementation plan.
**Rule:** No mock/fake data. Every fix must work end-to-end against real backend + real database.
**Design rule:** All redesigned surfaces must adopt the existing design system (`frontend/src/lib/design/theme.css` → `th-*` classes + `tokens.ts`). Today the adoption rate in utility tools is **0%** — none of the tool pages under `app/tools/**` use a single `th-*` class.

---

## 0. Master status table

| # | Area | Current state | Priority |
|---|------|---------------|----------|
| 1 | Editor header: user menu + credits (`/tools/*/editor`) | Dropdown menu missing entirely; badge shows Free/0 on any auth hiccup | **P0** |
| 2 | `/dashboard/files`: upload + new folder + download | List/delete real; upload/folder/download buttons dead; endpoints missing | **P0** |
| 3 | `/dashboard/projects` list | Real end-to-end (likely auth/empty-data confusion) | P1 (verify + small gaps) |
| 4 | `/dashboard/projects/[id]` detail | Load/delete real; file actions dead; no add-file flow | P1 |
| 5 | `/dashboard/history` | API real but starved + field-name mismatch → always looks empty | **P0** |
| 6 | `/dashboard/settings` | ✅ Real logic + real data (verified) | — (minor scope notes only) |
| 7 | `/tools/favicon-generator` | Single `.ico` only; no PNG set, no ZIP, no preview, no snippet | **P0** |
| 8 | `/ai` default model + chat box size | No ChatGPT default (Auto routes paid-first for payers); composer small (`max-w-2xl`, 200px cap) | P1 |
| 9 | Password + QR generator UX | Generation real; QR download = zero; dead params; generic UI | P1 |
| 10 | Resume builder PDF | `window.print()` only; no PDF pipeline installed | **P0** |
| 11 | PDF tools (merge/compress/suite) | Download real on all 8; compress is weak; split mislabeled; generic UI | P1 |
| 12 | SEO tools (4) | Backend real; copy-only, no previews/counters/downloads; dated UI | P2 |
| 13 | Cross-cutting: shared components + empty stubs | `useUpload`, `useDownload`, `useUser`, `lib/storage` are **empty files** | **P0** |

---

## 1. Editor header — user details + real credits

### Current state (researched)
- `frontend/src/components/editor/EditorHeader.tsx:89-96` reads **only** `EditorContext.entitlements`. `planName = entitlements?.plan_name || "Free"`, credits line `:248` → `Free / 0 credits` whenever entitlements is null OR the backend saw an anonymous request.
- There is **no dropdown menu** — lines `242-251` render a static `<span>` badge. No `useAuth`, no logout, no email/avatar.
- Backend `GET /subscriptions/entitlements/` (`backend/apps/subscriptions/views.py:94-197`) is **real** (`AllowAny` + anonymous fallback → `Free/free, credits 0`). So any missing/expired `access_token` cookie makes a logged-in user look like `Free / 0 credits`. No mock involved.
- Real user data exists: `GET /accounts/profile/` (`apps/accounts/views.py:6-39`, `IsAuthenticated`). Real wallet data exists in the entitlements payload (`wallet.ai_credits`).
- The main site header is explicitly suppressed on editor routes (`components/layout/Header.tsx:11-14` + `PublicChromeGate`), so the only working user menu never appears in the editor.
- Reusable patterns: `Header.tsx:170-260` (`UserMenu` with Profile/Dashboard/Settings/Logout) and `components/ai-workspace/AiWorkspaceHeader.tsx:85-158` (tier badge + credits with `∞` handling).

### Implement
1. **Frontend only (no backend change):**
   - In `EditorHeader`, consume `useAuth()` (`contexts/AuthContext.tsx`) alongside entitlements.
   - Replace the static badge with a real dropdown (reuse `DropdownMenu` + `UserMenu` pattern): avatar initial, `full_name` + email, plan badge, **wallet-aware credits** (`wallet.ai_credits`, `-1` → Unlimited/∞ via existing `types/payment.ts:179-187` helpers), menu items: Profile, Dashboard, Billing/Upgrade, Settings, Logout. Guest state → Login button.
   - Distinguish states: `entitlements === null` (loading → skeleton) vs `401/guest` (Login CTA) vs real Free (show Free + real 0 balance). Never render `Free / 0 credits` as a guess.
2. **Robustness:** on `401` from entitlements, trigger `refreshUser()` once before falling back to guest UI (kills the "logged in but shows Free" symptom caused by expired access token).
3. **Acceptance:** logged-in Pro user sees name/email/plan/real credits + working logout in every `/tools/*/editor`; logged-out user sees Login; no `0 credits` unless the wallet is truly 0.

---

## 2. `/dashboard/files` — upload, folders, download

### Current state (researched)
- Page: `frontend/src/app/dashboard/files/page.tsx` (178 lines). **List + delete are REAL** (`GET/DELETE /storage/files/`, user-scoped, `backend/apps/storage/views.py:10-30`).
- **Upload button (lines 100-111): dead** — no `onClick`, no file input. `FileUploadZone` (used elsewhere) is a client-only picker that never POSTs. `hooks/useUpload.ts` and `lib/storage.ts` are **empty files**. Backend has **no `POST /storage/files/`**.
- **New Folder button: dead** — no handler. `Folder` model + serializer exist (`workspace/models.py:127-136`) but **zero views/URLs** — orphaned table.
- **Download icon (lines 145-147): dead** — no handler, no download endpoint.
- Tool uploads (PDF/image) write to `MEDIA_ROOT/temp/` and **never create `storage.File` rows** → Saved Files stays empty even after real tool usage.

### Implement
**Backend:**
1. `POST /storage/files/` (multipart): validate type/size against plan limits (`entitlements.limits`), save under `MEDIA_ROOT/user_<id>/`, create `File` row (user, filename, mime_type, size, storage_path, status). Return the `FileSerializer` shape the page already renders.
2. `GET /storage/files/<id>/download/` (user-scoped): stream file with correct `Content-Disposition`. (Alternative: short-lived signed URL — either is fine, pick one and use everywhere.)
3. Folders CRUD: `GET/POST /workspace/folders/`, `PATCH/DELETE /workspace/folders/<id>/` on the existing `Folder` model (support `parent` nesting); add optional `folder` FK on upload so files can be filed.
4. Wire tool pipelines to persist: after PDF/image tool success, create the `File` row (+ `History` row — see §5) instead of temp-only URLs. Add a `?save=true` flag or a `POST /storage/files/from-job/` confirm step — keep it server-side, never trust client paths.
**Frontend:**
5. Implement the two empty stubs properly: `useUpload` (multipart POST + progress + toast + list refresh) and a shared download helper (follow the proven `BatchEditorApp.tsx:118-132` blob-download pattern; do NOT invent a new pattern).
6. Files page: working Upload (drag-drop + picker + progress), New Folder modal (nested), breadcrumb, per-row Download (calls the endpoint), replace hardcoded 1GB bar with real `GET /storage/usage/` (already exists, used by `/dashboard/usage`).
7. **Acceptance:** upload → row appears → download returns the identical file → folder create/nest/delete works → refresh persists everything (DB, not localStorage).

---

## 3. `/dashboard/projects` — list

### Current state (researched)
- Page + `WorkspaceService` + `CreateProjectModal` + backend `ProjectListView` (GET/POST/DELETE incl. soft-delete) are **all real, no mocks**. If it "doesn't work", the cause is runtime (auth cookie, API base URL `lib/api.ts:13-24`, or genuinely empty table) — not missing logic.
- Known gap: `project.files?.length` is normally 0 because nothing ever sets `File.project`.

### Implement
1. Add a diagnostics pass: authenticated empty-state copy ("No projects yet" vs error state with Retry), loading skeletons, and surface API errors instead of silent empty list.
2. `PATCH /workspace/projects/<id>/` (rename/description) — missing today (only GET/DELETE).
3. Add-file-to-project flow (ties into §2 upload: `folder`/`project` selector at upload time).
4. **Acceptance:** create → appears; reload persists; delete → soft-deleted; error states show Retry, never a fake empty screen.

---

## 4. `/dashboard/projects/[id]` — detail

### Current state (researched)
- Load + delete are **real** (`ProjectDetailView.get`, nested `files` via `File.project` FK).
- **Broken edges:** per-file Download/Open buttons (lines 139-144) are dead; `Open in Editor` is hardcoded to `/tools/image-editor/editor` ignoring project context; crash risk `file.mime_type.split('/')[1]` (line 136); `storage_path` never used so no preview/download possible; real projects almost always show "No files yet" (no add-file flow).

### Implement
1. Wire file Download to the §2 download endpoint + preview via `resolveMediaUrl(file.storage_path)` (`lib/api.ts:46-69`).
2. Null-guard `mime_type`/size rendering.
3. `Open in Editor` deep-links with file reference (or hide it until the editor can open a stored file — never a dead link).
4. Add-file-to-project UI (upload picker + existing-files picker).
5. **Acceptance:** every button on the page performs a real action; no dead icons.

---

## 5. `/dashboard/history` — empty-by-design + contract mismatch

### Current state (researched)
- API is **real** (`HistoryListView.get`, soft-delete). Two root causes for "no real data":
  1. **Nothing writes History** except AI jobs (`ai_tools/tasks.py:94-105`). PDF/image/video/business paths never create `History` (or `File`) rows → table permanently empty for those users.
  2. **Field mismatch:** frontend expects `file: { original_name, url }` (lines 17-25, 73, 146-147, 157-166); backend sends `filename` / `storage_path`. Result: always "Processed File", Open/Download icons **never render**, search never matches.

### Implement
1. **Backend:** emit `History` (+ `File`) rows from every tool execution path (pdf, image, video, business, developer, seo — at minimum pdf/image). One shared helper, e.g. `record_tool_history(user, tool, file)`; AI path already does this — generalize it, don't duplicate.
2. **Contract (pick one side, keep one):** either backend aliases `original_name`/`url` in the history serializer, or frontend reads `filename`/`storage_path` + `resolveMediaUrl`. Frontend adaptation is smaller and also fixes search.
3. Keep `DELETE /workspace/history/<id>/` (already real). No `POST` needed (server-side creation by design).
4. **Acceptance:** run a PDF merge → history row appears with real filename, working Open/Download, correct timestamp; delete works; search matches filenames.

---

## 6. `/dashboard/settings` — verified real ✅

- `GET/PATCH /accounts/profile/` (name + `autoSave`/`marketing` preferences) and forgot-password email flow are correctly wired to real endpoints. **No rebuild needed.**
- Optional follow-ups only: expose bio/company/website (today only on `/dashboard/profile`) if desired; in-place password change needs a new endpoint (current email-link flow is intentional); email stays read-only by design.

---

## 7. `/tools/favicon-generator` — multi-device pack + ZIP + preview

### Current state (researched)
- Page (`app/tools/favicon-generator/page.tsx:1-120`) + `ImageService.createFavicon` → `POST /image/favicon/` → Pillow `create_favicon()` (`image_tools/services.py:201-222`) returns **one `.ico`** (16/32/48 embedded). That's all.
- Missing: 180 apple-touch, 192/512 android-chrome, standalone 16/32 PNGs, SVG/mstile, `manifest.json`, `browserconfig.xml`, HTML snippet, ZIP (`jszip` not installed), browser-tab preview (only a raw `<img>`).

### Implement
**Backend** (`image_tools/services.py`, same async-job pattern — keep the polling contract):
1. Render PNG set from the uploaded master (pad to square, keep transparency): `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png` (180, flattened on white/solid option), `android-chrome-192x192.png`, `android-chrome-512x512.png`, `mstile-150x150.png`, multi-size `.ico`.
2. Generate `site.webmanifest` (name, icons w/ sizes+types, theme/background color inputs), `browserconfig.xml`, and the copy-paste HTML `<link>` snippet.
3. Assemble everything server-side into a ZIP — copy the proven `zipfile` pattern from `ecommerce_studio/services.py:91-114` (`build_zip_from_jobs`) / `pdf_tools/conversion_services.py`. Return `{ zip_url, files: [{name, size, url}], html_snippet, manifest }`.
**Frontend:**
4. Result dashboard: per-file checklist grid with sizes, individual downloads + one **Download ZIP** (reuse `BatchEditorApp` blob-download pattern), readonly snippet `<textarea>` + Copy (reuse the SEO pages' copy pattern `seo/open-graph-generator/page.tsx:103-108`), options for background/padding.
5. **Browser preview:** mock browser tab (traffic lights + 16px favicon + title + URL bar), address-bar/bookmark-bar at 16px, plus light/dark + mobile-home-screen tile previews to prove legibility.
6. **Acceptance:** upload once → ZIP contains every file above + manifest + browserconfig; snippet pastes into a real site and shows icons on desktop/mobile tabs.

---

## 8. `/ai` — free default + bigger professional composer

### Current state (researched — important correction)
- There is **no hardcoded ChatGPT default**. New chat and thread both fall back to `AUTO_MODEL_ID` (`ai/page.tsx:29,50`, `ai/c/[id]/page.tsx:30,128`), and backend auto-routing (`ai_workspace/routing.py:217-272`) picks **highest tier first** — so paying users get routed to paid/max models. Free users only see free models because entitlements block the rest.
- Model catalog is **real DB data** (`GET /ai-workspace/models/`); free rows exist (`tier=free`, 0 credits: `xkiro-*`, `openrouter-*-free`, `hf-*free`, …). Free identifier: `tier === "free"` + `credits_per_message === 0` + `locked === false` + `available !== false`. (`xkiro_free_models.json` is **stale, nothing imports it** — ignore it; DB seed is truth.)
- Composer today (`ChatComposer.tsx`): `max-w-2xl` landing / `max-w-3xl` thread, textarea `min-h-48px` capped at 200px autogrow, `rounded-28px` container.

### Implement (frontend-only, no routing change)
1. Default selection = first `tier==='free' && !locked && available!==false` chat model (via existing `sortModelsForDisplay`), keeping `Auto` as a selectable option in `ModelSelector.tsx` — not the initial value. Apply in `ai/page.tsx`, `ai/c/[id]/page.tsx` (and compare empty-state for consistency). Do NOT change backend `select_auto_model` ordering.
2. Bigger professional composer: landing `max-w-2xl → max-w-3xl/4xl`, thread `3xl → 4xl`; raise textarea min-height + 200px autogrow cap; richer container (padding, shadow, focus ring), larger send button, matching `MessageBubble` rhythm; keep mobile toolbar behavior.
3. **Acceptance:** fresh `/ai` shows a named free model selected (never Auto/GPT for any user); composer is visibly larger; paid models still selectable manually and still gated/billed as today.

---

## 9. Password + QR generators — real fixes + premium UX

### Password generator — generation is REAL (server `secrets.choice()`, `developer_tools/services.py:35-49)
**Fix the real bugs first:**
1. Frontend hardcodes all charsets on (`page.tsx:23`) — expose the toggles the API already supports (numbers/symbols/upper/lower).
2. Validate length (raw number input allows 0), add slider + preset lengths.
3. **Strongly consider moving generation client-side** (`crypto.getRandomValues`): instant/offline + removes the privacy negative of POSTing secrets to a server (the page's "never stored" claim is otherwise unverifiable).
**Premium UX:** entropy bits + strength meter + crack-time estimate, show/hide, one-click regenerate, copy with feedback toast, history of last N (in-memory only — never persist passwords).

### QR generator — encode is REAL (Python `qrcode` + Pillow), but:
**Fix the real bugs first:**
1. **Zero download options** — add Download PNG (+ SVG/vector if backend adds it; today backend emits PNG only).
2. **Dead params:** frontend sends `error_correction` + `size` but the serializer drops both and backend hardcodes `ERROR_CORRECT_L` + default geometry (`business_tools/services.py:11`, serializer only declares `data/fill_color/back_color/box_size/border`). Either wire them through or remove them from the UI — never ship non-functional controls.
3. Optionally expose what the backend already accepts: `fill_color`/`back_color`, real `box_size`/`border`.
**Premium UX:** live preview card with quiet-zone, size presets (social/print), logo overlay option, validation of empty/oversized payloads, smooth generate states.

### Both pages
- Restyle into the `th-*` system (panel, input, buttons, spinner, animations) via a shared tool-page shell — see §13. No more one-off `bg-green-50` result boxes.

---

## 10. Resume builder — real PDF export

### Current state
- Fully client-side editor + live HTML preview (nicer than most tools) but **no PDF pipeline**: no `jspdf`/`html2canvas` installed, "Download PDF" = `window.print()` with no print stylesheet, no filename control.
- Single template, no photo, no persistence.

### Implement
1. Install a real client-side PDF path (e.g. `html2pdf`/`jspdf` + `html2canvas`, or `html-to-image`): **Download PDF** renders the resume node to a paginated A4 file with proper filename (`Name_Resume.pdf`), plus export progress state. Add dedicated `@media print` CSS as fallback so print-to-PDF also looks right.
2. Templates (2–3 professional: modern/minimal/executive), typography + spacing + accent-color controls, photo upload, section reorder/show-hide, `localStorage` draft persistence, ATS checklist (contact info, action verbs, length).
3. Mobile: editor-first stacking; preview below is fine but drop the heavy `min-h-[1056px]` on small screens.
4. **Acceptance:** one click → a real multi-page-safe PDF downloads with the right filename; no browser print dialog required.

---

## 11. PDF tools — quality + UX (download already real ✅)

- Download works on all 8 tools (merge/split/compress/rotate/protect/unlock/JPG↔PDF) — **do not rebuild the download flow**.
- Real fixes: (a) `split` page mislabels its button **"Download ZIP"** for a single PDF — fix label; (b) `compress` only runs `compress_content_streams` (near-zero savings on scanned/image PDFs) — add image downsampling/re-encode with quality levels (Low/Medium/High) + before/after size + savings %; (c) merge needs file reorder/remove UI (order = selection order today); (d) route raw `href`s through `resolveMediaUrl`.
- Premium UX: unified result component (filename, size delta, download + process-another), real progress, drag-state polish, all in `th-*`.

---

## 12. SEO tools — modernize (backend real, UI dated)

- 4 tools, all working but copy-paste generic: meta-tag, open-graph, robots, sitemap generators.
- Implement: live **SERP preview** (pixel-width aware title/description counters), **social-card previews** (Facebook/X/LinkedIn), URL validation, **file downloads** (`sitemap.xml`, `robots.txt`, `.html` — copy alone is not enough), sitemap options (priority/changefreq/lastmod, multi-URL handling), multi-group robots builder, copied-feedback.
- Restyle into the shared tool shell (§13). These four should look like distinct professional instruments, not the same form.

---

## 13. Cross-cutting (do first — unblocks everything)

1. **Shared tool-page shell** (`components/tool/`): one `ToolShell` (header, stepper/dropzone, options panel, progress, `ToolResultCard` with download/copy/process-another, related-tools, SEO block) + one success/download component to replace ~15 hand-rolled green boxes (incl. the `bg-green-600` one-off in PDF pages). Migrate tools onto it incrementally.
2. **Fill the empty stubs for real:** `hooks/useUpload.ts` (multipart + progress), `hooks/useDownload.ts` (blob download), `hooks/useUser.ts` (wrap `useAuth`), `lib/storage.ts` — these are imported-or-documented gaps; implement against the §2 endpoints.
3. **Design-system pass:** adopt `th-btn-*`, `th-panel`, `th-input`, `th-badge-*`, `th-spinner`, `th-animate-*` across all touched pages; replace `Loader2`-everywhere and zinc/green one-offs; add reduced-motion-safe transitions for "smooth" feel.
4. **Contract hygiene:** backend file payloads use `filename` + (`storage_path` → `resolveMediaUrl`) everywhere; remove dead props end-to-end (QR size/EC, etc.); every button must either act or not render.

---

## 14. Suggested build order

| Phase | Contents | Why |
|-------|----------|-----|
| **Phase 0 — trust fixes** | §1 editor user menu + credits truth; §5 history contract + population for pdf/image; §9 QR dead params + PNG download; §11 split mislabel | Kills "fake/broken" perception; all small, no migrations except history/file writes |
| **Phase 1 — dashboard data** | §2 upload/folders/download endpoints + `useUpload`/`useDownload` + files page; §3 diagnostics + project rename; §4 detail actions | Makes dashboard real; unblocks projects/files/history population |
| **Phase 2 — flagship tools** | §7 favicon pack + ZIP + preview; §10 real resume PDF + templates; §11 real compress levels + merge reorder | The "wow, professional" deliverables |
| **Phase 3 — polish wave** | §8 AI free default + composer; §9 password/QR premium UX; §12 SEO previews + downloads; §13 shell migration for the rest | Consistent premium finish across the site |

Each phase ends with: `tsc --noEmit` clean, `vitest` green, production `next build` green, plus click-through QA of every touched button at 1366/1440/1536/1280/1024/768 against **real backend + real DB** (never mocks).
