**Product:** ToolHub AI

**Updated Version:** 2.0\
**Supersedes:** 1.0\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v2.0 Addendum --- Minimal AI Workspace Application Shell

Required shell:

``` text
┌──────────────────────────────────────────────────────────────┐
│ ToolHub AI                         Search  Theme  Profile    │
├──────────────────┬───────────────────────────────────────────┤
│ + New Chat       │              AI Workspace                 │
│ Models           │        Conversation / Composer            │
│ Projects         │                                           │
│ RECENT           │                                           │
│ Conversations    │                                           │
│ Settings         │                                           │
│ Help             │                                           │
└──────────────────┴───────────────────────────────────────────┘
```

### Navigation contract

-   No public marketing navigation inside the AI Workspace.
-   No duplicate horizontal workspace navigation.
-   Sidebar owns Models, Projects and Recent conversations.
-   Header owns Search, theme and account-level utilities.
-   Compare is contextual.
-   Usage is account/contextual.
-   Conversation and composer remain primary.
-   Future Agents, Research, Files and Vision appear contextually.

The AI Workspace, Creative Workspace and Export flow must feel like one
continuous application.

------------------------------------------------------------------------

**Status:** Architecture Specification

**Priority:** Critical

**Scope:** Multi-model AI Chat, Productivity, Research, Files, Vision,
and AI Agent capabilities

---

\## 1. Vision

ToolHub AI will provide a unified AI workspace where users can access
multiple AI models from different providers through one consistent
ToolHub AI interface.

The product is not intended to copy ChatGPT, Gemini, Claude, Aymo, or
any other brand. Those products may be studied for usability patterns,
but the final UX, visual language, navigation, interaction model, and
product identity must remain uniquely ToolHub AI.

The goal is:

\> **One professional workspace for chatting, reasoning, coding,
research, file analysis, image understanding, and everyday AI work.**

---

\## 2. Product Position

ToolHub AI will contain three major product pillars:

\`\`\`text

ToolHub AI

│

├── AI Workspace

│ ├── Multi-Model Chat

│ ├── Model Compare

│ ├── Auto Model

│ ├── Web Research

│ ├── File / PDF Analysis

│ ├── Vision

│ ├── Coding

│ └── Daily Productivity

│

├── Creative Workspace

│ ├── Image Editor

│ ├── AI Image Tools

│ ├── Templates

│ └── Creative Workflows

│

└── Free & Utility Tools

├── Image Utilities

├── Developer Tools

├── Productivity Tools

└── Future Free Traffic Tools

The AI Workspace should eventually become one of the primary reasons
users return to ToolHub AI every day.

------------------------------------------------------------------------

## 3. Multi-Model Principle

Users should not need separate interfaces for every provider.

The ToolHub AI interface remains constant while the model changes.

ToolHub AI UI

↓

AI Gateway

↓

Model Router

↓

Provider Adapter

┌────┼────┬────┬────┐

OpenAI Google Anthropic

DeepSeek xAI Qwen ...

The frontend must never depend directly on provider-specific API
implementations.

------------------------------------------------------------------------

## 4. Model Registry

Create a centralized model registry.

Each model should contain metadata such as:

id

provider

display_name

tier

capabilities

context_limit

supports_streaming

supports_vision

supports_files

supports_web

supports_reasoning

availability

cost_class

credit_multiplier

Example conceptual record:

{

"id": "provider-model-id",

"provider": "provider",

"display_name": "Model Name",

"tier": "pro",

"capabilities": \[

"chat",

"reasoning",

"vision"

\],

"supports_streaming": true,

"available": true

}

Do not hard-code model availability throughout the frontend.

------------------------------------------------------------------------

## 5. Provider Adapter Architecture

Every provider should be isolated behind an adapter.

AIProviderInterface

│

├── OpenAIAdapter

├── AnthropicAdapter

├── GoogleAdapter

├── DeepSeekAdapter

├── XAIAdapter

├── QwenAdapter

└── FutureProviderAdapter

A provider adapter is responsible for translating the internal ToolHub
AI request into the provider-specific API format.

The rest of the application must use a normalized internal interface.

------------------------------------------------------------------------

## 6. AI Gateway

All AI requests must pass through a centralized AI Gateway.

    Frontend

↓

Authentication

↓

Entitlement Check

↓

Credit / Usage Check

↓

AI Gateway

↓

Model Router

↓

Provider Adapter

↓

Provider

The AI Gateway is responsible for:

-   Authentication context

-   Authorization

-   Entitlement checks

-   Model availability

-   Credit reservation

-   Request normalization

-   Provider routing

-   Streaming

-   Error normalization

-   Usage recording

-   Credit settlement

-   Observability

------------------------------------------------------------------------

## 7. Free / Pro / Premium Model Access

ToolHub AI should have meaningful free access while reserving advanced
capabilities for paid plans.

### Free

Possible access:

-   Fast/lightweight models

-   Basic chat

-   Limited daily usage

-   Basic file capabilities

-   Selected vision capabilities

### Pro

Possible access:

-   Stronger reasoning models

-   Better coding models

-   Larger context

-   More file processing

-   Vision

-   Web search

-   Higher daily/monthly limits

### Premium / Max

Possible access:

-   Frontier/high-cost models

-   Advanced reasoning

-   Long-context workflows

-   Advanced research

-   Higher limits

-   Priority processing

-   Advanced agent features

Exact model assignments must be configurable from the backend rather
than hard-coded.

------------------------------------------------------------------------

## 8. Entitlement Enforcement

Premium model access must be enforced server-side.

Never rely on:

    Frontend hides premium model

as a security mechanism.

Required:

    User Request

↓

Authentication

↓

EntitlementService

↓

Can user access model?

↓

CreditService

↓

Can user afford request?

↓

Execute

------------------------------------------------------------------------

## 9. Auto Model

Provide an **Auto** model option.

The user can choose:

> Auto --- ToolHub AI selects an appropriate model for the task.

The router may consider:

-   Task type

-   Required capability

-   User plan

-   Model availability

-   Current provider health

-   Context size

-   Cost

-   User preferences

The routing policy must remain configurable.

------------------------------------------------------------------------

## 10. Model Selector

The model selector should show useful information rather than only model
names.

Recommended:

    Model

────────────────────────

✦ Auto

GPT

Fast reasoning

Vision

Claude

Writing & reasoning

Gemini

Long context

Vision

DeepSeek

Coding & reasoning

Premium models should clearly communicate:

-   Pro / Premium badge

-   Main strengths

-   Required plan

-   Optional estimated credit cost

------------------------------------------------------------------------

## 11. Model Comparison

A major differentiating feature is multi-model comparison.

Example:

    Prompt
      ↓
    ┌────────────┬────────────┬────────────┐
    │ Model A    │ Model B    │ Model C    │
    │            │            │            │
    │ Response   │ Response   │ Response   │
    │            │            │            │
    │ Copy       │ Copy       │ Copy       │
    └────────────┴────────────┴────────────┘

Users should be able to:

-   Compare responses

-   Copy one response

-   Continue with one model

-   Retry one model

-   Regenerate

-   Save preferred result

Comparison may consume credits for each model request.

------------------------------------------------------------------------

## 12. Conversation Architecture

Conversations should be persistent for authenticated users.

Conceptual hierarchy:

    Workspace

└── Project

└── Conversation

├── Messages

├── Attachments

├── Model selections

└── Usage records

A conversation should preserve enough metadata to continue the workflow.

------------------------------------------------------------------------

## 13. Model Switching Within a Conversation

Users should be able to switch models without losing conversation
context.

Example:

    GPT

↓

User switches to Gemini

↓

Context continues

↓

User switches to Claude

↓

Context continues

Provider-specific internal data must be normalized before passing
conversation context to another provider.

------------------------------------------------------------------------

## 14. Streaming

Where supported, responses should stream progressively.

UX:

    Generating...

▌

Avoid waiting for the entire response before rendering it.

Support:

-   Stop generation

-   Retry

-   Regenerate

-   Continue response where supported

-   Error recovery

------------------------------------------------------------------------

## 15. File and PDF Workspace

The AI Workspace should support:

-   Upload

-   PDF analysis

-   Text documents

-   Images

-   Structured extraction

-   Summarization

-   Question answering

-   File-based conversations

Conceptual flow:

    Upload

↓

Validate

↓

Store

↓

Extract / Index

↓

Create context

↓

AI request

Large files should use asynchronous processing where necessary.

------------------------------------------------------------------------

## 16. Vision

Vision-capable models may process:

-   Photos

-   Screenshots

-   UI screenshots

-   Documents

-   Charts

-   Diagrams

The UI should clearly indicate when the selected model supports vision.

------------------------------------------------------------------------

## 17. Web Research

Where supported, AI Workspace may provide:

-   Web search

-   Source collection

-   Source-aware answers

-   Research summaries

-   Multi-step research

Research should be represented as a distinct capability rather than
pretending every model has native web access.

------------------------------------------------------------------------

## 18. Daily Productivity

The workspace should eventually support reusable workflows such as:

-   Email drafting

-   Document rewriting

-   Translation

-   Summarization

-   Brainstorming

-   Meeting notes

-   Coding

-   Debugging

-   Data extraction

-   Content planning

-   Research

-   File Q&A

These should use the same AI Gateway.

------------------------------------------------------------------------

## 19. AI Agents --- Future Architecture

The architecture should leave room for agents.

Future:

    User Goal

↓

Agent

├── Model

├── Tools

├── Files

├── Web

├── Memory

└── Tasks

Agents must be added incrementally after the core multi-model
architecture is stable.

------------------------------------------------------------------------

## 20. Credit Consumption

AI requests should integrate with the centralized credit ledger.

Conceptual flow:

    Request

↓

Estimate / Reserve

↓

Provider execution

↓

Actual usage

↓

Settle

↓

Ledger entry

Never deduct credits only on the frontend.

The ledger must remain auditable.

------------------------------------------------------------------------

## 21. Provider Failure and Fallback

The architecture should support controlled fallback.

Example:

    Preferred Model

↓

Unavailable

↓

Fallback Policy

↓

Compatible Model

Fallback must respect:

-   User entitlement

-   Capability requirements

-   Credit cost

-   User-selected model preferences

Never silently switch to a materially different paid model without an
appropriate UX decision.

------------------------------------------------------------------------

## 22. Rate Limiting

Apply rate limiting at multiple levels:

-   User

-   IP where appropriate

-   Endpoint

-   Model

-   Plan

-   Provider

Heavy requests must receive stronger protection.

------------------------------------------------------------------------

## 23. Security

Required:

-   Provider API keys remain server-side

-   Never expose provider secrets to browser

-   Server-side entitlement checks

-   Server-side credit checks

-   Request validation

-   File validation

-   Abuse protection

-   Rate limiting

-   Audit logs

-   Safe error messages

------------------------------------------------------------------------

## 24. Cost Control

Because different models have different costs, the system must track:

-   Provider

-   Model

-   Input usage

-   Output usage

-   Estimated cost

-   Actual cost where available

-   Credits consumed

-   User plan

The business should be able to change model access or credit multipliers
without rewriting the frontend.

------------------------------------------------------------------------

## 25. Observability

Track:

-   Request success rate

-   Error rate

-   Latency

-   Model usage

-   Provider usage

-   Credit usage

-   Token usage where available

-   Abandoned requests

-   Retry rate

Do not store sensitive user content unnecessarily.

------------------------------------------------------------------------

## 26. UI Architecture

The AI Workspace should feel like professional software.

Recommended:

    ┌──────────────────────────────────────────────────────────────┐
    │ ToolHub AI      Search     Projects     Usage     Account    │
    ├──────────────┬───────────────────────────────────────────────┤
    │ New Chat     │                                               │
    │              │              Conversation                     │
    │ Models       │                                               │
    │ Projects     │                                               │
    │ History      │                                               │
    │              │                                               │
    │              ├───────────────────────────────────────────────┤
    │              │ Attach | Web | Tools | Model | Send           │
    └──────────────┴───────────────────────────────────────────────┘

The exact layout must follow the ToolHub AI design system, not another
company's UI.

------------------------------------------------------------------------

## 27. Responsive Workspace

Desktop:

-   Sidebar

-   Conversation area

-   Context panel when needed

Mobile:

-   Compact header

-   Conversation-first canvas

-   Bottom tool/model controls

-   Sheet/drawer for secondary controls

The conversation must remain the primary focus.

------------------------------------------------------------------------

## 28. Premium UX

Premium access should communicate value without becoming intrusive.

Show:

-   Model capability

-   Plan requirement

-   Usage/credits

-   Upgrade CTA

-   Remaining quota

Do not repeatedly interrupt an active workflow with upgrade dialogs.

------------------------------------------------------------------------

## 29. Integration With Existing ToolHub AI

This architecture must integrate with:

-   `11-payment-subscription-architecture.md`

-   `12-ai-processing-architecture.md`

-   `26-application-workspace-architecture.md`

-   Editor architecture

-   Storage architecture

-   Admin architecture

-   Analytics architecture

The AI Workspace is a first-class application workspace, not a
standalone page.

------------------------------------------------------------------------

## 30. Implementation Phases

### Phase A --- Foundation

-   AI Gateway

-   Provider interface

-   Model registry

-   Basic model selector

-   Streaming

-   Chat persistence

### Phase B --- Entitlements

-   Free/Pro/Premium access

-   Credit checks

-   Usage ledger

-   Model availability controls

### Phase C --- Advanced Chat

-   Model switching

-   Compare mode

-   File attachments

-   Vision

### Phase D --- Productivity

-   Web search

-   Research

-   PDF analysis

-   Reusable workflows

### Phase E --- Intelligence

-   Auto routing

-   Provider fallback

-   Advanced context

-   Projects

### Phase F --- Agents

-   Tool calling

-   Agent execution

-   Multi-step workflows

-   User-approved actions

------------------------------------------------------------------------

## 31. Definition of Done

The AI Workspace is production-ready only when:

-   Multiple providers work through a normalized gateway

-   Free and premium access is server-enforced

-   Credits are enforced server-side

-   Conversations persist

-   Streaming works

-   Model switching works

-   Compare mode works

-   File workflows work where enabled

-   Errors are handled

-   Provider keys are protected

-   Usage is recorded

-   Mobile UX is usable

-   Dark/light mode is polished

-   UI follows ToolHub AI branding

-   No competitor branding is copied

**Core principle:**

> ToolHub AI should feel like one intelligent product, even though many
> different AI models and providers operate behind it.`<br>`{=html}"""

docs\["11-payment-subscription-architecture.md"\] = r"""# 11 --- Payment
& Subscription Architecture

**Status:** Updated for Multi-Model AI
Workspace`<br>`{=html}**Priority:** Critical

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

-   Frontend cannot bypass premium restrictions`<br>`{=html}"""

docs\["12-ai-processing-architecture.md"\] = r"""# 12 --- AI Processing
Architecture

**Status:** Updated for Multi-Model AI
Workspace`<br>`{=html}**Priority:** Critical

------------------------------------------------------------------------

## 1. Purpose

This document defines the architecture for AI processing across ToolHub
AI.

It now covers both:

1.  AI image/creative processing

2.  Multi-model conversational AI processing

Both systems must share security, entitlement, credit, queue, storage,
and observability principles.

------------------------------------------------------------------------

## 2. Two AI Processing Classes

    AI Processing

│

├── Interactive AI

│ ├── Chat

│ ├── Streaming

│ ├── Vision

│ └── Short requests

│

└── Async AI Jobs

├── Background removal

├── Upscaling

├── Enhancement

├── Object removal

├── Heavy file analysis

└── Long-running workflows

------------------------------------------------------------------------

## 3. Multi-Model Request Flow

    Frontend

↓

Auth

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

Streaming / Response

↓

Usage Record

↓

Credit Settlement

------------------------------------------------------------------------

## 4. Async Image AI Flow

    Frontend

↓

Authenticated API

↓

Entitlement

↓

Credit Reservation

↓

Create Job

↓

Celery / Worker

↓

AI Provider / Model

↓

Storage

↓

Job Result

↓

Frontend polling / realtime update

↓

Credit Settlement

------------------------------------------------------------------------

## 5. Provider Abstraction

All model providers must be behind a normalized interface.

    AIProviderInterface

├── chat()

├── stream()

├── vision()

├── image_process()

└── capabilities()

Not every provider must implement every capability.

The registry determines capability support.

------------------------------------------------------------------------

## 6. Model Router

The router chooses a model based on:

-   Explicit user selection

-   Auto mode

-   Capability requirements

-   Plan entitlement

-   Cost

-   Availability

-   Context requirements

-   Provider health

The router must never select a model the user is not entitled to use.

------------------------------------------------------------------------

## 7. Streaming

Chat requests should stream when provider support exists.

The system should normalize provider-specific streaming formats into a
ToolHub AI stream.

The frontend should support:

-   Token/content streaming

-   Stop generation

-   Connection recovery

-   Error state

-   Retry

------------------------------------------------------------------------

## 8. Async Job Model

Long-running AI operations require a job abstraction.

Conceptual states:

    queued

processing

completed

failed

cancelled

expired

Each job should have:

-   ID

-   User

-   Tool/model

-   Status

-   Input reference

-   Output reference

-   Usage

-   Credit reservation

-   Error information

-   Timestamps

------------------------------------------------------------------------

## 9. Celery and Redis

Celery/Redis may be used for:

-   Image AI processing

-   Large file processing

-   Background research

-   Scheduled model operations

-   Heavy document extraction

Do not use Celery for ordinary low-latency streaming chat unless the
workflow actually requires background execution.

------------------------------------------------------------------------

## 10. File Processing

File AI workflows:

    Upload

↓

Validation

↓

Object Storage

↓

Extraction

↓

Optional indexing

↓

Context preparation

↓

Model request

↓

Result

Large files should be processed asynchronously.

------------------------------------------------------------------------

## 11. AI Context

Conversation context should be normalized internally.

Possible context sources:

-   Conversation history

-   User-provided files

-   Project knowledge

-   Image inputs

-   Tool outputs

-   Web research results

Only context required for the request should be sent to the provider.

------------------------------------------------------------------------

## 12. Model Context Management

The system must account for provider context limits.

Possible strategies:

-   Truncation

-   Summarization

-   Conversation compaction

-   Retrieval

-   File indexing

-   Context prioritization

Never blindly send unlimited conversation history.

------------------------------------------------------------------------

## 13. Credit Integration

Every billable AI request must integrate with CreditService.

For streaming chat:

    Authorize

↓

Reserve estimated amount

↓

Stream

↓

Measure actual usage

↓

Settle

For async jobs:

    Authorize

↓

Reserve

↓

Process

↓

Settle or refund

------------------------------------------------------------------------

## 14. Error Normalization

Provider-specific errors must be converted into safe internal error
categories.

Examples:

    RATE_LIMITED

PROVIDER_UNAVAILABLE

MODEL_UNAVAILABLE

INVALID_REQUEST

CONTENT_REJECTED

INSUFFICIENT_CREDITS

ENTITLEMENT_DENIED

PROCESSING_FAILED

Frontend should receive useful user-facing messages without leaking
provider secrets.

------------------------------------------------------------------------

## 15. Retry Policy

Retry only when appropriate.

Retryable:

-   Temporary provider failure

-   Network timeout

-   Temporary rate limit, subject to policy

Non-retryable:

-   Invalid request

-   Insufficient credits

-   Entitlement failure

-   Invalid file

-   Unsupported capability

Avoid duplicate charges during retries.

------------------------------------------------------------------------

## 16. Provider Failover

Failover is allowed only when:

-   User selected Auto

-   Policy permits fallback

-   Compatible capability exists

-   User is entitled

-   Credit rules are satisfied

Explicit model selection should normally remain explicit unless the user
has opted into fallback.

------------------------------------------------------------------------

## 17. Image AI Processing

Existing image AI tools remain supported:

-   Background removal

-   Upscaling

-   Enhancement

-   Object removal

-   Future AI editing tools

All must use the same:

    Auth → Entitlement → Credits → Job → Processing → Storage → Result

pattern.

------------------------------------------------------------------------

## 18. Observability

Record:

-   Model

-   Provider

-   Request duration

-   Queue duration

-   Input/output usage where available

-   Credit consumption

-   Error category

-   Retry count

-   Job state

Avoid retaining unnecessary sensitive content.

------------------------------------------------------------------------

## 19. Security

Required:

-   Provider keys server-side

-   Authenticated endpoints

-   Server-side entitlement

-   Server-side credit enforcement

-   File validation

-   Upload limits

-   Rate limiting

-   Abuse protection

-   Safe logging

-   Secure object storage

------------------------------------------------------------------------

## 20. AI Processing Boundaries

Do not put provider-specific logic into:

-   React components

-   Page components

-   Generic UI components

-   Business domain models

Keep provider integration inside backend AI infrastructure.

------------------------------------------------------------------------

## 21. Integration With Existing Architecture

This document must integrate with:

-   Payment/subscription

-   Credit ledger

-   Storage/file management

-   Editor

-   Analytics

-   Admin panel

-   Application workspace

-   AI multi-model workspace

------------------------------------------------------------------------

## 22. Definition of Done

AI processing is production-ready when:

-   Providers are abstracted

-   Model registry exists

-   AI Gateway exists

-   Entitlements are enforced

-   Credits are enforced

-   Streaming works

-   Async jobs work

-   Errors are normalized

-   Retries are safe

-   Provider secrets remain private

-   Usage is recorded

-   Image AI and conversational AI use consistent
    infrastructure`<br>`{=html}"""

docs\["26-application-workspace-architecture.md"\] = r"""# 26 ---
Application Workspace Architecture

**Status:** Updated for AI Multi-Model
Workspace`<br>`{=html}**Priority:** Critical

------------------------------------------------------------------------

## 1. Purpose

ToolHub AI is evolving from a collection of tools into a unified
application platform.

The application workspace architecture must support:

-   AI Workspace

-   Image Editor

-   Creative tools

-   Projects

-   Files

-   Conversations

-   History

-   Account

-   Usage

-   Subscription

-   Future AI agents

The interface should feel like professional software rather than a
traditional marketing website.

------------------------------------------------------------------------

## 2. Application Shell

The application shell is the shared environment after users enter a
workspace.

    ToolHub AI Application

│

├── Global Header

├── Primary Navigation

├── Workspace Navigation

├── Main Workspace

├── Context Panels

└── Notifications / Status

Marketing pages and application workspaces should remain visually
connected but functionally distinct.

------------------------------------------------------------------------

## 3. Main Product Workspaces

    Application

│

├── AI Workspace

│

├── Creative Workspace

│ └── Image Editor

│

├── Projects

│

├── Files

│

├── History

│

└── Account / Billing

------------------------------------------------------------------------

## 4. AI Workspace

The AI Workspace is a first-class application workspace.

Core areas:

-   New chat

-   Conversations

-   Model selector

-   Auto model

-   Compare

-   Attachments

-   Web/research controls

-   Tools

-   Projects

-   Usage

------------------------------------------------------------------------

## 5. AI Workspace Layout

Desktop concept:

    ┌───────────────────────────────────────────────────────────────┐
    │ ToolHub AI | Search | Projects | Usage | Account              │
    ├──────────────┬────────────────────────────────────────────────┤
    │              │                                                │
    │ New Chat     │                Conversation                     │
    │              │                                                │
    │ Models       │                                                │
    │ Projects     │                                                │
    │ History      │                                                │
    │              │                                                │
    │              ├────────────────────────────────────────────────┤
    │              │ Attach | Web | Tools | Model | Send            │
    └──────────────┴────────────────────────────────────────────────┘

Optional contextual panels may open without destroying the conversation.

------------------------------------------------------------------------

## 6. Creative Workspace

The existing Image Editor remains a professional full-screen workspace.

    Creative Workspace

└── Editor

├── Tool Rail

├── Canvas

├── Inspector

├── History

└── Export

The AI Workspace and Creative Workspace share:

-   Authentication

-   User

-   Projects

-   Files

-   Credits

-   Entitlements

-   Design tokens

-   Notifications

-   Application shell

------------------------------------------------------------------------

## 7. Shared Project Model

A project may contain:

    Project

├── Conversations

├── Images

├── Files

├── Editor documents

├── AI outputs

└── Metadata

This allows a future workflow such as:

    Project

↓

Upload product images

↓

AI analyzes images

↓

Remove background

↓

Generate marketing copy

↓

Create social assets

------------------------------------------------------------------------

## 8. Shared File System

Files should be accessible to permitted workspaces.

Example:

    Files

├── Images

├── Documents

├── PDFs

└── Generated Assets

Permissions and ownership must be enforced server-side.

------------------------------------------------------------------------

## 9. Navigation

The navigation should expose the product's breadth without becoming
overwhelming.

Recommended high-level categories:

    AI

Creative

Image

Documents

Productivity

Developer

Utilities

The Mega Menu can expose popular tools and categories.

The application sidebar should prioritize workspace actions rather than
marketing content.

------------------------------------------------------------------------

## 10. History

History should unify relevant user activity.

Possible entries:

-   AI conversations

-   Generated images

-   Edited images

-   AI processing jobs

-   Exported assets

Users should be able to return to previous work.

------------------------------------------------------------------------

## 11. Usage

Users should have a clear usage area:

    Credits

████████░░ 80%

Plan

Pro

Usage this period

AI messages

Image processing

File processing

Avoid making users guess why a premium operation is unavailable.

------------------------------------------------------------------------

## 12. Subscription Integration

Application workspaces must consume the same entitlement system.

    Application

↓

User

↓

Plan

↓

Entitlements

↓

Workspace capability

There should not be separate premium logic for every page.

------------------------------------------------------------------------

## 13. Responsive Application Shell

Desktop:

-   Persistent navigation where appropriate

-   Large workspace canvas

-   Contextual side panels

Mobile:

-   Compact header

-   Drawer navigation

-   Bottom sheets

-   Workspace-first content

-   Touch-friendly controls

Do not simply shrink the desktop UI.

------------------------------------------------------------------------

## 14. Global Command/Search

The application should eventually support a command/search interface.

Example:

    Search or Command

────────────────────────

Open AI Workspace

Open Image Editor

Search projects

Search conversations

Find tools

Upload file

This becomes increasingly valuable as the platform grows.

------------------------------------------------------------------------

## 15. Notifications and Background Jobs

Users should be able to see long-running job status without losing their
workspace.

Example:

    Background task

AI Upscaling

████████░░ 80%

On completion:

    ✓ Upscaling complete

\[ View Result \]

------------------------------------------------------------------------

## 16. Workspace Persistence

When users leave and return:

-   Current project should remain available

-   Conversations should persist

-   Editor projects should persist where supported

-   Generated assets should remain accessible

-   Usage state should be current

Never assume the browser session is the only source of state.

------------------------------------------------------------------------

## 17. Application Performance

The shell must remain lightweight.

Use:

-   Route-level code splitting

-   Lazy loading

-   Virtualized long lists where appropriate

-   Optimized images

-   Efficient state management

-   Server-side data fetching where appropriate

Heavy editors and AI modules should not unnecessarily load on every
page.

------------------------------------------------------------------------

## 18. Design System Integration

The entire application must follow:

-   ToolHub AI design tokens

-   shadcn/ui foundation

-   Consistent typography

-   Consistent spacing

-   Consistent surfaces

-   Consistent motion

-   Dark/light themes

Each workspace can have specialized controls while retaining the same
visual identity.

------------------------------------------------------------------------

## 19. Cross-Workspace Workflow

A core strategic advantage is moving between tools without leaving the
application.

Example:

    AI Workspace

↓

Generate product description

↓

Creative Workspace

↓

Edit product image

↓

AI Background Removal

↓

Generate social asset

↓

Export

Future workflows should feel connected rather than like separate
websites.

------------------------------------------------------------------------

## 20. Future Agent Workspace

The application shell must leave room for:

    Agent Workspace

├── Goal

├── Model

├── Tools

├── Files

├── Browser/Web

├── Tasks

└── Approval

Agents should operate inside the same permission and credit
architecture.

------------------------------------------------------------------------

## 21. Admin Integration

Administrators should eventually configure:

-   Models

-   Providers

-   Plans

-   Entitlements

-   Credit costs

-   Tool availability

-   Feature flags

-   Usage limits

-   AI provider health

This avoids code changes for routine product configuration.

------------------------------------------------------------------------

## 22. Analytics Integration

Track workspace-level events such as:

-   Workspace opened

-   Model selected

-   Tool used

-   AI request completed

-   AI request failed

-   Upgrade viewed

-   Subscription started

-   File uploaded

-   Export completed

Analytics must avoid collecting unnecessary sensitive content.

------------------------------------------------------------------------

## 23. Product Growth Principle

Free tools remain important for discovery and traffic.

Premium features should focus on:

-   High-value AI models

-   Advanced workflows

-   Expensive processing

-   Professional productivity

-   High-quality creative capabilities

The product should not become artificially restrictive just to force
upgrades.

------------------------------------------------------------------------

## 24. Definition of Done

The application workspace architecture is complete when:

-   AI Workspace is a first-class workspace

-   Creative Editor remains a first-class workspace

-   Shared authentication exists

-   Shared projects/files exist

-   Shared credits/entitlements exist

-   Shared navigation exists

-   History works

-   Usage works

-   Responsive shell works

-   Dark/light themes are consistent

-   Cross-workspace workflows are possible

-   Future agents can be added without redesigning the entire
    application

**Core principle:**

> ToolHub AI should feel like one coherent professional application
> containing multiple powerful workspaces---not a website with many
> unrelated tools.
