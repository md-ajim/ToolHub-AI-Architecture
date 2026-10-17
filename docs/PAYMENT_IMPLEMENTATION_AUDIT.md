# PAYMENT IMPLEMENTATION AUDIT — ToolHub-AI

**Date:** 2026-09-28 · **Phase:** 1 (read-only, no code modified)
**Scope:** existing billing architecture, models, APIs, pricing, credit system,
payment code, conflicts/gaps, implementation plan for Lemon Squeezy + bKash + Nagad.

---

## 1. EXISTING BILLING ARCHITECTURE

### 1.1 Apps & responsibilities
| App | Role | Key files |
|---|---|---|
| `subscriptions` | Plans, prices, subscriptions, entitlements, credit ledger, webhooks record | `models.py`, `services.py`, `views.py`, `pricing_urls.py`, `management/commands/seed_plans.py` |
| `billing` | Provider abstraction, Stripe provider, checkout, webhooks, payments, invoices, refunds, coupons | `providers.py`, `services.py`, `views.py`, `webhooks.py`, `models.py`, `urls.py` |
| `authentication` | Register/login/OAuth (no payment coupling except free provisioning) | `services.py:create_user_account` |
| `affiliates` (new, this session) | Referral tracking/commission/payouts (unrelated to checkout flow) | `services.py`, `views.py`, `urls.py` |

### 1.2 Provider abstraction (EXISTS — extend, do not duplicate)
`billing/providers.py:7` `PaymentProvider(ABC)` already defines the exact interface
the payment spec asks for: `create_customer`, `create_checkout_session`,
`cancel_subscription`, `update_subscription`, `get_subscription_status`,
`create_refund`. `StripeProvider` implements it (`providers.py:33`), selected via
`get_provider()` (`providers.py:147`). New providers subclass this ABC.

### 1.3 Data models (all present, no new core tables needed)
- **Plan / PlanPrice** (`subscriptions/models.py`): code, name, features JSON,
  `billing_interval`, `amount` (minor units), `provider_price_id`, active flags.
- **Subscription**: user, plan, provider, `provider_subscription_id`,
  status, period start/end, `cancel_at_period_end`. No `ended_at` — uses
  `expires_at` (`services.py` webhook handler).
- **CreditWallet / CreditTransaction** (`subscriptions/models.py:135-173`):
  idempotency-keyed ledger (`idempotency_key` unique, `balance_after`,
  non-negative DB constraint). Types include `purchase` (`TransactionType.
  PURCHASE`, `models.py:152-156`).
- **Payment / Invoice / Refund** (`billing/models.py:27-130`): user, amount
  (minor), currency, gateway, status, `transaction_id`, `provider_payment_id`.
- **Coupon / Promotion** (`billing/models.py`): generic discounts, validated
  via `coupons/validate/`, applied at checkout. Not affiliate-tied.
- **WebhookEvent** (`subscriptions/models.py:201`): `(provider, event_id)`
  unique implicitly via `event_id unique=True`; status pending/processed/failed
  + payload hash. Used by Stripe path (`webhooks.py:45-59`).

### 1.4 API surface (verified against `config/urls.py` + frontend callers)
- `POST /api/v1/billing/checkout/` — server resolves plan + price + coupon,
  returns `checkout_url` only. Frontend never prices (`pricing/page.tsx:97-117`).
- `POST /api/v1/billing/webhooks/stripe/` — signature-verified (secret),
  idempotent on provider event/invoice IDs.
- `GET /billing/{plans,payments,invoices}`, `plan-prices/?plan_id=`,
  `coupons/validate/`, `subscription/upgrade|downgrade`, `refunds/`, `summary/`.
- Frontend: `/pricing` (Stripe redirect checkout + coupons), `/dashboard/billing`
  (plan, balances, payments, invoices, cancel), no dedicated success/cancel
  pages (relies on `?success=true` / `?canceled=true` query handling).

### 1.5 Credit lifecycle (authoritative, audited previously — do not touch)
Reserve-on-enqueue → hold → success consumes (`consumed=reserved`, no second
debit) → failure/cancel/expire refunds via per-attempt idempotency keys +
state-machine guards + 300s sweeper. QA bypass centralized on `is_qa()`.
Renewal allocation idempotent on provider invoice reference. Known quirk
(preserved): `refund_minor_to_credits` 100:1 truncation, isolated.

### 1.6 Pricing source of truth (verified, DO NOT hardcode)
Seeded via `seed_plans`: **Free $0 / Pro $9.99 mo ($89 yr) / Business $29.99 mo
($299 yr)** with `monthly_credits` 0/500/1500. DB (`Plan`/`PlanPrice`) is
authoritative; frontend reads it; provider mapping today = Stripe
`provider_price_id` per price row. Renewal fallback (`500`) now logs a warning
instead of minting silently.

### 1.7 What does NOT exist (greenfield scope)
**Zero** Lemon Squeezy / bKash / Nagad code, models, endpoints, env vars,
tests, or docs anywhere in backend, frontend, or docs (verified by grep).
No success/cancel pages. No payout rails (affiliate payouts are manual/admin).
No analytics event taxonomy for payments. No CI.

---

## 2. CONFLICTS / GAPS

1. **Single-provider assumption.** `get_provider()` returns one (Stripe) provider;
   checkout has no `provider` selector; `Payment.gateway` is a free string
   (no choices) — workable, but provider-scoped behavior needs a selector.
2. **Plan↔provider mapping lives in `PlanPrice.provider_price_id`** (Stripe-only
   semantics). Multi-provider needs a mapping layer (variant/code per provider
   per price) — must not overload this column ambiguously.
3. **Currency: USD-only in practice.** Models carry `currency` (default USD);
   bKash/Nagad require BDT. Plan prices are USD amounts — BDT pricing needs a
   decision (same minor-unit rows in BDT vs converted display).
4. **Renewal/upgrade/downgrade/cancel flows are Stripe-shaped** (Stripe
   subscription IDs, Stripe portal assumptions in UI copy). Each new provider
   needs its own lifecycle mapping.
5. **No sandbox/test-mode separation** for payments (only `sk_test_dummy`
   fail-open when unconfigured). bKash/Nagad sandbox vs production URLs must
   be explicit per environment.
6. **Pre-existing failures unrelated to payments** (for regression baseline):
   `test_celery_retry_is_not_converted_into_failure_refund`,
   8× `ecommerce_studio/test_studio.py` (verified identical-or-better vs
   pristine worktree). Full backend suite otherwise green (571 passed at last
   full run); frontend 112/112, tsc/eslint clean, build exit 0 (144 pages).

---

## 3. PROPOSED IMPLEMENTATION PLAN

**Design principles:** extend `PaymentProvider` ABC; DB is source of truth;
server-side price resolution always; webhooks authoritative; idempotency at
provider-event, payment, subscription, and credit-grant levels; no frontend
pricing; no secrets in frontend or logs; per-provider capability flags.

### Phase 2 — Abstraction + mappings (no provider SDKs yet)
1. `PaymentProvider` ABC: add `provider_name`, `supports_*` capability flags
   (recurring, one_time, refunds, webhooks, sandbox), `get_config_status()`.
2. New `PlanProviderMapping` model: `(plan_price, provider, provider_product_id,
   provider_variant_id, currency, sandbox)` unique per triple. Admin-registered.
3. `GET /billing/providers/` — public capability/config endpoint driving the
   frontend payment-method selector (no secrets).
4. Checkout API accepts `provider`; resolves price server-side; rejects
   unknown/unmapped/disabled providers with structured errors
   (`PLAN_NOT_AVAILABLE`, `PAYMENT_PROVIDER_UNAVAILABLE`).
5. Unit tests: mapping resolution, currency validation, disabled provider.

### Phase 3 — Lemon Squeezy
1. `LemonSqueezyProvider(PaymentProvider)` — checkout (store+variant),
   subscription get/cancel, refund; HMAC-SHA256 webhook verification
   (`X-Signature`).
2. Webhook events mapped from official names (order_created/paid,
   subscription_created/updated/cancelled/resumed/expired,
   subscription_payment_success/failed, refund events) → internal
   Payment/Subscription/CreditTransaction via existing canonical helpers
   (`allocate_renewal_credits`, entitlement activation).
3. State mapping incl. past_due/unpaid grace + cancel-at-period-end
   preservation. Renewal credits exactly once per billing event.
4. Tests: signature vectors, duplicate/replayed webhooks, activation,
   renewal, cancel, refund, amount/currency tamper, wrong-user isolation.
   Docs: `docs/PAYMENT_SYSTEM.md` Lemon Squeezy section + env template.

### Phase 4 — bKash
1. `BkashProvider` — create (token grant under the hood), execute, query
   (`/payment/status`-equivalent per current docs) + callback verification.
2. Frontend: method selector → backend checkout returns paymentID +
   gateway URL → JS interaction → backend verify-before-grant (amount,
   currency=BDT, status, merchant, user/order binding, replay guards).
3. Tests incl. amount mismatch, duplicate callback, fake success rejection.

### Phase 5 — Nagad
1. `NagadProvider` — initialize/verify per current docs (sensitive fields,
   callback decrypt/verify as documented).
2. Same verify-before-grant + tests as bKash.

### Phase 6 — Frontend + security audit
Method selector (backend-driven list), pending/verifying/success/failure
states (poll `GET /payments/{id}/`, never trust redirects), billing page
provider column, history provider labels. Adversarial test battery
(§37–38 of the command): fake payment/price/plan, duplicate/replayed
webhooks, invalid signature, wrong user/amount/currency, expired payment.

### Phase 7 — Docs, env, regression
`docs/PAYMENT_SYSTEM.md`, `docs/PAYMENT_PROVIDER_SETUP.md`,
`docs/PAYMENT_SECURITY.md`; `.env.example` placeholders only; full backend
+ frontend + lint + type + build + (new) provider test files; Docker
unchanged (no new infra).

## 4. DECISIONS REQUIRED BEFORE PHASE 2
1. BDT pricing: same USD minor-unit rows reinterpreted, or separate BDT
   `PlanPrice` rows per interval?
2. Commission/affiliate interplay: affiliate percent applies to which
   providers (Stripe-only today)?
3. Sandbox strategy + who holds provider test credentials.
4. Refund policy wording (credits consumed already) for `docs/` + support.
