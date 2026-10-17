# Phase 6 — Frontend Payment UX/UI Placement Report

Date: 2026-09-30 (UTC). Regression: `tsc` clean · vitest 14/112 pass · `next build` pass (`/pricing`, `/checkout`) · pricing lint clean · 0 `alert()` in pricing/checkout.

## Problem (per screenshot)

The pricing page rendered `PaymentMethodSelector` (incl. `stripe` test/unavailable rows) **above** the plan cards, and prices rendered as `$$9.99` — a payment-gateway look instead of SaaS pricing.

## Architecture implemented

```
PricingPage (WHICH plan: Free/Pro/Business + Monthly/Yearly + comparison + CTA)
  → /checkout?plan=pro&interval=monthly (HOW to pay)
      → OrderSummary (server price/currency/credits/total) + PaymentMethodSelector
      → single dynamic CTA → provider checkout → backend verification → billing
```

## Changes in this pass (on top of the checkout/selector foundation in-tree)

1. `pricing/page.tsx`: subscription-aware CTAs — active-plan card shows disabled `Current plan` + `Manage billing` link (backend `SubscriptionService.getSubscription()`, never local inference); logged-out users always see purchase CTAs via `effectivePlanCode`.
2. `pricing/page.tsx`: coupon `alert()`s → inline `role="alert"/"status"` messages with server currency via `formatCurrencyMinor`; hardcoded `$/100` math removed.
3. `pricing/page.tsx`: `Loading plans...` text → 3 skeleton cards (`Skeleton`, stable shape, `aria-busy`); coupon `<input>` → design-system `Input`.
4. Verified pre-existing foundation: single `PaymentMethodSelector` usage (checkout only), `fieldset`+`legend`+native radios, backend `configured` gating (`providers_*.py` credential checks, `ProviderListView`), `pickPrice` provider-currency matching + mismatch note, selection-before-creation, provider memory with backend-wins, friendly (non-raw) errors, backend-driven states, no optimistic activation, mobile order (summary first), one dynamic CTA.

## Acceptance criteria (§31)

All 21 boxes check out statically: plan-selection pricing; no providers in cards; dedicated checkout method section; LS/bKash/Nagad selectable; availability/price/currency from backend; selection before creation; one CTA; provider UI only when relevant; backend-driven status; no optimistic activation; billing separate; subscriber state; mobile; a11y; no duplicate selector; design system preserved; functionality intact.

## Human-review items

Live card/wallet sandbox runs, cancelled/expired redirect visuals, mobile checkout at 390px, screen-reader radio pass. Pre-existing lint nits in checkout (`set-state-in-effect`, missing `params` dep) left untouched — tracked with the repo's 141 pre-existing lint errors.
