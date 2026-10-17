# Payment Security

- Server-side pricing only: plan/price/amount/currency resolved from DB;
  frontend never controls amounts, credits, or entitlements.
- Webhooks authoritative: Stripe `Stripe-Signature`, Lemon Squeezy
  `X-Signature = hex(HMAC-SHA256(raw, secret))`; bKash/Nagad via server
  execute/verify calls. Redirects/query params are never proof.
- Idempotency: `WebhookEvent(provider, event_id)` unique,
  `Payment.provider_payment_id` unique, `Refund.idempotency_key` unique,
  credit grants keyed by `{provider}_payment_{id}` / `sub_renewal_{invoice}`.
  Concurrent duplicates → one payment, one grant (`select_for_update`).
- Anti-tamper: amount/currency/user/provider-ref binding checked on every
  verify; payment-ID reuse, cross-user attachment, replays rejected
  (`PAYMENT_AMOUNT_MISMATCH`, `PAYMENT_CURRENCY_MISMATCH`,
  `PAYMENT_ALREADY_PROCESSED`, `WEBHOOK_SIGNATURE_INVALID`,
  `WEBHOOK_ALREADY_PROCESSED`).
- AuthZ: payments/invoices/subscriptions owner-scoped; reconciliation admin-only.
- Secrets: env-only, never in frontend, logs, or git. Audit logs carry
  user/payment/provider/event/status only.
- No silent fallback between providers; no mock provider in production
  (`sk_test_dummy` fail-open applies to Stripe only and reports unconfigured).
