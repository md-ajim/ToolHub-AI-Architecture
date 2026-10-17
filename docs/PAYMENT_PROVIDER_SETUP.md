# Payment Provider Setup (placeholders only — never commit secrets)

## Common
```env
PAYMENT_PROVIDER=lemon_squeezy
PAYMENT_ENABLED_PROVIDERS=stripe,lemon_squeezy,bkash,nagad
```

## Lemon Squeezy (international, API v1 — https://docs.lemonsqueezy.com/api)
1. Create store → note Store ID. Test mode is store-level.
2. Create products/variants per plan (Pro Monthly/Yearly, Business Monthly/Yearly).
3. API key (Settings → API) → `LEMON_SQUEEZY_API_KEY`.
4. Webhook → `https://<api>/api/v1/billing/webhooks/lemon-squeezy/`,
   secret → `LEMON_SQUEEZY_WEBHOOK_SECRET`. Subscribe to:
   `order_created`, `order_refunded`, `subscription_created/updated/cancelled/resumed/expired/paused`,
   `subscription_payment_success/failed/recovered`.
5. Per price: Django admin → PlanProviderMapping
   `(plan_price, provider=lemon_squeezy, variant id, currency, sandbox)` —
   or legacy `PlanPrice.provider_price_id = variant id`.
```env
LEMON_SQUEEZY_API_KEY=
LEMON_SQUEEZY_STORE_ID=
LEMON_SQUEEZY_WEBHOOK_SECRET=
LEMON_SQUEEZY_SANDBOX=True
```

## bKash (Bangladesh, tokenized v1.2.0-beta)
1. Merchant account → app key/secret, username/password.
2. Sandbox base `https://tokenized.sandbox.bka.sh/v1.2.0-beta`;
   production `https://tokenized.pay.bka.sh/v1.2.0-beta`.
3. Callback URL → `https://<app>/payments/callback?provider=bkash`
   (page calls `POST /api/v1/billing/bkash/execute/` server-side).
4. Create BDT `PlanPrice` rows per plan/interval; backend verifies
   amount/currency/status/merchant/user binding on execute.
```env
BKASH_APP_KEY=
BKASH_APP_SECRET=
BKASH_USERNAME=
BKASH_PASSWORD=
BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta
BKASH_SANDBOX=True
BKASH_CALLBACK_URL=
```

## Nagad (Bangladesh merchant API)
1. Merchant ID/number + RSA public/private keys from Nagad.
2. Base URL selects sandbox vs production.
3. Callback → `https://<api>/api/v1/billing/nagad/callback/`
   + frontend `/payments/callback?provider=nagad`.
4. Backend verifies reference server-side (`/payment/verify/{ref}`) before granting.
```env
NAGAD_MERCHANT_ID=
NAGAD_MERCHANT_NUMBER=
NAGAD_PUBLIC_KEY=
NAGAD_PRIVATE_KEY=
NAGAD_BASE_URL=
NAGAD_CALLBACK_URL=
NAGAD_SANDBOX=True
```

## Production activation
Set `*_SANDBOX=False`, point base URLs at production, install live
credentials via environment (never in git), create live PlanProviderMapping
rows, run a real small-amount end-to-end (checkout → webhook → credits),
then check `billing/reconciliation/` (admin).
