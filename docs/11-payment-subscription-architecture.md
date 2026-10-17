# 11 --- Payment & Subscription Architecture

**Status:** Updated for Multi-Model AI Workspace  
**Priority:** Critical

------------------------------------------------------------------------

## 1. Purpose

The payment system controls access to ToolHub AI premium capabilities
while preserving useful free access.

It must support:

-   Free plan

-   Pro plan

-   Premium/Max plan

-   Subscription lifecycle

-   Credits

-   AI model entitlements

-   Premium image/AI tools

-   Usage limits

-   Payment provider integration

-   Webhook processing

-   Auditability

Payment status must never be determined only by frontend state.

------------------------------------------------------------------------

## 2. Product Access Model

    Plan

├── Features

├── Models

├── Tools

├── Limits

└── Credits

Example:

    FREE

├── Selected free AI models

├── Existing free tools

├── Limited AI usage

└── Basic workspace

PRO

├── More AI models

├── Premium tools

├── Higher credits

├── File / vision capabilities

└── Higher limits

PREMIUM / MAX

├── Advanced models

├── Highest limits

├── Advanced AI workflows

├── Priority processing

└── Premium creative capabilities

Exact entitlements must be configurable.

------------------------------------------------------------------------

## 3. Entitlement Architecture

Create a centralized:

    EntitlementService

It must answer:

-   Can this user access this model?

-   Can this user use this AI tool?

-   Can this user upload/process this file?

-   What is the user's current plan?

-   What limits apply?

The same service must be used by:

-   AI Gateway

-   Image processing

-   Premium editor tools

-   File processing

-   Future agents

------------------------------------------------------------------------

## 4. Credit Architecture

The system must have a real credit wallet and immutable ledger.

Conceptual entities:

    CreditWallet

CreditLedgerEntry

UsageRecord

Ledger operations should include:

-   Grant

-   Purchase

-   Subscription allocation

-   Reservation

-   Consumption

-   Refund

-   Expiration

-   Adjustment

Do not use a mutable balance without an auditable ledger.

------------------------------------------------------------------------

## 5. AI Model Credit Policy

Different models may have different credit costs.

Conceptually:

    Fast model        = low multiplier

Standard model = medium multiplier

Advanced model = high multiplier

Frontier model = premium multiplier

The multiplier must be configurable from backend/admin settings.

------------------------------------------------------------------------

## 6. Reservation and Settlement

For AI jobs:

    Request

↓

Check entitlement

↓

Estimate usage

↓

Reserve credits

↓

Execute provider request

↓

Record actual usage

↓

Settle reservation

If execution fails:

    Reservation → Release / Refund

This prevents users from being charged for failed operations.

------------------------------------------------------------------------

## 7. Subscription Lifecycle

Support:

    active

trialing

past_due

cancelled

expired

paused

Payment provider webhooks are the source of truth for payment events.

------------------------------------------------------------------------

## 8. Webhook Security

Payment webhooks must:

-   Verify signatures

-   Be idempotent

-   Validate event types

-   Prevent replay

-   Record processed event IDs

-   Update subscription state atomically

Never trust client-side payment success messages.

------------------------------------------------------------------------

## 9. AI Model Entitlement

Model access must be derived from plan configuration.

Example:

    Plan: Free

Allowed:

model-a

model-b

Plan: Pro

Allowed:

model-a

model-b

model-c

model-d

Plan: Premium

Allowed:

all eligible models

This should be data-driven.

------------------------------------------------------------------------

## 10. Usage Limits

Support limits such as:

-   Daily messages

-   Monthly credits

-   Model-specific limits

-   File size

-   File count

-   AI processing limits

-   Concurrent jobs

Limits must be enforced server-side.

------------------------------------------------------------------------

## 11. Upgrade Experience

Premium model selection should provide a contextual upgrade experience.

Do not block users with generic subscription pages unnecessarily.

Explain:

-   Why the model is premium

-   What capability it provides

-   Which plan unlocks it

-   What the user gets

------------------------------------------------------------------------

## 12. Existing Free Tools

Existing free tools remain available.

The product strategy is:

> Free tools drive discovery and traffic; premium AI and high-value
> workflows drive conversion.

Do not remove useful free tools merely to force subscriptions.

------------------------------------------------------------------------

## 13. Future Payment Provider

The architecture must keep payment-provider-specific logic isolated.

    PaymentService

↓

Provider Adapter

├── Stripe

└── Future Provider

The business layer must not depend directly on Stripe-specific objects.

------------------------------------------------------------------------

## 14. Required Audit Trail

Track:

-   Subscription events

-   Payment events

-   Credit changes

-   Entitlement changes

-   AI usage

-   Refunds

-   Administrative adjustments

All financial and credit mutations should be auditable.

------------------------------------------------------------------------

## 15. Security Rules

Never trust:

-   Client plan values

-   Client credit values

-   Client model access

-   Client payment success

-   Client usage counters

The backend is authoritative.

------------------------------------------------------------------------

## 16. Integration With AI Workspace

    AI Workspace

↓

AI Gateway

↓

EntitlementService

↓

CreditService

↓

Model Router

This is mandatory for all premium model requests.

------------------------------------------------------------------------

## 17. Definition of Done

Payment architecture is complete only when:

-   Real subscription state exists

-   Webhooks are verified

-   Entitlements are centralized

-   Credits have an auditable ledger

-   AI model access is server-enforced

-   Failed AI jobs do not incorrectly consume credits

-   Usage is recorded

-   Admin can configure plans and model access

-   Frontend cannot bypass premium restrictions
