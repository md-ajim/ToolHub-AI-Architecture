# 11 — Payment & Subscription Architecture

**Project:** ToolHub AI  
**Document:** Payment & Subscription Architecture  
**Version:** 2.0  
**Status:** Critical — Master Payment Architecture  
**Previous Version:** 1.0  
**Supersedes:** 1.0 only after full-content preservation review  
**Priority:** CRITICAL

---

# 1. Purpose

This document defines the complete payment, subscription, billing,
entitlement, usage, credit, monetization, checkout, invoice, refund,
promotion and financial architecture of ToolHub AI.

The architecture must support:

- Free users
- Paid subscribers
- Multiple subscription plans
- Monthly billing
- Yearly billing
- One-time purchases where required
- One-day / temporary premium passes
- Usage-based limits
- AI credits
- Tool-specific limits
- Bulk processing limits
- High-resolution exports
- Cloud storage limits
- API usage
- Subscription upgrades
- Subscription downgrades
- Cancellation
- Renewal
- Failed payments
- Refunds
- Webhooks
- Invoices
- Billing history
- Coupons
- Promotional offers
- Affiliate/referral rewards where required
- Business/team plans
- Enterprise plans
- Future usage-based billing

The architecture must remain provider-agnostic and scalable.

---

# 2. Core Principle

Payment is NOT simply:

User → Pay → Premium

The correct architecture is:

User
↓
Plan / Pricing
↓
Checkout
↓
Payment Provider
↓
Verified Webhook
↓
Billing Service
↓
Subscription
↓
Entitlement
↓
Usage / Credits
↓
Tool / AI / Workspace Access

The frontend must never be the final authority for payment,
subscription, entitlement or credit access.

---

# 3. Existing Functionality Preservation

Payment implementation or redesign must NOT silently:

- remove existing tools
- remove existing plans
- remove existing billing functionality
- remove existing APIs
- remove subscription workflows
- remove credits
- remove usage tracking
- remove billing history
- remove invoices
- remove refunds
- remove cancellation
- remove renewal
- break existing premium access
- duplicate billing logic

Any removal requires:

Reason
↓
Impact Analysis
↓
Replacement / Migration
↓
Approval
↓
Implementation
↓
Testing
↓
Documentation Update

No silent deletion.

---

# 4. Monetization Philosophy

ToolHub AI follows:

FREE TRAFFIC
↓
FREE VALUE
↓
USER RETENTION
↓
PREMIUM VALUE
↓
SUBSCRIPTION
↓
RECURRING REVENUE

Free users must receive meaningful value.

Premium users should receive:

- higher limits
- faster processing
- better quality
- bulk processing
- advanced AI
- cloud history
- premium tools
- advanced export
- API access where applicable
- higher storage
- priority processing
- premium model access
- ad-free experience where applicable

Premium value must not depend only on removing ads.

---

# 5. Initial Plan Architecture

The architecture must support:

- FREE
- PRO
- BUSINESS
- ENTERPRISE

Future plans may include:

- STARTER
- TEAM
- AGENCY
- MAX

Plans must be configurable from centralized backend configuration.

Pricing and feature rules must never be scattered throughout frontend
or backend code.

---

# 6. Current Pricing UI Decision

The current Pricing UI contains:

## Free

$0 / month

## Pro

$9 / month

The UI also supports:

- Monthly
- Yearly
- Yearly savings indicator

The exact production price must come from centralized pricing
configuration and must not be hardcoded into UI components.

If yearly billing provides a discount, the displayed:

- monthly equivalent
- yearly total
- discount
- billing frequency

must all be mathematically consistent.

Example:

Monthly:
$9 / month

Yearly:
$X / year

The UI must clearly communicate whether the displayed amount is:

- monthly equivalent
- total annual charge
- recurring monthly charge

No misleading pricing.

---

# 7. Pricing as Data

Pricing must be represented as backend data.

Conceptual structure:

Plan
├── id
├── code
├── name
├── description
├── status
├── is_public
├── sort_order
└── features

PlanPrice
├── plan
├── billing_interval
├── amount
├── currency
├── provider_price_id
├── is_active
└── metadata

Supported billing intervals:

- monthly
- yearly
- promotional
- temporary
- one_time

---

# 8. Money Representation

Never use floating-point values for financial calculations.

Use:

- integer minor units
OR
- deterministic Decimal representation

Example:

$9.99

must be stored as:

999

with:

currency = USD

Every financial record must contain:

- amount
- currency

The system must never assume every future transaction is USD.

---

# 9. Payment Provider Abstraction

The application must not depend directly on a single payment provider
throughout the codebase.

Architecture:

PaymentService
│
├── Provider Adapter
├── Checkout
├── Subscription
├── Refund
├── Invoice
└── Webhook

The provider is a deployment/business decision.

Possible providers include:

- Stripe
- Paddle
- Other supported providers

The selected provider must be documented separately.

---

# 10. Internal Payment Interface

Business logic should communicate through normalized interfaces.

Conceptual interface:

create_customer()
create_checkout_session()
create_subscription()
update_subscription()
cancel_subscription()
refund_payment()
retrieve_invoice()
verify_webhook()
retrieve_payment()
retrieve_subscription()

Provider-specific SDK calls must remain inside provider adapters.

---

# 11. Checkout Architecture

Checkout flow:

User
↓
Select Plan
↓
Select Billing Interval
↓
Server Validates Plan
↓
Server Creates Checkout Session
↓
Payment Provider
↓
Payment
↓
Provider Confirmation
↓
Webhook
↓
Billing Service
↓
Subscription
↓
Entitlement Activation

The frontend success page must NOT activate premium access by itself.

---

# 12. Checkout Security

Before creating checkout:

Server must verify:

- authenticated user
- requested plan
- requested billing interval
- active price
- currency
- promotion eligibility
- coupon validity
- account status

The server must NOT trust:

- client price
- client plan name
- client entitlement
- client discount amount
- client credit amount

---

# 13. Payment Source of Truth

For asynchronous payment state:

WEBHOOK = SOURCE OF TRUTH

Frontend:

success page
↓
display result

Backend:

verified webhook
↓
update payment/subscription
↓
update entitlement

A user must never receive premium access simply because the browser
navigated to a success URL.

---

# 14. Webhook Architecture

Payment Provider
↓
Webhook Endpoint
↓
Signature Verification
↓
Event Validation
↓
Idempotency Check
↓
Queue
↓
Billing Worker
↓
Database
↓
Entitlement / Usage / Analytics

---

# 15. Webhook Security

Every webhook must:

- verify provider signature
- validate event structure
- validate event type
- validate provider account
- store event ID
- reject invalid requests
- prevent duplicate processing
- record processing status
- expose operational errors safely

Never trust an unverified webhook.

---

# 16. Webhook Idempotency

Webhook events may arrive multiple times.

Therefore:

event_id

must be unique.

If an event has already been processed:

return success
do not process again

Conceptual:

WebhookEvent
├── provider
├── event_id
├── event_type
├── payload_hash
├── status
├── processed_at
├── error_message
└── created_at

---

# 17. Billing Events

Internal normalized events may include:

- checkout_completed
- payment_succeeded
- payment_failed
- subscription_created
- subscription_updated
- subscription_canceled
- invoice_created
- invoice_paid
- invoice_failed
- refund_created

Provider-specific event names must be mapped to internal events.

---

# 18. Billing Service

Create a centralized:

BillingService

Responsibilities:

- checkout
- customer synchronization
- payment synchronization
- subscription creation
- subscription updates
- cancellation
- renewal
- refund
- invoice synchronization
- billing history synchronization

Billing logic must remain separate from individual tools.

---

# 19. Subscription Service

Create:

SubscriptionService

Responsibilities:

- active subscription
- subscription creation
- subscription update
- upgrade
- downgrade
- cancellation
- renewal
- expiration
- grace period
- subscription history

---

# 20. Subscription State

Internal application states:

- active
- trialing
- past_due
- grace_period
- canceled
- expired

Provider-specific statuses must be mapped into internal states.

---

# 21. Subscription Period

Every subscription must track:

current_period_start
current_period_end

These values control:

- usage reset
- credit reset
- renewal
- expiration
- analytics

---

# 22. Upgrade

Example:

FREE
↓
PRO

or:

PRO
↓
BUSINESS

Upgrade must correctly handle:

- new plan
- new price
- new entitlement
- new limits
- credits
- existing usage
- billing period
- provider subscription state

Proration behaviour must be explicitly defined for the selected
payment provider.

---

# 23. Downgrade

Example:

BUSINESS
↓
PRO

If current usage exceeds the new plan's limits:

- data must not be unexpectedly deleted
- user must receive clear warning
- migration path must be provided
- entitlement changes must occur according to policy

---

# 24. Cancellation

Support:

1. Cancel immediately
2. Cancel at period end

For cancellation-at-period-end:

- subscription remains active until period end
- premium access remains according to policy
- cancellation date is visible
- renewal is disabled
- data is retained according to policy

Cancellation must be easy to find.

---

# 25. Failed Payment

Flow:

Payment Failed
↓
Verified Webhook
↓
Subscription = PAST_DUE
↓
User Notification
↓
Provider Retry
↓
Success

If retries fail:

Grace Period
↓
Restriction
↓
Cancellation

Exact timing depends on provider and business policy.

---

# 26. Grace Period

During grace period:

- payment recovery continues
- user receives warnings
- premium access may continue according to policy
- data must not be immediately deleted

After grace period:

- premium access may be restricted
- subscription may become canceled/expired
- data retention policy continues

---

# 27. Refunds

Refunds must be processed through the payment provider.

Record:

refund_id
payment_id
amount
currency
reason
status
created_at

Refund must update:

- payment status
- subscription/billing state where applicable
- credit ledger where applicable
- analytics
- billing history

---

# 28. Invoice

Invoice model should support:

- user
- subscription
- provider_invoice_id
- amount
- currency
- status
- invoice_url
- invoice_pdf
- period_start
- period_end
- created_at

Users should be able to access available invoices from Billing.

---

# 29. Billing History

User Billing area should show:

Current Plan
Payment Method Reference
Billing Period
Usage
Credits
Invoices
Payments
Refunds
Subscription Changes
Upgrade
Downgrade
Cancellation

---

# 30. Payment Method

ToolHub AI must NOT store raw:

- card number
- CVV
- full payment credentials

Payment credentials remain with the payment provider.

ToolHub AI stores provider references where necessary.

---

# 31. Entitlement Architecture

Subscription status alone must NOT determine feature access.

Correct flow:

User
↓
Subscription
↓
Plan
↓
Entitlements
↓
Feature Access

Create:

EntitlementService

Responsibilities:

- determine active plan
- determine active subscription
- determine feature access
- determine limits
- determine remaining usage
- determine remaining credits
- determine premium permissions
- determine temporary entitlements

---

# 32. Feature Entitlements

Examples:

basic_image_resize
advanced_image_resize
background_removal
4k_export
bulk_processing
cloud_history
brand_kit
pdf_batch_processing
ai_enhancement
object_removal
api_access
priority_processing
ad_free
ai_workspace_pro_models
ai_workspace_max_models
ai_workspace_compare
ai_workspace_file_context

Each feature must have centralized entitlement rules.

---

# 33. Usage Service

Create:

UsageService

Responsibilities:

- record usage
- check limits
- consume usage
- return usage
- return remaining usage
- reset usage
- generate usage statistics

Examples:

image_processing
ai_generation
background_removal
pdf_processing
storage
api_requests
bulk_jobs

Individual tools must not create isolated billing counters.

---

# 34. Atomic Usage Consumption

Never use:

check()
process()
increment()

because concurrent requests can bypass limits.

Use:

atomic check + reserve
↓
process
↓
finalize

Expensive operations must support reservation/settlement.

---

# 35. Credit Architecture

Centralized credit types may include:

- AI Credits
- Image Processing Credits
- PDF Processing Credits
- API Credits
- Storage Credits

Architecture:

User
└── Credit Wallet
    ├── AI Credits
    ├── API Credits
    └── Processing Credits

---

# 36. Credit Ledger

Do NOT only store:

balance = 500

Maintain an append-only transaction ledger.

Example:

+1000 subscription credits
-10 AI enhancement
-20 background removal
+500 promotional credits
-50 API usage
+100 refund

Conceptual fields:

id
user
credit_type
amount
transaction_type
reference_type
reference_id
balance_after
created_at

Transaction types:

subscription_grant
usage
refund
promotion
admin_adjustment
expiration

---

# 37. Credit Reservation and Settlement

For AI operations:

Request
↓
Estimate
↓
Reserve
↓
Provider Execution
↓
Actual Usage
↓
Settlement
↓
Ledger Entry

Failed jobs must NOT incorrectly consume credits.

The existing AI architecture explicitly requires centralized entitlement,
credit reservation and credit settlement for both conversational and
async AI processing. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

---

# 38. Credit Expiration

Credit expiration must be explicitly defined.

Possible rule:

Monthly Credits
↓
Billing Period
↓
Expire at period end

Promotional credits may have separate expiration rules.

The UI and billing FAQ must communicate the actual rule.

---

# 39. AI Model Entitlement

AI model access must be controlled by the server.

The frontend model selector must never be trusted.

Model access:

User
↓
EntitlementService
↓
Model Registry
↓
Allowed Model
↓
AI Gateway

The model router must consider:

- user selection
- auto mode
- capability
- plan entitlement
- cost
- availability
- context requirements
- provider health

It must never select a model the user is not entitled to use. :contentReference[oaicite:4]{index=4}

---

# 40. AI + Billing Integration

AI request:

Frontend
↓
Authentication
↓
AI Gateway
↓
Entitlement
↓
Credit Reservation
↓
Model Router
↓
Provider Adapter
↓
Provider
↓
Response
↓
Usage Record
↓
Credit Settlement

This must remain compatible with:

12-ai-processing-architecture.md
32-ai-multi-model-workspace-architecture.md

---

# 41. Tool-Level Monetization

Every monetized tool should define:

- free capability
- premium capability
- usage limit
- processing cost
- required entitlement
- required credits
- maximum input
- maximum output
- batch limits

Example:

Image Resizer

Free:
- limited daily processing
- standard output
- limited file size

Pro:
- higher limits
- high-quality output
- bulk processing

Exact numbers must come from centralized plan configuration.

---

# 42. Pricing Page

Pricing page must clearly communicate:

- plans
- prices
- monthly/yearly billing
- savings
- features
- limits
- Free plan
- premium benefits
- cancellation
- billing FAQ
- supported payment methods
- what happens after failed payment
- credit rules

Important billing terms must not be hidden.

---

# 43. Pricing Comparison

Use a centralized feature matrix.

Example:

Feature                    Free     Pro      Business
------------------------------------------------------
Basic Tools                 ✓        ✓          ✓
AI Features              Limited    ✓          ✓
Bulk Processing             ✗        ✓          ✓
High Resolution             ✗        ✓          ✓
Cloud History            Limited    ✓          ✓
AI Models                Limited    ✓          ✓
Compare Mode                ✗        ✓          ✓
API Access                  ✗        ✓          ✓
Team Features               ✗        ✗          ✓
Priority Processing         ✗        ✓          ✓

Actual feature availability must match backend entitlements.

---

# 44. Pricing UI Rules

The current ToolHub AI visual identity must remain.

Pricing page must be:

- clean
- modern
- professional
- minimal
- easy to compare
- responsive
- accessible

Competitor platforms may be used as capability benchmarks,
but their exact visual layout must not be copied.

The project's master verification documentation explicitly requires
ToolHub AI branding, typography, tokens, components and visual identity
to remain owned by ToolHub AI. :contentReference[oaicite:5]{index=5}

---

# 45. Pricing Card Rules

Each plan should contain:

- plan name
- target audience
- price
- billing interval
- savings where applicable
- key features
- major limits
- CTA
- plan status

Recommended hierarchy:

FREE
$0
Start Free

PRO
$9/month
MOST POPULAR
Start Pro

BUSINESS
Business pricing
Contact / Start Business

ENTERPRISE
Custom
Contact Sales

Business and Enterprise must not be shown as purchasable if their
backend checkout does not actually exist.

---

# 46. Monthly / Yearly Toggle

The toggle must update:

- displayed price
- billing total
- savings
- provider price ID
- checkout session

Frontend must never calculate a different amount from backend pricing.

Backend remains the source of truth.

---

# 47. Billing FAQ

Pricing page should answer:

- Is there a free plan?
- Is a card required?
- Can I cancel anytime?
- What happens after cancellation?
- What happens if payment fails?
- Are refunds available?
- Are credits refundable?
- Do credits expire?
- Is yearly billing available?
- What payment methods are supported?
- What happens after downgrade?
- What happens when usage reaches the limit?

Only publish answers that match actual policy.

---

# 48. Billing Dashboard

User account should include:

Billing
├── Current Plan
├── Usage
├── Credits
├── Billing Period
├── Payment History
├── Invoices
├── Upgrade
├── Downgrade
├── Cancel
└── Payment Provider Management

---

# 49. Usage Dashboard

Show:

AI Credits
Image Processing
PDF Processing
Storage
API Requests

Example:

AI Credits

650 / 1000 used

350 remaining

Usage data must come from the backend.

---

# 50. Usage Warnings

Provide warnings at:

80%
90%
100%

Example:

"You have used 90% of your monthly AI credits."

Possible actions:

- Upgrade
- Buy Credits
- Wait for Reset

Only show actions actually supported by the account.

---

# 51. One-Day Pass

Architecture may support:

24-Hour Premium Pass

It must be represented as:

TemporaryEntitlement

not as a fake recurring subscription.

The exact price is a business decision and must come from pricing configuration.

---

# 52. One-Time Purchases

Architecture must support future:

- credit packs
- template packs
- processing packs
- premium exports
- one-day passes
- other digital products

One-time purchases must create appropriate financial and credit ledger records.

---

# 53. Credit Packs

Future products may include:

100 AI Credits
500 AI Credits
1000 AI Credits
5000 AI Credits

Purchased credits must create immutable ledger transactions.

---

# 54. Coupons

Support:

- percentage discount
- fixed discount
- first-payment discount
- recurring discount
- limited-time offer

Coupon validation must happen server-side.

---

# 55. Promotional Pricing

Promotional pricing must NOT modify core plan logic.

Promotion should contain:

- start date
- end date
- eligibility
- redemption limit
- duration
- discount
- applicable plan
- billing interval

---

# 56. Free Trial

Optional support:

- 3-day
- 7-day
- 14-day

Trial rules must be documented before implementation.

Abuse prevention must be proportionate and privacy-conscious.

---

# 57. Billing Notifications

Important notifications:

- subscription started
- payment successful
- payment failed
- renewal reminder
- subscription canceled
- refund issued
- trial ending
- usage limit warning

Billing email flow:

Queue
↓
Email Service
↓
Retry

Checkout completion must never depend on email delivery.

---

# 58. Account Deletion

Before deleting an account:

Check billing status.

If active:

Cancel subscription
↓
Provider confirmation
↓
Account deletion policy
↓
Data deletion/retention

Never leave an active paid subscription unintentionally running.

---

# 59. Data Retention

Cancellation must NOT automatically delete user data.

Flow:

Subscription canceled
↓
Premium access ends
↓
Data retained according to policy
↓
User may export/delete according to policy

Retention periods must be explicitly documented.

---

# 60. Fraud Protection

Monitor:

- repeated trials
- repeated refunds
- payment failures
- credit abuse
- API abuse
- automated account creation

Use layered detection.

Never permanently ban users solely from weak signals.

---

# 61. Tax Architecture

Future architecture must support:

- VAT
- GST
- sales tax
- regional taxes

Tax calculation must remain separate from unrelated business logic.

---

# 62. Subscription Analytics

Track:

- MRR
- ARR
- new subscriptions
- cancellations
- churn
- upgrade rate
- downgrade rate
- trial conversion
- Free → Paid conversion
- ARPU
- LTV
- refund rate
- failed payment rate

---

# 63. Revenue Analytics

Track revenue where legally and technically appropriate by:

- plan
- country
- currency
- acquisition source
- tool
- campaign
- time

---

# 64. Tool-to-Payment Attribution

Track:

User discovers tool
↓
Uses free feature
↓
Hits premium limit
↓
Views pricing
↓
Starts checkout
↓
Payment succeeds
↓
Subscription activated
↓
Premium feature used

This allows the platform to identify high-converting tools.

---

# 65. Security Rules

Mandatory:

1. Verify payment server-side.
2. Trust verified webhooks, not frontend success pages.
3. Centralize entitlements.
4. Centralize usage metering.
5. Make webhook processing idempotent.
6. Never store raw card details.
7. Never trust client-provided plan data.
8. Protect provider secrets.
9. Protect webhook secrets.
10. Protect credit operations.
11. Protect refund operations.
12. Rate-limit billing endpoints.
13. Audit sensitive billing operations.
14. Prevent concurrent usage races.
15. Keep billing separate from tool logic.

These rules are consistent with the existing payment architecture golden
rules. :contentReference[oaicite:6]{index=6}

---

# 66. Database Domain Separation

Do NOT combine payment, subscription, entitlement and usage into one model.

Recommended domain models:

Plan
PlanPrice
PlanFeature
Subscription
BillingCustomer
Payment
Invoice
Refund
Coupon
Promotion
CreditWallet
CreditTransaction
UsageRecord
Entitlement
TemporaryEntitlement
WebhookEvent

Only create models actually required by implementation.

---

# 67. Payment Database Requirements

Every financial record must preserve:

- provider
- provider reference
- amount
- currency
- status
- timestamps
- related user
- related subscription where applicable

Financial records must be auditable.

---

# 68. Billing History Integrity

Billing history must be append/audit friendly.

Do not silently overwrite historical financial records.

Subscription changes should remain traceable:

FREE → PRO
PRO → BUSINESS
BUSINESS → PRO
PRO → CANCELED

---

# 69. Provider Failure Handling

If the payment provider is temporarily unavailable:

- checkout should fail safely
- no premium access should be granted incorrectly
- user should receive clear error state
- no duplicate subscription should be created
- retry should be possible where appropriate
- operational error should be observable

---

# 70. Duplicate Checkout Protection

The system must prevent:

- duplicate checkout creation where possible
- duplicate subscription creation
- duplicate webhook processing
- duplicate credit grants
- duplicate refunds

Use provider references and idempotency mechanisms.

---

# 71. Admin Billing Controls

Admin architecture must eventually support:

- plan management
- price management
- feature entitlement management
- promotional pricing
- coupon management
- subscription inspection
- payment inspection
- refund workflow where authorized
- credit adjustment with audit trail
- usage inspection

Admin permissions must be server-enforced.

If the authoritative Admin architecture document is unavailable,
implementation must not invent undocumented admin behaviour.

---

# 72. API Billing

API access is a premium/business capability where enabled.

API usage must use the same centralized usage architecture.

Track:

API request
Tool
User
API key
Timestamp
Cost
Response status

API keys must support:

- revocation
- expiration
- rate limits
- usage tracking

Secrets must not be unnecessarily stored in plaintext.

---

# 73. Billing API Security

Protected endpoints must enforce:

Authentication
↓
Authorization
↓
Ownership
↓
Entitlement
↓
Validation
↓
Operation

Frontend checks are never sufficient.

---

# 74. Critical E2E Payment Flow

Required:

Pricing
↓
Select Plan
↓
Checkout
↓
Payment
↓
Webhook
↓
Subscription
↓
Entitlement
↓
Premium Feature
↓
Usage
↓
Credit Ledger

The complete flow must be tested.

---

# 75. Critical Payment Test Matrix

## Free

- Free account created
- Free tools available
- Premium tools correctly restricted
- Usage limits enforced

## Checkout

- Monthly checkout works
- Yearly checkout works
- Correct provider price used
- Correct currency used
- Coupon rules work
- Invalid plan rejected

## Payment

- Successful payment
- Failed payment
- Duplicate payment event
- Provider retry
- Refund

## Subscription

- Created
- Updated
- Renewed
- Canceled
- Expired
- Past due
- Grace period

## Entitlement

- Pro access granted
- Free access remains correct
- Downgrade handled
- Cancellation handled
- Frontend cannot bypass access

## Credits

- Grant
- Reservation
- Consumption
- Settlement
- Refund
- Expiration
- Ledger audit

---

# 76. Billing Webhook Test Matrix

Test:

- valid webhook
- invalid signature
- duplicate event
- out-of-order event
- malformed event
- provider retry
- worker failure
- database failure
- already processed event

Expected:

No duplicate subscription
No duplicate credit grant
No unauthorized premium access
No incorrect financial record

---

# 77. Payment UI Acceptance

Pricing page must visually verify:

- clean plan hierarchy
- clear price
- clear billing interval
- clear savings
- clear CTA
- clear limits
- clear premium benefits
- feature comparison
- billing FAQ
- cancellation information
- responsive mobile layout
- accessible controls

---

# 78. Mobile Billing Acceptance

Test at minimum:

320×568
375×667
390×844
430×932
768×1024
1024×768
1280×800
1440×900

Also test:

- portrait
- landscape
- keyboard
- touch
- 200% zoom
- loading
- error
- empty states

---

# 79. Accessibility

Verify:

- keyboard navigation
- visible focus
- semantic headings
- accessible buttons
- accessible pricing toggle
- screen reader labels
- sufficient contrast
- accessible FAQ
- accessible dialogs
- reduced motion
- 200% zoom
- no keyboard traps

---

# 80. Billing UX Principles

Payment UX must be:

- transparent
- predictable
- non-deceptive
- easy to understand
- easy to cancel
- clear about renewal
- clear about charges
- clear about limits

No dark patterns.

---

# 81. Pricing Page vs Backend Consistency

Every visible pricing claim must have a backend equivalent.

Example:

UI:

50 MB upload

Backend:

max_file_size = 50 MB

UI:

300 API credits

Backend:

api_credit_limit = 300

UI:

Unlimited

Backend:

must actually support the documented policy.

If UI and backend disagree:

RELEASE = FAIL

---

# 82. Documentation Consistency

Payment documentation must remain synchronized with:

- 00-README_FOR_AI.md
- 00.1-AI_PROJECT_CONTEXT.md
- AI_DEVELOPER_GUIDE.md
- 04-database-design.md
- 05-domain-model.md
- 08-api-design.md
- 09-authentication-and-authorization.md
- 12-ai-processing-architecture.md
- 13-storage-file-management-architecture.md
- 15-Admin-Architecture.md
- 16-Analytics-Architecture.md
- 32-ai-multi-model-workspace-architecture.md

Before significant billing changes, these related documents must be
reviewed.

The existing payment specification explicitly requires billing changes
to be made with the relevant architecture documents in view. 
83. Definition of Done — Payment

Payment architecture is NOT complete until all applicable items pass:
Plan                         ✓
Pricing                      ✓
Monthly Billing              ✓
Yearly Billing               ✓
Checkout                     ✓
Payment                      ✓
Payment Provider Adapter     ✓
Webhook Verification        ✓
Webhook Idempotency          ✓
Subscription                 ✓
Entitlement                  ✓
Usage                        ✓
Credits                      ✓
Credit Ledger                ✓
Credit Reservation           ✓
Credit Settlement            ✓
Upgrade                      ✓
Downgrade                    ✓
Cancellation                 ✓
Renewal                      ✓
Failed Payment               ✓
Grace Period                 ✓
Refund                       ✓
Invoice                      ✓
Billing History              ✓
Payment Security             ✓
Pricing UI                   ✓
Billing Dashboard            ✓
Billing Notifications        ✓
Analytics                    ✓
Testing                      ✓
E2E Testing                  ✓
Documentation                ✓
Regression                   ✓
The existing architecture already defines the same core completion gate:
real subscription state, verified webhooks, centralized entitlements,
auditable credits, server-enforced model access, usage recording,
admin configuration and frontend bypass protection.
84. Automatic Release Blockers

Release MUST be blocked if any of these occur:
FAIL:
Existing billing functionality removed

FAIL:
Existing payment flow broken

FAIL:
Client-only entitlement enforcement

FAIL:
Client-only credit enforcement

FAIL:
Unverified payment webhook accepted

FAIL:
Non-idempotent webhook processing

FAIL:
Provider secret exposed

FAIL:
Raw card details stored

FAIL:
Duplicate subscription created

FAIL:
Duplicate credit grant

FAIL:
Incorrect refund state

FAIL:
Incorrect invoice state

FAIL:
Pricing UI differs from backend

FAIL:
Premium access granted without verified payment

FAIL:
Paid access remains after required expiration

FAIL:
Critical billing migration not reviewed

FAIL:
Critical billing test failure

FAIL:
Documentation no longer matches implementation
The master verification document already identifies client-only entitlement,
credit bypass, invalid/non-idempotent payment webhooks, critical migration
issues and documentation mismatch as automatic release blockers.

85. Mandatory Payment Self-Review

Before declaring payment complete, the implementation agent MUST answer:

Which documentation was read?
Which payment architecture was used?
What existing payment functionality was preserved?
What changed?
What did not change?
Were any plans removed?
Were any APIs changed?
Were any database models changed?
Was provider integration changed?
Are webhooks verified?
Are webhooks idempotent?
Is entitlement server-enforced?
Is credit enforcement server-enforced?
Are card details protected?
Were upgrade/downgrade tested?
Was cancellation tested?
Was failed payment tested?
Was refund tested?
Was billing history tested?
Was mobile pricing tested?
Was accessibility tested?
Was E2E checkout tested?
What evidence proves payment works?
Are any requirements BLOCKED, PENDING or FAIL?

If a critical answer is unknown:

PAYMENT = NOT COMPLETE

86. Verification Status

Allowed statuses:

PASS
FAIL
BLOCKED
PENDING
N/A

Meaning:

PASS
= verified with actual implementation evidence

FAIL
= implementation does not satisfy requirement

BLOCKED
= required source/access/evidence unavailable

PENDING
= implementation exists but evidence is incomplete

N/A
= not applicable with documented reason

Documentation alone is never implementation evidence.

87. Final Payment Production Gate

ToolHub AI Payment is PRODUCTION READY only when:
Documentation
        +
Architecture
        +
Database
        +
API
        +
Authentication
        +
Authorization
        +
Checkout
        +
Payment
        +
Webhook
        +
Subscription
        +
Entitlement
        +
Usage
        +
Credits
        +
Refund
        +
Billing History
        +
Security
        +
Analytics
        +
Testing
        +
E2E
        +
Responsive
        +
Accessibility
        +
Visual QA
        +
Regression
        +
Documentation Sync
        =
PRODUCTION READY
No single UI screenshot is sufficient evidence.
88. Final Principle

ToolHub AI Payment must feel simple to the user while remaining
architecturally robust underneath.

USER EXPERIENCE:

Simple
Transparent
Professional
Predictable

BACKEND:

Provider-Agnostic
Server-Enforced
Auditable
Idempotent
Secure
Scalable

Core principle:

ONE PAYMENT SYSTEM
+
ONE BILLING DOMAIN
+
ONE ENTITLEMENT SYSTEM
+
ONE USAGE SYSTEM
+
ONE CREDIT LEDGER
+
MANY POWERFUL PRODUCTS

### গুরুত্বপূর্ণ

এই `v2.0`-এ আমি **আগের payment documentation-এর requirement বাদ দিইনি**; বরং checkout security, pricing/backend consistency, duplicate checkout protection, billing UI, webhook test matrix, payment E2E, release blockers এবং self-review আরও স্পষ্ট করেছি। মূল architecture-এ payment provider abstraction, configurable plans, centralized entitlement, credit ledger, subscription lifecycle, failed payment, refund, invoice এবং billing history ইতিমধ্যেই ছিল। :contentReference[oaicite:9]{index=9} :contentReference[oaicite:10]{index=10} :contentReference[oaicite:11]{index=11}

আর সবচেয়ে গুরুত্বপূর্ণ: **এখনই এটাকে “Payment সম্পূর্ণ হয়েছে” বলা যাবে না।** Master verification specification অনুযায়ী documentation থাকা implementation pass-এর প্রমাণ নয়; actual implementation evidence, tests এবং E2E verification লাগবে। :contentReference[oaicite:12]{index=12}

এটাই আমি আপনার জন্য **Payment Documentation-এর নতুন master version হিসেবে recommend করছি: `v2.0`**।
