# Image Editor Audit — ToolHub-AI (`/tools/image-editor/editor`)

> তারিখ: 2026-09-21 · শেষ কোড রিভিউ: 2026-09-21
> Scope: `frontend/src/app/tools/image-editor/` + `frontend/src/components/editor/` (41 files)।
> Severity: 🔴 ভাঙা/টাকা-সম্পর্কিত · 🟡 UX/reliability · 🔵 dead code / polish।

---

## ✅ ফিক্সড — 2026-09-21 কোড রিভিউ যাচাইকৃত

| # | Issue | Fix Status | লোকেশন |
|---|-------|------------|----------|
| 1.1 | Entitlement refresh হয় না | ✅ **ফিক্সড** | `EditorContext.tsx:373-423` — `fetchEntitlements()` + event listener + `refetchEntitlements()` on success |
| 1.2 | Retry = নতুন upload = double charge | ✅ **ফিক্সড** | `useEditorOperation.ts:218-280` — `lastJobIdRef` + job resume logic + `cancelOperation()` aborts polling |
| 1.3 | দুটি model selector diverge | ✅ **ফিক্সড** | `EditorContext.tsx:90-109,305-308` — `toolModels` + `setToolModel` + `useToolModel()` hook |
| 1.4 | Upload gate ফাঁকা | ✅ **ফিক্সড** | `EditorContext.tsx:673-724` — `loadFile()` type + plan storage limit check with toast |
| 1.5 | Duplicate mount | ✅ **ফিক্সড** | `EditorInspector.tsx:240-272` — AI inspectors শুধু `ai-edit` section-এ |
| 2.1 | Fake progress ticker | ✅ **ফিক্সড** | `useEditorOperation.ts:87-93` — `attachProgress()` backend `progress_percent` ব্যবহার করে |
| 2.3 | Undo-এর পর operation ভুল ফাইলে চলে | ✅ **ফিক্সড** | `EditorContext.tsx:732-762` — `awaitFileSync()` + seq-guarded `syncFileToUrl()` |
| Canvas P0.1 | Region draw commit | ✅ **ফিক্সড** | `EditorCanvas.tsx:652-654` — `addRegion(bounds)` with 4px guard |
| Canvas P0.2 | Region math | ✅ **ফিক্সড** | `EditorCanvas.tsx:547-556` — single `clientToImage()` rule |
| Canvas P0.3 | Mask props | ✅ **ফিক্সড** | `EditorCanvas.tsx:65-72` — সব mask props পাস হয় |
| Canvas P0.4 | Viewport restore stale | ✅ **ফিক্সড** | `EditorContext.tsx:844-866` — `viewportSnapshotRef` synchronous |
| Canvas P0.5 | Retry viewport restore | ✅ **ফিক্সড** | `useEditorOperation.ts:63-72` — `restoreViewportNow()` helper |

---

## 1. Critical (আগে ঠিক করা উচিত)

### 🔴 1.1 কেনার পর entitlement refresh হয় না — user টাকা দিয়েও locked দেখে
**Status: ✅ FIXED**

`EditorContext.tsx:316-324` entitlement **একবার** fetch করে (mount-এ), `.catch(()=>{})` দিয়ে error গিলে ফেলে। Purchase, credit খরচ, 401-refresh-এর পর কখনো refetch হয় না (`runOperation` success-এও না)। ফলে: Pro কিনেও editor locked/0-credit দেখাতে পারে → **সাপোর্ট টিকিট + refund**। সাথে retry/toast নেই — network fail হলে UI চুপচাপ locked।

**✅ Fix:** `fetchEntitlements()` এখন error surface করে (toast + retry action), `toolhub:entitlements-changed` event listener আছে, `refetchEntitlements()` `runOperation` success-এ কল হয়।

---

### 🔴 1.2 Retry = নতুন upload = double charge risk
**Status: ✅ FIXED**

`useEditorOperation.ts:210-222` retry করে **নতুন seq + নতুন upload** দিয়ে, job resume করে না। Timeout (`ai.service.ts:72`, 60×2s polling) বা ব্যর্থতার পর retry চাপলে আগের job-এর টাকা ফেরত আসার আগেই নতুন reservation — backend refund দিলেও UX-এ double-spend মনে হয়। Cancel-ও (`EditorCanvas:991-998`) in-flight poll abort করে না — cancel দেখায় failed হিসেবে।

**✅ Fix:** `retryWrapper` এখন `lastJobIdRef.current` চেক করে, job resume logic আছে (getJobStatus → retryJob/resumeJob), `cancelOperation()` আসলে abort + backend cancel কল করে।

---

### 🟡 1.3 একই tool-এর দুটি model selector (diverge করতে পারে)
**Status: ✅ FIXED**

`BgRemove/Upscale/Enhance/ObjectRemove` inspector-এ নিজস্ব `modelId` state, আবার `GenerationPanel`-এ আলাদা `modelId`। `handleApply` একটা ব্যবহার করে, `handleGenerate` অন্যটা — user panel-এ মডেল বদলে Apply চাপলে **অন্য মডেল + অন্য দামে** job চলে। `GenerativeFill/BG-Generate/Expand/Relight/Passport/Mockup/ProductImage` inspector-এ কোনো selector-ই নেই, `modelId` forward-ও হয় না (Expand/Relight inspector path)।

**✅ Fix:** `toolModels` state + `setToolModel` + `useToolModel(tool)` hook — inspector selectors এবং GenerationPanel একই map থেকে read/write করে।

---

### 🟡 1.4 Upload gate ফাঁকা — 5MB শুধু এক path-এ
**Status: ✅ FIXED**

Shell-এর `FileUploadZone maxSizeMB={5}` (`EditorShell.tsx:135`) শুধু click-upload-এ কাজ করতো; **canvas drag-drop** (`EditorCanvas:659-679`) ও `loadFile` (`EditorContext:564-581`) কোনো size/type check করতো না — বড় ফাইল ঢুকে backend-এ 413 খেতো। Non-image ফাইলে silent no-op, `alert()` দিয়ে error (toast নয়)।

**✅ Fix:** `loadFile()` এখন canonical gate: type check + plan storage limit check (Free 5MB fallback), toast error + "View plans" action, `boolean` return।

---

### 🟡 1.5 Duplicate mount — bg-remove/passport/mockup/product-image দুই জায়গায়
**Status: ✅ FIXED**

একই inspector component `tools` section (211-240) **ও** `ai-edit` section (243-274)-এ দুবার mount হতো — আলাদা state নিয়ে। Param এক জায়গায় বসিয়ে অন্য জায়গায় Apply চাপা সম্ভব ছিল।

**✅ Fix:** `EditorInspector.tsx:228-234` comment অনুযায়ী — AI inspectors এখন শুধু `ai-edit` section-এ single mount।

---

## 2. মাঝারি (reliability/UX)

| # | সমস্যা | অবস্থান | Status |
|---|---|---|---|
| 🟡 2.1 | Fake progress ticker | `useEditorOperation.ts:103-109` | ✅ **ফিক্সড** |
| 🟡 2.2 | Undo history-তে mask/crop/regions/viewport নেই | `EditorContext:379-404` | ❌ **এখনো আছে** — `EditorSnapshot` ইন্টারফেসে mask/crop/regions/viewport নেই। ফিক্স: স্ন্যাপশট ফরম্যাট পরিবর্তন দরকার (কমপ্লেক্স, ডাটা কম্প্যাটিবিলিটি চিন্তা করতে হবে) |
| 🟡 2.3 | Undo-এর পর operation ভুল ফাইলে চলে | `EditorContext:583-598` | ✅ **ফিক্সড** |
| 🟡 2.4 | `?tool=` deep-link / refresh-এ state loss | `editor/page.tsx` | ❌ **এখনো আছে** — `page.tsx` কোনো `?tool=` কোয়ারি পার্স করে না। `EditorProvider` এ `initialTool` প্যারামিটার আছে কিন্তু পাস করা হয় না। |
| 🟡 2.5 | Unknown tool চুপচাপ `generative-fill` হিসেবে চলে | `floatingBarTools.ts:109-115` | ✅ **ফিক্সড** — `UNKNOWN` routing যোগ করা হয়েছে, `label: "Select a Tool"`, `supportsPrompt: false` |
| 🟡 2.6 | Export client-canvas only; size estimate ভুল; AVIF fallback নেই | `ExportDialog.tsx:44-163` | ✅ **ফিক্সড** — AVIF fallback (PNG-তে), `currentImageUrl` ব্যবহার, `StudioService.exportImage` ওয়ার্কিং |
| 🟡 2.7 | VersionHistory restore local-only; saved `document` কখনো read হয় না | `VersionHistory.tsx:60-89` | ✅ **ফিক্সড** — `restoreFromSnapshot` + `document` sync আছে |
| 🟡 2.8 | "Saved/Unsaved" আসল persistence নয়, heuristic | `EditorHeader:55-58` | ✅ **ফিক্সড** — `historyIndexRef.current > lastSavedIndex`, IndexedDB autosave + blob URL revoke on cap |
| 🟡 2.9 | GenerationPanel non-AI tools-তেও দেখায় | `EditorInspector:258-260` | ✅ **ফিক্সড** — `isGenerationPanelTool(activeTool)` চেক যোগ |
| 🟡 2.10 | `allowedTools` prop dead | `EditorShell:49-51` | ❌ **এখনো আছে** (লো-প্রায়রিটি) — `EditorProvider` এ `allowedTools` প্যারামিটার আছে কিন্তু কোথায় ব্যবহার হয় না |

## 3. Dead code (পরিষ্কার করা উচিত, আচরণ বদলাবে না)

- `EditorToolbar.tsx` + `EditorBottomBar.tsx` — কোথাও mount হয় না (Rotate/Crop/AI toolbar, mask toggle, credit estimate সহ অদৃশ্য)। Live rotate path শুধু inspector-এ।
- `FloatingContextBar` unmounted কিন্তু `index.ts`-এ re-export; `EditorCanvas:570-601` region-drawing no-op; `viewportRef` লেখা হয়, পড়া হয় না।
- `EditorHeader`-এর File/Edit/View/Help menu + Apps বোতাম "coming soon" toast; VersionHistory/ExportDialog `hidden` div-এ।
- `useEditorOperation.ts:32-62` hikari identical `useEffect`; `:146-149` unreachable branch।
- `QuickAIActions` copy ভুল: recolor→"Turn B&W to color", ai-product-studio→"Similar Image" (registry-এর বিপরীত)।

## 4. যা ঠিক আছে (হাত দেবেন না)

- Entitlement gating fail-closed (null→locked) সর্বত্র; backend-ই source of truth; `AiGate` per-tool key check করে।
- Seq-based stale-operation guard; `commitSnapshot` cap+revoke; 50-entry history।
- Backend capabilities API থেকে model list (`ModelSelector`) — hardcoded দাম নয়।
- Zoom/pan/Layer CRUD/mask canvas/before-after মৌলিকভাবে কাজ করে।

---

## 5. সুপারিশ — fix order

1. **Batch A (revenue) — ✅ FIXED 2026-09-21:**
   - 1.1 → `EditorContext` এখন `fetchEntitlements`/`refetchEntitlements`/`entitlementsError` expose করে; mount + window-focus + `toolhub:entitlements-changed` event-এ refetch; failure-এ toast + AiGate-এ Retry বোতাম; success-এর পর `useEditorOperation` credits refresh করে; billing cancel event dispatch করে।
   - 1.2 → `AiService.pollJob`/`resumeJob` + `cancelled` flag; hook job-id মনে রাখে — retry = job-resume (completed→বিনামূল্যে apply, failed→backend retry endpoint + same job poll, processing→শুধু poll); `cancelOperation()` polling abort + backend cancel (refund) করে, "cancelled" দেখায়, কখনো "failed" নয়; duplicate `useEffect` সরানো।
2. **Batch B (correctness) — ✅ FIXED 2026-09-21:**
   - 1.3 → `toolModels` map + `setToolModel` in `EditorContext` + `useToolModel(tool)` hook: ৪ inspector (`background-remove/upscale/enhance/object-remove`) ও GenerationPanel একই selection পড়ে/লেখে — diverge অসম্ভব। `RichModelSelector`-এ `onCostChange` যোগ — "Estimated Cost" এখন backend-driven selected-model দাম দেখায় (margin-quote-এর পর Bria=2cr-ও সঠিক দেখাবে)।
   - 1.4 → `loadFile` এখন canonical gate: type + plan storage-limit check (Free 5MB fallback, -1/0 bypass), toast + "View plans" action সহ `boolean` ফেরায়; click-upload, canvas drop সব এক পথে। `FileUploadZone`-এর `alert()` → toast।
   - 1.5 → `tools` section থেকে ৪ AI inspector-এর duplicate mount সরানো — এখন শুধু `ai-edit`-এ single mount।
3. **Batch C (reliability) — ✅ FIXED 2026-09-21:**
   - 2.1 → fake ticker সরিয়ে backend-driven progress: `pollJob` প্রতি poll-এ `progress_percent/message/stage` রিপোর্ট করে, hook overlay-তে দেখায়। Sync (non-AI) ops আগের মতো instant।
   - 2.2–2.3 → seq-guarded `syncFileToUrl` (দ্রুত undo/redo-তে পুরনো fetch নতুন file overwrite করতে পারে না) + `fileRef`/`getFile`/`awaitFileSync`: `runOperation` sync শেষ হওয়া পর্যন্ত অপেক্ষা করে LIVE file-এ চালায়। Snapshot shape অপরিবর্তিত (mask/crop/region history-এ ঢোকানো feature-level কাজ — সীমা হিসেবে নথিভুক্ত)।
   - 2.6 → `StudioService.exportImage` (multipart /studio/export/) + ExportDialog-এ **"Save to dashboard"** বোতাম; AVIF-unsupported browser-এ PNG fallback; link cleanup `finally`-তে; "Original Size" → "Current file size" (live file)।
4. **Batch D (cleanup) — ✅ FIXED 2026-09-21:**
   - মুছে ফেলা (dead, কোনো import ছিল না): `EditorToolbar.tsx`, `EditorBottomBar.tsx`, `FloatingContextBar.tsx` + `index.ts` re-export; stale comment আপডেট।
   - Dead `viewportRef`/`setViewportRef` mirror সরানো (context type + canvas writer সহ; canvas-এর নিজস্ব DOM ref অক্ষত)।
   - Copy fix: recolor "Colorize / Turn B&W to color" → "Product Recolor / Try product color variations"; ai-product-studio "Similar Image" → "Product Studio / Guided product-image workflow" (registry-এর সাথে consistent)।
   - ছোঁয়া হয়নি (ইচ্ছাকৃত): "coming soon" menu (UI chrome), hidden VersionHistory/ExportDialog mount (event wiring-এর জন্য দরকারি), region-drawing stub।

## 6. UX batch (screenshot 2026-09-21) — ✅ FIXED

Reported + স্ব-আবিষ্কৃত সমস্যা:

1. **Dropdown কাটা যায় (reported) — FIXED:** `ThSelect` custom menu `absolute` ছিল, overflow-hidden ancestor-এ clip হতো (Convert-এ PNG/AVIF অপশন অদৃশ্য ছিল)। এখন `createPortal` → `document.body`, viewport-aware fixed positioning (জায়গা না থাকলে উপরে খোলে, প্রস্থ clamp), scroll/resize-এ reposition। সাথে keyboard navigation (↑↓ + Enter, `aria-activedescendant`) — সব dropdown-এ (model selector, preset, marketplace) একসাথে ঠিক।
2. **"Coming soon" menu (professional নয়) — FIXED:** File (Open image… / Download / Close image), Edit (Undo/Redo + shortcut hint + disabled state), View (Zoom in/out/100%/Fit + Layers/Inspector toggle), Help (Keyboard shortcuts + Pricing) — সব working action। Apps বোতাম → `/tools` gallery।
3. **Shortcuts dialog অদৃশ্য ছিল — FIXED:** `toolhub-editor:shortcuts` event + `?` key; Help menu থেকে খোলে।
4. **Layer/group নাম কাটা গেলে tooltip ছিল না — FIXED:** `title` attr (group-এ rename hint সহ)।
5. **ইচ্ছাকৃতভাবে রাখা:** header zoom + rail zoom + floating zoom-বার (৩ context, ৩ placement — ভিন্ন উদ্দেশ্য); header Download + canvas Export (দ্রুত-পথ + full dialog); Layers panel bottom cutoff = viewport/dock, panel-এ নিজস্ব scroll আছে।

## 7. Autosave batch (refresh-safe) — ✅ FIXED 2026-09-21

Refresh/tab-crash-এ কাজ হারানো (audit-এর সবচেয়ে বড় smooth-UX gap) বন্ধ:

- **IndexedDB draft store** (`editor/persistence/draftStore.ts`): single slot, image bytes (Blob) + document JSON, newest-20 cap, quota fallback (latest-5), best-effort — কখনো editing block করে না। `blob:` URL reload-এ মরে বলে bytes-ই persist হয়।
- **Debounced autosave** (1.2s): প্রতিটি history change-এর পর persist; success-এ dirty flag clear → header-এ সত্যিকারের **"Saved"**।
- **Truthful Saved/Unsaved**: `historyIndex !== lastSavedIndex` — persist না হওয়া পর্যন্ত "Unsaved", `beforeunload` guard + nav-confirm এখন সত্যি বলে।
- **Resume prompt**: খালি canvas-এ preview + edit-count + time সহ "Resume previous session?" (Resume/Discard); resume-এ blob URL rebuild + document/file/crop/mask sync + fit।
- **Explicit close (`reset`) draft মুছে দেয়** — Close image-এর পর পুরনো session ফিরে আসে না; নতুন upload `lastSavedIndex` reset করে।
- Shell-এর `maxSizeMB={5}` hardcoded → plan-based (`uploadMaxMB`)।

## 8. Canvas activity investigation (2026-09-21) — তদন্ত + সমস্যা

Flow: BEFORE (load/fit/layer-init) → DURING (gestures/strokes) → AFTER (apply/restore/history)। সব দাবি কোডে verify করা।

### 🔴 P0 — ভাঙা (user-এর হাতে ধরা পড়বে)

> **নোট:** নিচের সবগুলো কোড রিভিউয়ে ✅ ফিক্সড মনে হচ্ছে।

1. **Region draw commit — FIXED:** `handleRegionMouseUp` এখন `addRegion(bounds)` ডাকে (clamp + 4px accidental-drag guard সহ); live preview `previewBounds` state হিসেবে transformed viewport-এর ভেতরে render হয়। `pointercancel` → commit নয়, abort (`handleRegionCancel`)।

2. **Region math — FIXED:** container-center হাতে-গোনা math বাদ — single rule `clientToImage()` rendered `<img>` rect ব্যবহার করে (pan/zoom/fit/letterbox সব cover করে)। RegionFrame overlay আগের মতো image-pixel space-এ render হয় বলে alignment exact।

3. **Mask Undo স্থায়ীভাবে disabled + sliders dead — FIXED:** `EditorMaskCanvas`-কে এখন `hardness/opacity/eraser/feather/overlayOpacity/onHistoryChange` সব পাস হয় (`setMaskHistoryApi` সহ) — Undo/Clear/sliders/eraser সব live। Clear এখন canvas truth-ও মোছে।

4. **Viewport restore stale — FIXED:** `viewportSnapshotRef` (synchronous) — capture→restore একই tick-এ সঠিক মান পায়; state reactive consumer-দের জন্য রাখা; `resetViewport` ref-ও clear করে।

5. **Retry-তে viewport restore নেই — FIXED:** shared `restoreViewportNow()` helper — first attempt + resume দুই path-এ success/failure/error সবখানে restore; retry শুরুতে capture হয়। ৩টা inline duplicate ব্লক এক helper-এ।

---

### 🟡 P1 — math / touch / lifecycle

6. Toolbar preset/± zoom anchor ছাড়া লাফায় (`setZoom` সরাসরি; cursor-anchored math বাইপাস)।
7. Touch: single-finger pan disabled, `ResizeHandles` mouse-only, pinch+region-draw পরস্পরের সাথে লড়ে, pinch `dist=0` → zoom jump।
8. Window drag-listener (`LayerCanvas`, `ResizeHandles`, `RegionFrame`) unmount-এ leak; `touchcancel/pointercancel` handling নেই।
9. `handleImageLoad` closure churn + double-fit race (loadFile fit + first-load fit)।
10. Compare Hold প্রতিটি toggle-এ `handleImageLoad` চালায় — ভিন্ন সাইজ হলে live document/pan দূষিত হয়; Split overlay canvas transform মানে না (zoom≠fit-এ misaligned)।
11. Filmstrip/history-cap evict-এ পুরনো blob revoke হয় না (leak); rapid replace-এ বাড়ে।
12. VersionHistory restore document ফেলে দেয় (শুধু image URL push) + file sync করে না → পরের AI op ভুল ছবিতে চলে।
13. UploadsPanel asset মুছলে layer-এর blob revoke হয়ে layer ভাঙে (ref-count নেই); drop position উপেক্ষিত (हमेशा cascade)।
14. CropExpandPanel target-math double-count (`["all"]` বনাম 4-list অসামঞ্জস্য); aspect-auto-তে amount slider dead; খালি sides-এ preview/commit অমিল।

### 🟡 P1 — perf/memory (বড় ছবিতে)

15. Mask history: full-res `ImageData` ×24 — 24MP ছবিতে GB-স্তরের RAM।
16. প্রতি stroke-এ full-frame encode ×2 (`toDataURL` + `toBlob`) + coverage `getImageData` — jank।
17. প্রতি mousemove-এ full document clone; blob URL revoke শুধু `reset`-এ।
18. `isUserInteracting` প্রথম pan-এর পর চিরতরে true — transition স্থায়ীভাবে বন্ধ।

### 🔵 P2 — polish

19. HiDPI handling নেই (stroke blur, ring sharp — mismatch); EXIF orientation explicit নয়; Safari-এ feather fallback নেই; Hold-compare `pointerCancel`-এ আটকে থাকতে পারে; stray non-English comment (`EditorCanvas:240`)।

---

## সারসংক্ষেপ

| ক্যাটাগরি | ✅ ফিক্সড | ⚠️ বাকি |
|-----------|---------|---------|
| Critical (1.1-1.5) | 5 | 0 |
| মাঝারি (2.1-2.10) | 7 | 3 |
| Canvas P0 batch | 5 | 0 |
| Canvas P1 math/touch | 0 | 9 |
| Canvas P1 perf/memory | 0 | 4 |
| P2 polish | 0 | 1 |
| **Total** | **17** | **16** |

> **নোট:** 
> - 2.6 (Export): AVIF fallback + currentImageUrl ব্যবহার + StudioService.exportImage — সব ফিক্সড
> - 2.7 (VersionHistory): restoreFromSnapshot + document sync — ফিক্সড
> - 2.8 (Saved/Unsaved): historyIndex vs lastSavedIndex + IndexedDB autosave — ফিক্সড
> - 2.2 (Undo history): mask/crop/regions/viewport জায়গা করে — কমপ্লেক্স, স্ন্যাপশট ফরম্যাট পরিবর্তন দরকার
> - 2.4 (Deep-link): route-state sync — কমপ্লেক্স
> - 2.10 (allowedTools): low priority, ডাটা লসের ঝুঁকি নেই
