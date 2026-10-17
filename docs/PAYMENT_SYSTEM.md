# ToolHub-AI Payment System

Architecture: `Plan/PlanPrice (DB-authoritative)` → `Provider (LS/bKash/Nagad/Stripe)`
→ `Payment` → verified webhook/callback → `Subscription` → `Entitlement`
→ `CreditTransaction (ledger)` → AI usage. Internal DB is source of truth;
providers are payment sources only.

## Endpoints (`/api/v1/billing/`)
- `GET providers/` — public capability/config (no secrets), drives frontend selector.
- `POST checkout/` — `{plan_id, price_id?, billing_interval?, coupon_code?, promotion_id?, provider}`.
  Server resolves plan + price + coupon; returns `{provider, checkout_url}` (Stripe/LS)
  or `{provider, payment_id, bkashURL|redirect_url, paymentID|reference}` (bKash/Nagad).
- `GET payments/{id}/` — owner-scoped safe status for success-page polling.
- `POST bkash/execute/` — `{payment_id, paymentID}`: server executes + verifies, then grants.
- `POST nagad/verify/` — `{payment_id, reference}`: server verifies, then grants.
- `GET bkash/callback/`, `POST|GET nagad/callback/` — provider landing (never grants directly).
- `POST webhooks/stripe/`, `POST webhooks/lemon-squeezy/` — signature-verified, idempotent.
- `GET reconciliation/` (admin) — stale pendings + suspected missing credit grants.
- Existing: `plans/`, `payments/`, `invoices/`, `coupons/validate/`, `plan-prices/`,
  `subscription/upgrade|downgrade/`, `refunds/`, `summary/`.

## Success pattern
Customer pays → provider confirms → backend verification/webhook →
`Payment=COMPLETED` → entitlement → credits → frontend polls `GET payments/{id}/`
(`Payment received — confirming...`, never optimistic "Pro Active").

## Credits (exactly once)
`activate_verified_payment()` locks the payment row, creates/extends the
subscription, marks COMPLETED, then `allocate_renewal_credits()` keyed by
`{provider}_payment_{payment.id}` (unique `CreditTransaction.reference`).
Duplicate webhooks/callbacks are no-ops. Renewal credits come only from
verified billing events (`subscription_payment_success` / invoice success),
never from subscription existence.

## Refund policy (auditable, reversible)
Refunds mark `Payment=REFUNDED` + `Refund` row; existing credit balances are
**preserved** (no blind subtraction of consumed credits); subscription stays
until period end unless provider reports expiry. Ops decides further
adjustment via admin + `CreditService.admin_adjust_credits()` (ledgered).

## Failed payments
`PAYMENT_FAILED` → subscription `PAST_DUE`; no data deletion; no silent
downgrade to Free. Grace-period rules unchanged.

## Currency
PlanPrice currency is authoritative. Lemon Squeezy/Stripe → USD rows;
bKash/Nagad → BDT rows (same `Plan`/`billing_interval`, `currency='BDT'`).
BD checkout with a non-BDT row logs a warning but still charges/verifies the
DB amount (no client-side conversion).

## Reconciliation
Admin `GET billing/reconciliation/` reports `stale_pending` (>2h) and
`missing_credits_suspected` for LS/bKash/Nagad succeeded payments without a
matching credit reference. Canonical fix: re-run verification (idempotent).
