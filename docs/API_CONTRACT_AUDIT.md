# API_CONTRACT_AUDIT.md — ToolHub-AI Endpoint & Delivery Audit (spec v2 §3, §34, §46)

**Date:** 2026-10-02 · Envelope: `{success, message, data[, errors]}` · Base: `/api/v1`.
**Headline:** every frontend-called endpoint in the audited apps EXISTS with auth + ownership. No missing-route breakage. Gaps are semantic (rename, preview, history richness, batch linkage) — listed in §4.

## 1. Endpoint matrix (frontend → backend verdict)

### Storage — all exist
| Call | Route | Auth / ownership | Notes |
|---|---|---|---|
| `listFiles` | `GET /storage/files/` | ✅ auth, user-scoped | No server search/sort/pagination — client-side only |
| `upload` (XHR multipart) | `POST /storage/files/` | ✅ auth, folder/project user-validated, plan limit, 500 MB cap, executable blocklist | `201 {data}` |
| `updateFile` | `PATCH /storage/files/{id}/` | ✅ owner lookup, targets user-scoped | ❌ `filename` NOT writable — **file rename unsupported** |
| `deleteFile` | `DELETE /storage/files/{id}/` | ✅ owner lookup | Hard delete despite `status/deleted_at` columns — no restore path |
| `downloadStoredFile` | `GET /storage/files/{id}/download/` | ✅ owner + existence check, correct `Content-Type`, attachment disposition | §46-correct for download; ❌ no `inline` preview variant, no range requests |
| `getUsage` | `GET /storage/usage/` | ✅ user-scoped | `{used_bytes, file_count}` |

### Workspace — all exist
`dashboard`, `projects` CRUD (soft-delete ✅), `folders` CRUD incl. **rename/move** ✅ (cycle-guarded), project share (token, no expiry), members (⚠️ `ProjectPermission.VIEWER` bare reference → runtime `NameError` when `permission` omitted; no remove-member), comments (top-level list only; `file_id` not project-validated), versions (`POST`-for-update quirk — works, flag for normalization), presets/export-presets (no update/delete), batch-jobs (⚠️ **file IDs discarded on create** — per-file progress impossible), `history` list + soft-delete (minimal columns), tool-only `favorites`, `resumes` CRUD (template whitelist, 3 MB cap).

### Business / Image / PDF tools — all exist
- QR: `POST /business/generate/` (`AllowAny`, stateless) — params `data, error_correction, fill_color, back_color, box_size(1–100), border(0–20), format`; SVG monochrome (documented).
- Short links: create + redirect (click-counted) ✅.
- All 12 image endpoints ✅ (`HasImageToolPermission` ≈ optional-auth, usage-limited); async `202 {job_id}` → poll `GET /image/job/{id}/` (anon jobs UUID-readable, user jobs owner-gated) → cancel ✅. Frontend tolerates backend key aliases; no breakage.
- All 7 PDF endpoints ✅ (`AllowAny`); synchronous `{filename, size, file_data}`; authed `record_tool_result` best-effort. `to-image` returns a ZIP (name the artifact honestly).
- Settings persistence ✅ via `GET/PATCH /accounts/profile/` (nested `profile.preferences` JSONField verified). Auth refresh `POST /auth/refresh/` consistent across fetch/XHR/SSE.

### History page media links — ⚠️ §46 bypass
`resolveMediaUrl(storage_path)` renders raw `/media/…` anchors (DEBUG-gated static serve): no auth, no disposition control, no expiry. Private-file preview must move behind an authorized inline endpoint.

## 2. Model notes

- `storage.File`: UUID, owner FK, folder/project FKs, `parent_file`, `version_number`, `origin_tool`, `status`+`deleted_at` (unused by API). No favorite/thumbnail fields.
- `storage.ProcessedFile`: exists but unreferenced by audited pipelines (jobs use `ImageProcessingJob.output_file` + `/media/temp/`).
- `workspace.Project/Folder`: soft-delete ✅; no favorite/thumbnail. `workspace.History`: `{id, user, tool, file FK, created_at, deleted_at}` — no status/artifact/job/thumbnail columns (§48 unmet at API level).
- `workspace.Favorite`: tool-level only (`unique(user, tool)`).

## 3. Not covered here

Services for `/ai/*`, `/ai-workspace/*`, `/studio/*`, `/seo/*`, `/billing/*`, `/subscriptions/*`, `/affiliates/*`, `/developer/*`, `/admin/*` were inventoried but their backend apps were outside this audit's app scope — verify before touching those surfaces.
