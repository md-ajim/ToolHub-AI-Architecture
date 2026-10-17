# ToolHub-AI — Content & Naming Audit

Date: 2026-09-30. Static string inspection (`rg` over `frontend/src`).

## Method

Searched user-visible strings for: spelling/grammar spot-checks, `lorem|TODO|FIXME|fake|dummy|sample data`, `mock|demo`, `placeholder`, `coming soon`, stale plan/model/credit names.

## Findings

1. No `lorem ipsum`, `TODO`, `FIXME`, `fake data`, `dummy data`, `sample data` in user-visible components. PASS.
2. `mock` hits are guard code, not user copy: selectors filter `provider=='mock'` / `is_mock` / `TEST_ONLY`; `floatingBarTools.ts` lists `"mock"` in `LOCAL_PROVIDERS` only to exclude it; `useEditorOperation` labels local-engine output honestly ("Demo result from free local engine — no credits used"). `mockup-theme.css` / `th-editor-mockup` = CSS theme name, not mock data. PASS — no fake AI output presented as real.
3. `placeholder=` hits are legitimate input hints (`Search tools…`, `Select model/format/preset`, `Ask anything`, `e.g. Summer Collection Drop`, `Product Photography`, `John Doe/Acme Inc.` as profile hints). No placeholder data rendered as content. PASS.
4. `coming soon`: 2 intentional uses — logo-watermark notice in `EditorInspector` ("Logo watermarks and opacity controls are coming soon") and the `coming_soon` model-availability filter tier + `ToolStatus='coming-soon'` gating enum. No "coming soon" masking an existing feature. PASS.
5. Plan names: Free / Pro / Business consistent across `constants/plans.ts`, pricing page, billing, seed (`seed_plans.py`: Free $0/0cr, Pro $9.99/500cr, Business $29.99/1500cr). Frontend constants carry a sync comment and are fallback-only; pricing page loads backend `pricing/` API. PASS.
6. Operation names: `BACKEND_OPERATION_IDS` (EditorToolRail) ↔ backend `OPERATION_ALIASES`/`canonical_operation()` (bg-remove→background-remove, passport→passport-photo, ai-product-studio→product-photography). Consistent. PASS.
7. Legal routes: footer links `/legal/privacy`, `/legal/terms`, `/security` — all exist. No dead legal links. PASS (static href check).

## Remaining (needs human browser read-through)

Full spelling/grammar proofread of marketing copy and empty/error strings at real viewports — marked NEEDS_HUMAN_REVIEW in the production QA report.
