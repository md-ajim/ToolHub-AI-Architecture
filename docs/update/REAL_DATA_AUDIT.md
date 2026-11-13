# REAL_DATA_AUDIT.md — ToolHub-AI Real-Data Integrity Audit (spec v2 §2–§3, §33)

**Date:** 2026-10-02 · **Scope:** `frontend/src` + backend `storage/workspace/business_tools/image_tools/pdf_tools` + `accounts` (settings/auth surface)
**Method:** automated pattern search (mock/sample/demo/fake/TODO/setTimeout/Math.random/storage/hardcoded), route-by-route service wiring review, endpoint↔view contract check.
**Verdict:** No systemic fake production data. All dashboard/AI/file/project/history/settings surfaces are backend-driven. Findings below are the only exceptions, each with a fix.

## 1. PRODUCTION DATA BUGS (must fix)

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| R-1 | `frontend/src/app/dashboard/profile/page.tsx:90-91` | Reads `access_token`/`refresh_token` from `localStorage`, but `login()` only writes cookies + `user` JSON → profile refresh after `PUT /accounts/profile/` is silently skipped | Use cookie-backed `refreshUser()` from `AuthContext` (already exists) instead of the `localStorage` token hack |
| R-2 | `frontend/src/app/layout.tsx:93` | `GoogleOAuthProvider clientId={... \|\| 'dummy-client-id'}` ships a dummy credential to production; button renders then fails | Fail closed: hide Google button (or throw at build) when `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is unset |
| R-3 | `frontend/src/app/dashboard/history/page.tsx:63-68` | Load failure only toasts; UI falls through to "No history found" empty state → **network failure looks like empty account** | Add honest error state + Retry (same pattern as files/projects pages) |
| R-4 | `frontend/src/app/dashboard/projects/[id]/page.tsx:43-46` | `formatSize` is KB-only (`(bytes/1024).toFixed(1) KB`) — wrong for MB/GB | Use a proper `formatBytes` helper (shared with files page) |
| R-5 | `frontend/src/components/editor/EditorInspector.tsx:983` | "Logo watermarks and opacity controls are coming soon." — advertised functionality with no handler | Gate behind entitlement or remove until real |
| R-6 | `frontend/src/components/editor/EditorPanelsEcommerce.tsx:863-864` | Tool with no settings panel is still selectable; toast-as-handler | Don't offer unmapped tools, or link to a real panel |
| R-7 | `backend/apps/workspace/views.py` (project members) | Bare `ProjectPermission.VIEWER` reference with no import → `NameError` at runtime when `permission` omitted | Import or remove the reference |
| R-8 | File rename | `PATCH /storage/files/{id}/` accepts only `folder_id`/`project_id` — no `filename` write path; UI rename for files has no backend | Add `filename` to the PATCH serializer/view (validated, owner-scoped) |
| R-9 | History API | `workspace.History` has no `status`/artifact/job-link/thumbnail columns; serializer nests full `File` row (leaks `storage_path`, feeds raw `/media/` bypass) | Short term: honest text rows (current); do not render fake thumbnails/status. Track artifact columns as backend follow-up |

## 2. CLASSIFIED VALID CLIENT STATE (not bugs — do not "fix")

- **UUIDs/keys:** `Math.random()` only in `uuid()`/`createIdempotencyKey()` fallbacks, ref-image ids, crop-region ids, OAuth `state`, robots rule keys.
- **Polling/timeouts:** all `setTimeout`/`setInterval` are real poll cadence (`/ai/jobs`, `/image/job`, batch status, billing re-verify), abort guards, or copied-feedback resets. No simulated backend success.
- **Storage keys (all legitimate):** `ai-pending-*` + payment/OAuth handoffs (`sessionStorage`, consumed once), UI prefs (`toolhub:ai-sidebar-collapsed`, rail/inspector collapse), `toolhub-recent-models`, `toolhub:library-favorites`, `toolhub:resume-draft`, `toolhub_provider_preference`. Auth tokens live in cookies; `localStorage 'user'` is an instantly-revalidated cache.
- **Static config (not user data):** tool registries, presets, plan fallback constants (marked `@deprecated`, canonical = backend), AI starter prompts, SEO heuristic thresholds (labeled inline), homepage showcase slices.
- **Placeholders:** every `placeholder=` is an input hint (`John Doe`, `you@example.com`); real values come from `/accounts/profile/`.
- **Offline-by-design tools:** password generator (WebCrypto CSPRNG), QR payload preview, SEO analyzer (local DOM computation) — real client computation, no fake server claims.
- **Demo labeling:** `useEditorOperation` free-engine notice is explicitly labeled server-demarcated demo text — the honest label the spec requires. Keep.

## 3. MUTATION / REFRESH HYGIENE (verified)

- Success toasts follow awaited service calls or real client artifacts (Blob download, clipboard write) — no success-before-server found.
- No dead buttons found (100+ handlers sampled; disabled states are real `loading`/`!files.length`/entitlement gates).
- File/folder/project mutations revalidate or patch from server responses; upload queue tracks per-file states (§5.4 pattern already present in files page).
- Known drift risk: folder `file_count` patched optimistically without revalidation; `updateFile` move has no rename; storage `DELETE` is hard (schema has soft-delete columns but no API path sets them).

## 4. MANUAL VERIFICATION STILL REQUIRED (§30–§32 — cannot be done statically)

Login → DevTools Network → perform upload/folder/project/history/settings/export flows → inspect payloads → DB rows → refresh/new-tab/private-window persistence → 401/403/404 behavior. No test credentials or running backend were available to this agent; §31 request/response tables and §32 DB row checks must be completed in a live session.
