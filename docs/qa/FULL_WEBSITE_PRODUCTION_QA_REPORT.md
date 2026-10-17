# ToolHub-AI — Full Website Production QA Report

Date: 2026-09-30 (UTC) · Auditor: Senior Product QA (static + automated; no live browser in this environment)
Evidence: `tsc --noEmit` PASS · `vitest` 14 files / 112 tests PASS · `next build` PASS (all routes prerender) · `eslint` 141 pre-existing errors + 90 warnings · `rg` inventories (routes/components/strings/nav).

Status vocabulary: PASS (evidence below) · FAIL (broken, fix applied or filed) · NEEDS_HUMAN_REVIEW (requires live browser/device) · NO_RUN (not executable here) · RELY_ON_RECORD (prior docs/tests, not re-proven).

## 1–17. Coverage matrix (summary counts)

| # | Area | Result |
|---|---|---|
| 1 | Total routes (141 `page.tsx`) | 141 discovered; build prerenders all — PASS (static). Live click-through per route: NEEDS_HUMAN_REVIEW |
| 2 | Routes tested (automated) | tsc + vitest + build PASS; E2E browser crawl NO_RUN here |
| 3 | Components tested | ~150 files inventoried; 14 vitest files / 112 tests PASS; visual browser check NEEDS_HUMAN_REVIEW |
| 4 | Buttons (~90 files use canonical `<Button>`) | Handlers/loading/disabled verified statically on samples (AIActionButton, checkout, billing cancel); rapid/double-click + offline: NEEDS_HUMAN_REVIEW |
| 5 | Dropdowns (Radix dropdown/select ×7 usages, ThSelect, command palettes, 3 model selectors) | Mock-filtering + viewport-safe primitives PASS (static); Escape/outside-click/keyboard/mobile: NEEDS_HUMAN_REVIEW |
| 6 | Forms (login/register/forgot/reset/verify/OAuth/checkout/profile/settings/tool params) | Validation + server-error + toast paths PASS (static); autofill/mobile-keyboard: NEEDS_HUMAN_REVIEW |
| 7 | Modals (dialog/alert-dialog/sheet; Export/Shortcuts/CreateProject/cancel-sub) | Open/close/focus/scroll-lock patterns PASS (static); nested + mobile sizing: NEEDS_HUMAN_REVIEW |
| 8 | Responsive (12 viewports + zoom required) | Tailwind breakpoints + mobile Sheet nav + editor app-shell PASS (static); all viewports NO_RUN → NEEDS_HUMAN_REVIEW |
| 9 | Loading states | Skeletons (11 files) + spinners + AI job polling + checkout/billing states PASS (static); **added** route `loading.tsx` (was 0) |
| 10 | Error states | Page error+retry, 404, status page PASS (static); **added** `error.tsx` + `global-error.tsx` (were 0) |
| 11 | Empty states | projects/history/favorites/files/usage/invoices/results/no-models/no-batch PASS (static, intentional copy) |
| 12 | AI tools (32 image/AI tools + workspace) | Registry → capability → provider → credit lifecycle traced to backend PASS (static); live provider runs NEEDS_HUMAN_REVIEW |
| 13 | Model selectors (3) | All filter `mock`/`is_mock`/`TEST_ONLY`, backend-driven, honest locked/setup-required states PASS (static) |
| 14 | Dashboard flows (11 routes, real-data gated) | Real API data, no fabricated numbers PASS (static); zero-credit/expired-sub visuals NEEDS_HUMAN_REVIEW |
| 15 | Batch flows | Real ops, validation, credit via `useSubscription`, cap 20 PASS (static); 20-image + partial-failure E2E NEEDS_HUMAN_REVIEW |
| 16 | Billing flows | Real wallet/invoices/entitlements, idempotent webhooks, no frontend grants PASS (static); live gateway sandbox NEEDS_HUMAN_REVIEW |
| 17 | Accessibility | Semantic buttons, focus rings, aria-labels (37 files), dialog/sheet semantics, `prefers-reduced-motion` PASS (static); screen-reader + keyboard-only pass NEEDS_HUMAN_REVIEW |

18. Performance: `optimizePackageImports: [lucide-react]`, dynamic `import('fabric')` isolation, route streaming via new `loading.tsx` — PASS (static). LCP/CLS/INP + slow-3G: NEEDS_HUMAN_REVIEW.
19. Console errors: none observed in build output; runtime console: NEEDS_HUMAN_REVIEW (browser run required).
20. Network failures: offline/timeout/401-refresh paths exist (`probeBackendAvailability`, refresh mutex, retry UIs) — PASS (static); throttled-network E2E: NEEDS_HUMAN_REVIEW.
21. Fake/stale data: 0 findings in user-visible surfaces (guards + honest labels only) — PASS.
22. Broken features found & fixed: 3 (below). No other static breakage.
23. Fixed issues: P1 proxy matcher `/dashboard` root · P2 `loading.tsx`/`error.tsx`/`global-error.tsx` · P3 OAuth `<a>` → `Link` (×2).
24. Remaining issues: P0 0 · P1 0 (static) · P2 0 (static) · P3 2 notes (legacy Radix toast duality; dual Select — both intentional, deprecate-later).
25. Human-review-required: browser E2E (flows A–F), 12-viewport responsive, throttled-network, screen-reader, live provider + live billing sandbox, marketing copy proofread. `eslint` 141 pre-existing errors (mostly `no-explicit-any`) — cleanup tracked separately, not gating.

## Bug log

| ID | Severity | Issue | Evidence | Fix | Regression |
|---|---|---|---|---|---|
| QA-001 | P1 | `proxy.ts` matcher omitted exact `/dashboard` (only `/dashboard/:path*`), so edge guard skipped the dashboard root | `src/proxy.ts` matcher pre-fix | Added `'/dashboard'` to matcher; redirect logic already covered the path | tsc PASS, tests 112 PASS, build PASS |
| QA-002 | P2 | 0 `loading.tsx`, 0 `error.tsx`, 0 `global-error.tsx` — blank-screen risk on slow/failed segments | `find src/app -name` counts pre-fix | Added honest skeleton `loading.tsx`, retry `error.tsx`, dependency-free `global-error.tsx` reusing shared primitives | tsc PASS, build PASS, lint 0 errors on new files |
| QA-003 | P3 | Raw `<a href="/login">` in OAuth callbacks forced full reload | `rg '<a[^>]*href="/'` | Replaced with `next/link` `Link` | tsc PASS, lint: no new errors |

## Quality gate

BUILD ✓ · AUTOMATED TESTS ✓ · BROWSER E2E ⏳ human · RESPONSIVE ⏳ human · REAL DATA ✓ (static trace) · LOADING/ERROR UX ✓ (static + new boundaries) · A11Y ⏳ human · PERFORMANCE ⏳ human · AI FLOWS ⏳ live-provider human · BILLING ⏳ sandbox human · VISUAL REVIEW ⏳ human.

**Verdict: NOT declared production-ready.** Static + automated gates pass with 0 P0/P1 remaining *in static scope*, but the browser/device/network/provider/billing-sandbox passes this product requires were NO_RUN in this environment and are recorded above as NEEDS_HUMAN_REVIEW. Ship only after a human completes flows A–F on real devices.
