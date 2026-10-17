# ToolHub-AI — PRODUCTION IMPLEMENTATION PLAN

**Date:** 2026-09-28 · **Basis:** `docs/PRODUCTION_DISCOVERY_REPORT.md` (read it first)
**Rules (binding):** no feature deletion without proof + approval; backend
authoritative; no fake data; credit formula untouched; editor preserved;
tests after every phase; before/after regression inventories (§8).

---

## PHASE A — P0 SECURITY (first, blocks production traffic)

| ID | Task | Files | Verify |
|---|---|---|---|
| A1 | Scope storage to owner: `FileListView` → `IsAuthenticated` + `user=` filter; `FileDetailView` → owner check (404, not 403, to avoid oracle) | `backend/apps/storage/views.py` | new unit tests: anon denied, cross-user denied, owner allowed |
| A2 | Workspace comments: add `user=` to project lookups in CommentList/Detail views | `backend/apps/workspace/views.py:235-265` | unit tests: cross-user 404 |
| A3 | PDF validation everywhere: call `validate_pdf_upload()` in all 8 serializers; sanitize upload filename (uuid prefix, no `../`) | `backend/apps/pdf_tools/serializers.py`, `views.py:22-27` | unit tests: oversize/non-PDF rejected, traversal neutralized |
| A4 | Fail-closed `SECRET_KEY`: raise `ImproperlyConfigured` when the insecure default would be used with `DEBUG=False` | `config/settings/base.py:29` | unit test (override_settings) |
| A5 | Decide ONE env source (root `.env` vs `backend/.env`) — owner decision recorded in §6 | env files (owner action) | documented |

Out of code scope (owner ops): rotate any shared secret; `SECURE_*`/HSTS behind HTTPS; explicit ALLOWED_HOSTS/CORS (no `*`).

## PHASE B — AUTH HARDENING + BILLING SAFETY (P1-1…P1-4, credit §4.6/4.7)
- Logout → blacklist refresh (`AllowAny`→`IsAuthenticated` + `RefreshToken.blacklist()`); reset-password blacklists sessions.
- Throttles/lockout on login/register/forgot/reset/OAuth (DRF scoped rates that survive `DEBUG=True`, i.e. set explicitly per-view, not only globally).
- OAuth: enforce `aud/iss/exp` on Google `id_token`; require client id for code exchange; GitHub: drop `GET ?code=` flow, add `state` (PKCE follow-up noted).
- `PASSWORD_RESET_TIMEOUT` set (e.g. 1h).
- Delete-or-unify dead `record_successful_payment` (webhook path canonical).
- Renewal fallback 500 → fail closed or alert.

## PHASE C — API CONTRACTS (P1-5…P1-10, M1–M3)
- `plan_id` query filter honored in billing `PlanPricesView`.
- Affiliate POST payouts: add `created_at` (parity with GET) — introduced this session, fix now.
- Gateway `_gateway_error_response` → `{success:false, message, errors}` shape (keep `error` for back-compat during migration); same for business/developer tools views.
- `previewPreset` via `fetchApi` (refresh-capable) or documented exception.
- Replace hardcoded `/api/v1` with `getApiBaseUrl()` (aiWorkspace.service ×2, AuthContext logout).
- `authApi` dead client: prove zero call-sites (audit says none) → delete per protocol.
- History status: add `status` model field + writer updates + migration + backfill `completed` (enables real badges, fixes P1-14).

## PHASE D — PUBLIC SITE HONESTY + SEO (P2-1…P2-3, audit §SEO)
- Homepage rebalance (hero CTA to tools, flagship deep links, category copy, pricing bullets) — separate UX proposal first.
- Thin pages: about/contact CTA+links; blog detail routes OR remove self-loop links; guides clickable detail OR honest index-only; docs internal links; security/status canonicals; legal contact link.
- Tool pages: `relatedTools` rollout (qr/password/webp/background-remover first), `image-editor` canonical.
- Sitemap: already fixed (/ai out, legal in). OG per-page images deferred (root image ships).
- Schema: keep FAQPage/pricing + Organization + [slug] SoftwareApplication; add Article only if blog detail routes ship.

## PHASE E — A11Y + RESPONSIVE (targeted, no redesign)
- `InspectorRow` → real `<label htmlFor>` (9+ controls; biggest a11y win).
- Icon-button accessible names (ExportPresets, ShortcutsDialog, VersionHistory, AICommandBar, files/history rows, Header trigger).
- `ToolLayout` h1→h3 skip; focus rings on raw ranges; 3 image alts.
- `dashboard/files` table scroll wrapper + truncate + action-bar wrap; history toolbar wrap; editor `lg`-crowding default-collapse; confirm-then-delete duplicate right panel (`CanvasChrome:825` vs `:2007`).
- Reduced-motion already correct — regression-guard only.

## PHASE F — PLATFORM HARDENING (P3, post-launch safe)
- CI workflow (lint+type+unit+build), Docker HEALTHCHECKs, beat-liveness monitor, `QUEUED/PROCESSING older than X` alert.
- Analytics decision (self-hosted collector on stub tables vs vendor) + event taxonomy (Phase 20 list) + consent wording.
- next.config: images remotePatterns, security/caching headers.
- `console.error` → `lib/logger.ts`.
- `allowedTools` enforcement decision; FabricCanvas wire-or-remove; ExportFormat dedup; cheapest-tie-break alignment; MP-scaled quote surfacing; ComfyUI lock heartbeat; `billing_attempt` semantics doc; cancel-confirmation UX.
- QA-email reservation + prod unset (with owner).

## PHASE G — FINAL GATE
Full §8 inventories before/after; backend 39+ suites + frontend tsc/eslint/vitest/build green (except documented pre-existing); manual route audit (/ai compare with QA + Free users, batch end-to-end, affiliate click→payout, help search, footer links); deployment checklist (migrate, seed, env, secrets, HTTPS, CORS, media URLs).

---

## 6. OWNER DECISIONS REQUIRED
1. Env source of truth (root vs backend `.env`) + prod values (SECRET/DEBUG/HOSTS/CORS/CSRF/HTTPS).
2. Removed placeholders stay out until real targets exist (video/audio, careers, social URLs, refund policy) — confirm.
3. Analytics: self-hosted vs vendor.
4. History status migration + ComfyUI/Fabric/dead-code dispositions.
5. Payout fulfillment rail (manual/admin vs Stripe Connect) — v1 is manual.

## 7. EXECUTION LOG
| Phase | Status |
|---|---|
| A (P0 security code) | starting |
| B–G | queued, in order |
