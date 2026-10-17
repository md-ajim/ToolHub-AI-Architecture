# ToolHub AI --- Master AI Model Ecosystem & Production Implementation Specification

**Version:** 3.0\
**Status:** Critical / Master Implementation Document\
**Product:** ToolHub AI\
**Purpose:** Give a coding agent one authoritative specification for the
multi-model AI platform, including UI/UX, backend architecture, provider
integration, model registry, subscriptions, credits, cost protection,
security, and future scalability.

> **Core principle:** ToolHub AI is a unified AI product, not a
> collection of third-party API wrappers.
>
> **Brand principle:** Official proprietary models keep their official
> provider/model identity. Open-model capabilities can be productized
> under ToolHub AI experiences where legally permitted, while preserving
> required attribution and license compliance.
>
> **Design principle:** `shadcn/ui` + Lucide + existing ToolHub AI
> `/tools` + Mega Menu visual language + Vercel-quality product
> discipline. **Vercel-inspired ≠ Vercel copied.**

------------------------------------------------------------------------

# 1. NON-NEGOTIABLE PRODUCT RULES

1.  The existing ToolHub AI brand always wins.
2.  `/tools` and the Mega Menu are the primary visual source of truth.
3.  Dashboard must not have a separate theme.
4.  All authenticated pages must feel like one application.
5.  Use `shadcn/ui` as the primary UI component foundation.
6.  Use Lucide icons consistently.
7.  Do not introduce random colors, gradients, backgrounds, shadows, or
    component libraries.
8.  Official providers such as OpenAI, Google, Anthropic, DeepSeek, and
    Qwen retain their recognizable names.
9.  Open-model experiences may use ToolHub branding only where this does
    not violate ownership, license, attribution, or provider terms.
10. Never claim ToolHub trained a model unless ToolHub actually
    trained/operates it.
11. Frontend must never directly call paid model providers.
12. All AI requests must pass through the server-side AI Gateway.
13. Premium access must be enforced server-side.
14. Credits must be enforced server-side.
15. Provider spending must be protected server-side.
16. Provider API keys must never reach the browser.
17. A new provider/model must be addable without redesigning the
    frontend.
18. Do not fabricate model IDs, prices, capabilities, licensing, or free
    inference.
19. Do not launch hundreds of raw models merely to make the product look
    large.
20. Quality, reliability, usefulness, cost, and user experience are more
    important than model count.

------------------------------------------------------------------------

# 2. PRODUCT VISION

ToolHub AI provides one professional workspace for:

-   General Chat
-   Reasoning
-   Coding
-   Vision
-   Image Generation
-   Image Editing
-   Speech-to-Text
-   Text-to-Speech
-   Embeddings
-   Video
-   Files and PDF workflows
-   Research
-   Productivity workflows
-   Future AI agents

Users should not need a separate application interface for every
provider.

The interface remains ToolHub AI while the underlying model changes.

``` text
ToolHub AI UI
      ↓
AI Gateway
      ↓
Model Router
      ↓
Provider Adapter
      ↓
Provider / Model
```

------------------------------------------------------------------------

# 3. TEN APPROVED AI CAPABILITIES

These are capability categories, not individual models.

## 3.1 General Chat / LLM

Conversation, Q&A, writing, rewriting, translation, summarization,
brainstorming.

## 3.2 Reasoning

Mathematics, complex analysis, planning, multi-step reasoning,
structured problem solving.

## 3.3 Coding

Code generation, debugging, refactoring, code review, repository tasks,
coding-agent workloads.

## 3.4 Vision

Images, screenshots, PDFs, documents, charts, diagrams, OCR, visual
reasoning.

## 3.5 Image Generation

Text → image and approved creative generation workflows.

## 3.6 Image Editing

Image → modified image, object removal, background editing, generative
editing, restoration.

## 3.7 Speech-to-Text

Audio → text, transcription, meeting notes, voice input.

## 3.8 Text-to-Speech

Text → voice, narration, accessibility, audio generation.

## 3.9 Embeddings

Semantic search, RAG, document retrieval, similarity search.

## 3.10 Video

Text/image → video and video understanding where a real provider/model
capability exists.

Never advertise a capability that the selected provider/model does not
actually support.

------------------------------------------------------------------------

# 4. PROVIDER BRANDING STRATEGY

## 4.1 Official proprietary providers

Keep recognizable provider/model names:

``` text
OpenAI
  GPT ...

Google
  Gemini ...

Anthropic
  Claude ...

DeepSeek
  DeepSeek ...

Qwen
  Qwen ...

Meta
  Llama ...

xAI
  Grok ...

Mistral
  Mistral ...
```

The provider identity is useful to users and must not be falsely
renamed.

## 4.2 ToolHub product experiences

ToolHub can expose routing/product experiences such as:

``` text
ToolHub Auto
ToolHub Light
ToolHub Flash
ToolHub Pro
ToolHub Frontier
ToolHub Vision
ToolHub Creative
ToolHub Voice
ToolHub Code
```

These are **ToolHub product experiences/routing profiles**, not
proprietary foundation models unless ToolHub actually operates those
models.

## 4.3 Open-source model branding

Open-source models can be presented through ToolHub experiences where
licensing permits:

``` text
ToolHub Code
  Based on an approved open model

ToolHub Vision
  Based on an approved open model
```

Required attribution must be driven by the model's legal metadata.

Do not remove attribution merely because the UI is ToolHub branded.

------------------------------------------------------------------------

# 5. SOURCE-OF-TRUTH PRIORITY

When changing UI, follow this exact priority:

1.  Existing ToolHub AI design tokens
2.  Existing `/tools`
3.  Existing Mega Menu
4.  Existing shared components
5.  Existing application shell
6.  shadcn/ui conventions
7.  Vercel-quality product principles
8.  Generic inspiration

Never create a new dashboard theme.

------------------------------------------------------------------------

# 6. VERCEL-INSPIRED DEFINITION

Vercel-inspired means:

-   clean
-   minimal
-   restrained
-   premium
-   precise
-   excellent typography
-   strong hierarchy
-   subtle borders
-   intentional whitespace
-   high information density
-   professional interaction states

It does **not** mean copying:

-   Vercel logo
-   Vercel branding
-   exact navigation
-   exact layout
-   exact visual identity
-   exact components

Target:

``` text
ToolHub AI Brand
      +
shadcn/ui
      +
Vercel-quality product discipline
      +
ToolHub AI's own visual identity
      =
Premium ToolHub AI
```

------------------------------------------------------------------------

# 7. COLOR & BACKGROUND RULES

The Dashboard, AI Workspace, Projects, History, Saved Files, Usage,
Billing, Settings and other authenticated pages must use the same
ToolHub AI color/background system as `/tools` and the Mega Menu.

Forbidden unless already part of the established brand:

-   random colored page backgrounds
-   blue dashboard canvas
-   purple dashboard canvas
-   decorative gradients
-   unrelated tinted surfaces
-   excessive colored cards
-   arbitrary accent colors
-   different backgrounds between sections

Hierarchy should come from:

-   typography
-   spacing
-   borders
-   separators
-   existing surface tokens

Premium does not mean adding more effects.

------------------------------------------------------------------------

# 8. SHADCN/UI RULE

Use `shadcn/ui` as the primary component foundation.

Preferred primitives:

``` text
Button
Card
DropdownMenu
Avatar
Tooltip
Separator
Input
Dialog
Sheet
Command
ScrollArea
Popover
Tabs
Badge
Skeleton
Alert
Select
Form
```

Do not introduce unrelated component libraries.

Reuse existing ToolHub components before creating duplicates.

Do not build custom dropdown/modal behavior when shadcn/Radix already
provides it.

------------------------------------------------------------------------

# 9. ICON SYSTEM

Use **Lucide icons** consistently.

Recommended mappings:

``` text
Dashboard       LayoutDashboard
AI Workspace    Sparkles
Favorites       Star
Projects        Folder
History         History
Saved Files     File
Usage           Activity
Billing         CreditCard
Settings        Settings
Search          Search
Notifications   Bell
Profile         User
Create          Plus
Expand          ChevronDown
Navigate        ChevronRight
Close           X
Code            Code2
Vision          ScanEye
Image           Image
Audio           AudioLines
Video           Video
Files           FileText
```

Rules:

-   one icon family
-   consistent size
-   consistent stroke
-   consistent alignment
-   consistent optical spacing

Forbidden:

-   emoji as UI icons
-   mixed icon libraries
-   random inline SVG styles
-   inconsistent stroke widths
-   decorative icons without a purpose

------------------------------------------------------------------------

# 10. GLOBAL APPLICATION SHELL

All authenticated pages must use one coherent application shell.

Concept:

``` text
┌──────────────────────────────────────────────────────────────┐
│ ToolHub AI                         Search Theme Profile       │
├──────────────────┬───────────────────────────────────────────┤
│ Application      │ Application Header                         │
│ Sidebar          │                                           │
│                  │ Main Content                               │
│                  │                                           │
└──────────────────┴───────────────────────────────────────────┘
```

The shell must feel like one product.

------------------------------------------------------------------------

# 11. SIDEBAR INFORMATION ARCHITECTURE

Recommended:

``` text
ToolHub AI
AI-POWERED TOOLS

WORKSPACE
  Dashboard
  AI Workspace

LIBRARY
  Favorites
  Projects
  History
  Saved Files

INSIGHTS
  Usage
  Billing

ACCOUNT
  Settings
```

The sidebar must inherit the same:

-   typography
-   icon family
-   colors
-   spacing
-   border treatment
-   active states
-   hover states
-   radius

------------------------------------------------------------------------

# 12. PROFILE DROPDOWN --- CRITICAL UI FIX

The profile dropdown must be a true overlay anchored to the avatar.

Use:

-   shadcn/ui `DropdownMenu`
-   Radix positioning
-   portal behavior
-   predictable stacking
-   viewport collision handling

Required:

-   does not enter document flow
-   does not push Dashboard content
-   does not appear embedded inside Dashboard content
-   closes on outside click
-   closes on Escape
-   keyboard accessible
-   remains above application content
-   does not clip

Concept:

``` text
Header
                         [Avatar]
                            ↓
                     ┌───────────────┐
                     │ User          │
                     │ email         │
                     │ Profile       │
                     │ Settings      │
                     │ ───────────── │
                     │ Log out       │
                     └───────────────┘

Dashboard content remains underneath.
```

Do not solve this by blindly increasing `z-index`. Inspect stacking
contexts, overflow, positioned parents, transforms, and portals.

------------------------------------------------------------------------

# 13. PROJECT CREATION

Never use browser:

``` js
alert()
confirm()
prompt()
```

Use a branded shadcn Dialog.

``` text
Create project

Project name
[________________________]

Description (optional)
[________________________]

             Cancel   Create Project
```

Requirements:

-   accessible label
-   validation
-   loading
-   disabled invalid state
-   success/error feedback
-   keyboard support

------------------------------------------------------------------------

# 14. DASHBOARD PAGE HIERARCHY

Every Dashboard page should use:

``` text
Page title
Supporting description

Primary action / controls

Main content
```

Avoid:

-   oversized titles
-   excessive top spacing
-   oversized empty containers
-   competing controls
-   inconsistent page headers

Navigation and content must feel balanced:

``` text
Global navigation
      ↓
Application navigation
      ↓
Page header
      ↓
Page content
```

------------------------------------------------------------------------

# 15. EMPTY STATES

Empty states must be minimal and proportional.

Example:

``` text
       [Folder]

     No projects yet

Create a project to group related tools,
processed files, and workflows together.

       [ + Create Project ]
```

Use a consistent shadcn surface.

Do not create huge empty containers just to fill space.

------------------------------------------------------------------------

# 16. RESPONSIVE RULES

## Desktop

-   global header
-   persistent sidebar
-   main content

## Tablet

-   compact header
-   reduced sidebar
-   responsive spacing

## Mobile

-   compact header
-   sidebar via shadcn Sheet/Drawer
-   full-width content
-   touch-friendly controls
-   no horizontal overflow

AI Workspace mobile should remain conversation-first.

------------------------------------------------------------------------

# 17. ACCESSIBILITY

Required:

-   keyboard navigation
-   visible focus
-   accessible labels
-   semantic buttons
-   semantic navigation
-   sufficient contrast
-   dropdown keyboard behavior
-   Escape-to-close overlays
-   screen-reader-friendly icon buttons
-   tooltips for icon-only controls

Never communicate state through color alone.

------------------------------------------------------------------------

# 18. INTERACTION STATES

Every interactive element should support:

``` text
Default
Hover
Focus
Active
Disabled
Loading
Error
Success where applicable
```

Motion should be:

-   subtle
-   fast
-   purposeful
-   consistent

Avoid excessive animation.

------------------------------------------------------------------------

# 19. PROVIDER REGISTRY

Create one centralized Provider Registry.

Conceptual type:

``` ts
type Provider = {
  id: string
  name: string
  displayName: string
  type: "official" | "open" | "aggregator" | "self_hosted"
  enabled: boolean
  configured: boolean
  status: "healthy" | "degraded" | "unavailable" | "disabled"
  capabilities: Capability[]
  adapter: string
  commercialReviewStatus: "pending" | "approved" | "rejected"
  privacyReviewStatus: "pending" | "approved" | "rejected"
  attributionRequired: boolean
  metadata?: Record<string, unknown>
}
```

------------------------------------------------------------------------

# 20. MODEL REGISTRY

The Model Registry is the production source of truth.

Each model should contain:

``` text
id
provider
displayName
officialName
productName
capability
tier
status
availability
pricing
creditCost
supportedInputs
supportedOutputs
contextLimit
streamingSupport
toolCallingSupport
visionSupport
fileSupport
webSupport
reasoningSupport
planAccess
rateLimit
fallbackModels
enabled
license
attribution
metadata
```

Never hard-code model availability across frontend components.

------------------------------------------------------------------------

# 21. MODEL REGISTRY EXAMPLE

``` json
{
  "id": "provider-model-id",
  "provider": "provider",
  "displayName": "Model Name",
  "officialName": "Official Model Name",
  "productName": null,
  "capabilities": ["chat", "reasoning"],
  "tier": "pro",
  "status": "healthy",
  "enabled": true,
  "supportsStreaming": true,
  "supportsVision": false,
  "supportsFiles": false,
  "supportsToolCalling": true,
  "creditCost": 8,
  "planAccess": ["pro", "business", "enterprise"],
  "fallbackModels": []
}
```

------------------------------------------------------------------------

# 22. PROVIDER ADAPTER ARCHITECTURE

Every provider must be isolated behind an adapter.

``` text
AIProviderInterface
   ├── OpenAIAdapter
   ├── GoogleAdapter
   ├── AnthropicAdapter
   ├── DeepSeekAdapter
   ├── QwenAdapter
   ├── XAIAdapter
   ├── OpenModelAdapter
   └── FutureProviderAdapter
```

Provider-specific API requests stay inside adapters.

The rest of the application uses normalized internal structures.

------------------------------------------------------------------------

# 23. NORMALIZED AI REQUEST

``` ts
type NormalizedAIRequest = {
  requestId: string
  userId: string
  conversationId?: string
  modelId: string
  capability: Capability
  messages: Message[]
  attachments?: Attachment[]
  tools?: ToolDefinition[]
  temperature?: number
  maxOutputTokens?: number
  stream?: boolean
  metadata?: Record<string, unknown>
}
```

------------------------------------------------------------------------

# 24. NORMALIZED AI RESPONSE

``` ts
type NormalizedAIResponse = {
  requestId: string
  provider: string
  modelId: string
  content: MessageContent[]
  usage?: UsageRecord
  finishReason?: string
  citations?: Citation[]
  toolCalls?: ToolCall[]
  metadata?: Record<string, unknown>
}
```

The UI must not depend on provider-specific response formats.

------------------------------------------------------------------------

# 25. AI GATEWAY

All AI requests must pass through one centralized AI Gateway.

Responsibilities:

-   authentication context
-   authorization
-   entitlement
-   model availability
-   capability validation
-   credit reservation
-   cost estimation
-   routing
-   provider invocation
-   streaming
-   cancellation
-   normalized errors
-   usage recording
-   credit settlement
-   observability

Architecture:

``` text
Frontend
  ↓
Authentication
  ↓
Entitlement
  ↓
Credit / Usage
  ↓
AI Gateway
  ↓
Model Router
  ↓
Provider Adapter
  ↓
Provider
```

------------------------------------------------------------------------

# 26. MANDATORY AI REQUEST FLOW

``` text
User Request
     ↓
Authentication
     ↓
Request Validation
     ↓
Subscription / Plan Check
     ↓
Entitlement Check
     ↓
Capability Check
     ↓
Credit / Usage Check
     ↓
Rate Limit Check
     ↓
Estimated Cost Check
     ↓
Provider Budget Check
     ↓
Model Selection
     ↓
Provider Health Check
     ↓
Provider Adapter
     ↓
AI Model
     ↓
Response
     ↓
Usage Meter
     ↓
Credit Settlement
     ↓
Conversation / History
     ↓
User
```

No paid external request may bypass these controls.

------------------------------------------------------------------------

# 27. MODEL ROUTER

The router considers:

-   task type
-   required capability
-   user-selected model
-   model quality
-   latency
-   cost
-   user plan
-   credit balance
-   provider health
-   model health
-   context size
-   supported input/output
-   fallback rules
-   user preferences

Concept:

``` text
Request
 ↓
Capability
 ↓
Eligible Models
 ↓
Plan Filter
 ↓
Credit/Cost Filter
 ↓
Availability Filter
 ↓
Health Filter
 ↓
Quality/Speed Ranking
 ↓
Best Eligible Model
```

------------------------------------------------------------------------

# 28. TOOLHUB AUTO

`ToolHub Auto` is a routing experience.

It is not a proprietary foundation model claim.

Example:

``` text
User: Analyze this PDF
       ↓
Detect document/vision task
       ↓
Check plan + credits
       ↓
Select best eligible model
       ↓
Execute
```

Auto must obey all cost and entitlement controls.

------------------------------------------------------------------------

# 29. MODEL SELECTOR

The selector must be scalable.

Do not show hundreds/thousands of raw provider model IDs.

Recommended:

``` text
Select AI Model

Recommended
  Auto
  ToolHub Light
  ToolHub Pro

ToolHub AI
  Chat
  Reason
  Code
  Vision
  Creative
  Voice

OpenAI
  GPT ...

Google
  Gemini ...

Anthropic
  Claude ...

DeepSeek
  DeepSeek ...

Qwen
  Qwen ...

More providers
```

Show useful metadata:

-   provider
-   strengths
-   capability
-   plan
-   credits
-   vision/files where useful

------------------------------------------------------------------------

# 30. MODEL SEARCH

Search must support:

-   model name
-   provider
-   capability
-   aliases
-   product experience
-   tags

Examples:

``` text
coding
vision
fast
claude
gemini
deepseek
image
```

Results must already be filtered by user entitlement and availability.

------------------------------------------------------------------------

# 31. MODEL COMPARISON

A differentiating feature:

``` text
Prompt
  ↓
Select models
  ↓
Run in parallel where supported
  ↓
Model A | Model B | Model C
```

Actions:

-   Copy
-   Save
-   Continue
-   Retry
-   Regenerate
-   Select preferred result

Each executed request consumes its configured credits.

Show credit impact when appropriate.

------------------------------------------------------------------------

# 32. CONVERSATION MODEL SWITCHING

Users can switch:

``` text
GPT
 ↓
Gemini
 ↓
Claude
 ↓
DeepSeek
```

Context continues.

Provider-specific internal data must be normalized before sending to
another provider.

------------------------------------------------------------------------

# 33. STREAMING

Where supported, stream responses.

Required actions:

-   Stop generation
-   Retry
-   Regenerate
-   Continue where supported
-   Recover from errors

Do not wait for the entire response when streaming is available.

------------------------------------------------------------------------

# 34. FREE MODEL STRATEGY

Free users should receive useful limited access.

Important:

> Open-source weights do not automatically mean free hosted inference.

Distinguish:

``` text
Open model weights
Free API allowance
Paid API inference
Self-hosted inference
Infrastructure cost
```

Every candidate free model must pass a cost and license review.

------------------------------------------------------------------------

# 35. PREMIUM MODEL STRATEGY

Suggested plans:

``` text
Free
Basic
Pro
Business
Enterprise
```

Possible:

### Free

-   basic chat
-   light models
-   selected open/free models
-   limited vision/files
-   limited credits

### Pro

-   stronger reasoning
-   advanced coding
-   larger context
-   premium models
-   more credits
-   advanced research

### Business

-   higher limits
-   team features
-   organization billing

### Enterprise

-   enterprise controls
-   custom limits
-   custom features

Exact access must be configurable server-side.

------------------------------------------------------------------------

# 36. ENTITLEMENT SERVICE

Create one centralized service:

``` ts
canUseModel(user, model)
canUseCapability(user, capability)
canUseTool(user, tool)
getPlan(user)
getRemainingCredits(user)
```

Do not duplicate subscription logic across routes.

Frontend visibility is not security.

------------------------------------------------------------------------

# 37. CREDIT SYSTEM

Subscription does not imply unlimited expensive AI.

Use a centralized credit ledger.

Flow:

``` text
Request
 ↓
Estimate
 ↓
Reserve
 ↓
Provider execution
 ↓
Actual usage
 ↓
Settle
 ↓
Ledger entry
```

Never deduct credits only on the frontend.

------------------------------------------------------------------------

# 38. CREDIT LEDGER

Each entry should contain conceptually:

``` text
id
userId
requestId
type
amount
balanceBefore
balanceAfter
modelId
provider
estimatedCost
actualCost
status
createdAt
metadata
```

Ledger types:

``` text
grant
purchase
reservation
settlement
refund
expiration
adjustment
```

Balances must remain auditable.

------------------------------------------------------------------------

# 39. COST ENGINE

Keep provider cost and user credits separate.

``` text
Provider Cost
+
Infrastructure Cost
=
ToolHub Internal Cost

User Credit Cost
=
Revenue / Usage Allocation
```

Different capabilities must have different economics.

Do not use one universal credit multiplier.

------------------------------------------------------------------------

# 40. SPEND GUARD

Implement provider budget protection:

``` text
Monthly Provider Budget
       ↓
Spend Monitoring
       ↓
Warning Threshold
       ↓
Restriction Threshold
       ↓
Emergency Protection
```

Protect against:

-   bugs
-   bots
-   abuse
-   retry storms
-   coding-agent loops
-   batch requests
-   unexpected usage spikes

------------------------------------------------------------------------

# 41. RATE LIMITING

Apply rate limits at:

``` text
User
Account
IP where appropriate
Plan
Model
Provider
Tool
Endpoint
```

Heavy requests require stronger limits.

------------------------------------------------------------------------

# 42. FALLBACK

Production models should have controlled fallbacks.

``` text
Primary
 ↓ unavailable
Fallback
 ↓ unavailable
Secondary fallback
```

Fallback must respect:

-   entitlement
-   capability
-   credits
-   cost ceiling
-   provider health
-   user preference

Never silently switch to a materially more expensive model.

------------------------------------------------------------------------

# 43. PROVIDER HEALTH

Statuses:

``` text
Healthy
Degraded
Unavailable
Disabled
Coming Soon
```

Track:

-   success rate
-   latency
-   timeout rate
-   error rate
-   recent failures

Router must avoid unavailable/disabled models.

------------------------------------------------------------------------

# 44. MODEL LIFECYCLE

``` text
Discovery
 ↓
Evaluation
 ↓
License Review
 ↓
Commercial Review
 ↓
Privacy Review
 ↓
Cost Review
 ↓
Integration
 ↓
Testing
 ↓
Staging
 ↓
Production
 ↓
Monitoring
 ↓
Deprecation
```

Do not delete historical model references required for analytics or
billing.

------------------------------------------------------------------------

# 45. MODEL APPROVAL

Before production:

-   capability verified
-   quality benchmarked
-   latency measured
-   license reviewed
-   commercial use reviewed
-   attribution reviewed
-   privacy reviewed
-   API terms reviewed
-   rate limits known
-   pricing known
-   credit cost configured
-   fallback configured
-   streaming tested
-   tool calling tested if supported
-   health check tested
-   errors tested

------------------------------------------------------------------------

# 46. SECURITY

Mandatory:

-   provider keys server-side
-   authentication
-   authorization
-   entitlement checks
-   credit checks
-   rate limiting
-   request validation
-   file validation
-   abuse protection
-   audit logs
-   safe error messages

Never expose provider secrets to the browser.

------------------------------------------------------------------------

# 47. "ONLY GIVE SECRET KEYS" SETUP

The system should be easy to configure, but do not falsely assume
secrets are the only possible deployment settings.

Typical server-side configuration may include:

``` env
OPENAI_API_KEY=
GOOGLE_AI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
QWEN_API_KEY=
XAI_API_KEY=
HUGGINGFACE_API_KEY=
```

Only configure providers actually used.

The project may additionally require:

``` text
DATABASE_URL
AUTH_SECRET
APP_URL
STORAGE_CONFIG
PAYMENT_KEYS
WEBHOOK_SECRETS
ENCRYPTION_SECRET
```

The coding agent must discover the existing project's required variables
rather than inventing replacements.

------------------------------------------------------------------------

# 48. SECRET MANAGEMENT RULES

Never put provider secrets in:

-   React client code
-   browser localStorage
-   sessionStorage
-   public environment variables
-   HTML
-   API responses
-   logs
-   analytics

Secrets must remain server-side.

When admin configuration is supported:

``` text
Provider
Configured
Healthy
Last checked
```

Never display the complete secret after saving.

------------------------------------------------------------------------

# 49. PROVIDER CONFIGURATION

Provider state:

``` text
OpenAI
Configured
Healthy

Google
Configured
Healthy

Anthropic
Not configured

DeepSeek
Configured
Degraded
```

Missing optional provider configuration should not crash the entire
application.

Critical application secrets should fail fast safely.

------------------------------------------------------------------------

# 50. PROVIDER INTEGRATION WORKFLOW

For every provider:

``` text
Provider selected
 ↓
Secret configured
 ↓
Configuration validated
 ↓
Health check
 ↓
Models registered
 ↓
Capabilities verified
 ↓
Pricing configured
 ↓
Credits configured
 ↓
Plan access configured
 ↓
Fallback configured
 ↓
Tests
 ↓
Staging
 ↓
Production
```

A secret existing is not enough to mark a provider production-ready.

------------------------------------------------------------------------

# 51. OPEN MODEL / HUGGING FACE STRATEGY

Open-model ecosystem integration should be abstracted.

``` text
ToolHub AI
   ↓
Open Model Adapter
   ↓
Approved inference route
   ↓
Open model
```

Possible runtime routes:

-   approved hosted inference
-   approved inference providers
-   self-hosted inference
-   other legally usable sources

Do not assume every open model has the same license, cost, runtime, or
capability.

The UI should remain ToolHub AI branded while required attribution
remains available.

------------------------------------------------------------------------

# 52. SELF-HOSTED FUTURE

Architecture should allow:

``` text
ToolHub AI
 ↓
Model Router
 ↓
SelfHostedAdapter
 ↓
GPU inference service
```

Self-hosting introduces:

-   GPU cost
-   scaling
-   deployment
-   monitoring
-   model serving
-   security
-   maintenance

Do not self-host simply because a model is open-source.

------------------------------------------------------------------------

# 53. FILE/PDF WORKSPACE

Support:

-   uploads
-   PDFs
-   text documents
-   images
-   structured extraction
-   summarization
-   Q&A
-   file-based conversations

Flow:

``` text
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
```

Large files should use asynchronous processing where necessary.

------------------------------------------------------------------------

# 54. VISION

Vision-capable models may process:

-   photos
-   screenshots
-   UI screenshots
-   documents
-   charts
-   diagrams

The UI must indicate Vision capability only when the selected model
supports it.

------------------------------------------------------------------------

# 55. WEB RESEARCH

Research is a capability layer.

Do not pretend every model has native web access.

Concept:

``` text
Research
 ↓
Search / Retrieval
 ↓
Sources
 ↓
AI model
 ↓
Source-aware response
```

------------------------------------------------------------------------

# 56. EMBEDDINGS / RAG

``` text
Document
 ↓
Chunking
 ↓
Embedding model
 ↓
Vector store
 ↓
Semantic retrieval
 ↓
Relevant context
 ↓
Generation model
```

Embedding models belong in the Model Registry but are not ordinary chat
models.

------------------------------------------------------------------------

# 57. IMAGE GENERATION / EDITING

Treat these as separate capabilities.

Do not assume a chat model can generate/edit images.

UI should clearly distinguish:

``` text
Generate
Edit
Upscale
Background
Restore
```

Only expose operations supported by the selected provider/model.

------------------------------------------------------------------------

# 58. AUDIO

Speech-to-Text:

``` text
Audio
 ↓
Validation
 ↓
STT model
 ↓
Transcript
```

Text-to-Speech:

``` text
Text
 ↓
TTS model
 ↓
Audio
```

Track duration and cost separately.

------------------------------------------------------------------------

# 59. VIDEO

Video operations must use stronger financial controls.

Use:

-   entitlement
-   credit estimate
-   spend guard
-   job queue
-   async processing
-   progress
-   cancellation
-   failure recovery

Do not perform expensive video generation as an uncontrolled synchronous
request.

------------------------------------------------------------------------

# 60. AI WORKSPACE UI

The AI Workspace should be professional software.

Concept:

``` text
┌──────────────────────────────────────────────────────────────┐
│ ToolHub AI       Search   Theme   Profile                    │
├──────────────────┬───────────────────────────────────────────┤
│ + New Chat       │                                           │
│ Models           │              Conversation                  │
│ Projects         │                                           │
│ Recent           │                                           │
│ Conversations   │                                           │
│ Settings        │                                           │
│ Help            │      Composer / Model / Tools              │
└──────────────────┴───────────────────────────────────────────┘
```

Rules:

-   no public marketing navigation inside focused workspace
-   sidebar owns workspace navigation
-   header owns search/theme/account utilities
-   conversation is primary
-   compare is contextual
-   usage is contextual
-   future agents/research/files/vision appear contextually

------------------------------------------------------------------------

# 61. AI COMPOSER

Support:

-   text
-   attachments
-   files
-   images
-   model selector
-   tools
-   research/web where supported
-   send
-   stop

Keep the composer visually calm and focused.

------------------------------------------------------------------------

# 62. QUICK WORKFLOWS

Examples:

``` text
Email drafting
Translation
Summarization
Explain
Brainstorm
Rewrite
Meeting notes
Code review
Data extraction
Research
File Q&A
```

All workflows use the same AI Gateway.

------------------------------------------------------------------------

# 63. AGENTS --- FUTURE ARCHITECTURE

Leave room for:

``` text
User Goal
 ↓
Agent
 ├── Model
 ├── Tools
 ├── Files
 ├── Web
 ├── Memory
 └── Tasks
```

Agents must use the same:

-   entitlement
-   credits
-   rate limits
-   spend guard
-   audit logs
-   tool permissions

Add agents incrementally after the core multi-model architecture is
stable.

------------------------------------------------------------------------

# 64. MODEL ECONOMICS

Classify models:

``` text
Free / Traffic
Low Cost
Standard
Premium
High Cost
Experimental
```

The router may use this classification.

A premium model must never be routed to a free user simply because the
frontend allows it.

------------------------------------------------------------------------

# 65. MODEL RANKING

Rank by:

``` text
Capability match
+
Quality
+
Reliability
+
Speed
+
Cost
+
User plan
+
User preference
+
Provider health
```

Do not rank only by benchmark quality.

------------------------------------------------------------------------

# 66. USER MODEL UX

Default:

``` text
Auto · Recommended
```

Advanced:

``` text
Choose Model
```

Power users:

``` text
Compare
```

This is progressive disclosure.

------------------------------------------------------------------------

# 67. PREMIUM UX

Show:

``` text
Claude
Writing & reasoning
Premium · 8 credits
```

or:

``` text
Requires Pro
```

Provide:

``` text
[Upgrade]
[Choose another model]
```

Do not repeatedly interrupt active workflows with upgrade dialogs.

------------------------------------------------------------------------

# 68. COST TRANSPARENCY

For expensive operations:

``` text
Estimated cost: 20 credits
```

After completion:

``` text
Used: 18 credits
```

Never surprise users with unexplained credit consumption.

------------------------------------------------------------------------

# 69. AUTO TRANSPARENCY

When appropriate:

``` text
Auto selected Claude for this request.
```

If provider details are hidden from normal UI, the backend must still
record the real provider/model.

------------------------------------------------------------------------

# 70. CONVERSATION PERSISTENCE

Authenticated conversations should preserve:

``` text
Conversation
Messages
Attachments
Model selections
Usage
Project
Timestamps
```

Users must be able to continue later.

------------------------------------------------------------------------

# 71. PROJECT ARCHITECTURE

``` text
Project
 ├── Conversations
 ├── Files
 ├── Saved Results
 └── Workflows
```

Cross-workspace context should remain coherent.

------------------------------------------------------------------------

# 72. USAGE DASHBOARD

Show:

``` text
AI Credits
Credits used
Credits remaining
Requests
Model usage
Capability usage
Recent activity
```

Example:

``` text
AI Credits
742 / 1000 used

Chat       320
Code       210
Vision      90
Image       80
Other       42
```

Keep charts readable and restrained.

------------------------------------------------------------------------

# 73. BILLING ARCHITECTURE

``` text
Payment
 ↓
Subscription
 ↓
Plan
 ↓
Entitlements
 ↓
Credit allocation
 ↓
Model access
```

Backend subscription state is authoritative.

------------------------------------------------------------------------

# 74. DATABASE CONCEPTS

The existing project stack determines exact schema, but the architecture
should support:

``` text
User
Subscription
Plan
Entitlement
Provider
Model
ModelCapability
Conversation
Message
Attachment
Project
UsageRecord
CreditWallet
CreditLedgerEntry
ProviderSpend
ModelHealth
ProviderHealth
AIRequest
AuditLog
```

Do not create duplicate tables if the existing project already has
equivalent entities.

------------------------------------------------------------------------

# 75. OBSERVABILITY

Track:

-   request success rate
-   error rate
-   latency
-   model usage
-   provider usage
-   credit usage
-   token usage where available
-   abandoned requests
-   retry rate
-   fallback rate
-   estimated cost
-   actual cost

Do not store sensitive user content unnecessarily.

------------------------------------------------------------------------

# 76. ERROR UX

User-facing errors should be normalized:

``` text
The selected model is temporarily unavailable.

[Retry]
[Use Auto]
```

Never expose:

-   API keys
-   raw provider stack traces
-   internal URLs
-   database errors
-   infrastructure secrets

------------------------------------------------------------------------

# 77. RETRY POLICY

Use:

-   bounded retries
-   exponential backoff where appropriate
-   idempotency where supported
-   request IDs
-   provider-aware retry classification

Never endlessly retry paid requests.

------------------------------------------------------------------------

# 78. FINANCIAL SAFETY TESTS

### Free user requests premium model

Expected:

``` text
Rejected before provider call.
```

### User has zero credits

Expected:

``` text
Rejected before provider call.
```

### Provider budget exceeded

Expected:

``` text
Rejected or routed to eligible lower-cost option.
```

### Provider fails

Expected:

``` text
Controlled fallback.
```

### Frontend sends premium model ID

Expected:

``` text
Backend enforces entitlement.
```

### Frontend lies about credits

Expected:

``` text
Backend uses authoritative ledger.
```

------------------------------------------------------------------------

# 79. MODEL SECURITY TEST

Attempt:

``` text
POST /api/ai/generate
modelId = premium-model
```

with a Free account.

Expected:

``` text
401/403-style authorization failure or product-safe denial.
No provider request.
No credit mutation.
```

Never rely on UI hiding.

------------------------------------------------------------------------

# 80. MODEL AVAILABILITY API

Frontend should receive normalized, already-filtered model data.

Example:

``` json
{
  "models": [
    {
      "id": "toolhub-auto",
      "displayName": "Auto",
      "provider": "toolhub",
      "tier": "free",
      "available": true,
      "capabilities": ["chat", "reasoning", "coding"]
    }
  ]
}
```

Backend must apply:

-   plan filtering
-   availability
-   capability filtering
-   provider health
-   product visibility

------------------------------------------------------------------------

# 81. MODEL UI CARDS

Compact card:

``` text
┌────────────────────────────────────────────┐
│ Claude                         Premium     │
│ Writing & reasoning                         │
│ Vision · Files                  8 credits  │
└────────────────────────────────────────────┘
```

Provider branding should remain subtle and ToolHub's overall visual
identity should dominate.

------------------------------------------------------------------------

# 82. OPEN MODEL UI

Example:

``` text
ToolHub Code
Optimized for coding
Based on an approved open model
```

Do not make "Hugging Face" the main product identity merely because an
open model came from that ecosystem.

Attribution should be shown when required.

------------------------------------------------------------------------

# 83. ATTRIBUTION METADATA

Model records should support:

``` text
license
attribution
officialName
provider
source
commercialUse
redistribution
termsReference
privacyNotes
```

Rendering must be driven by the model metadata and legal review.

------------------------------------------------------------------------

# 84. PROVIDER-AGNOSTIC FRONTEND

Frontend components should consume:

``` text
Model
Provider
Capability
Entitlement
Usage
```

They must not contain:

``` text
if provider === "openai"
if provider === "anthropic"
if provider === "google"
```

Provider-specific behavior belongs in backend adapters and normalized
capabilities.

------------------------------------------------------------------------

# 85. NEW PROVIDER ADDITION

Adding a provider should be approximately:

``` text
1. Provider record
2. Adapter
3. Secret
4. Configuration validation
5. Models
6. Capabilities
7. Pricing
8. Credits
9. Plan access
10. Health
11. Fallback
12. Tests
13. Staging
14. Production
```

No full frontend redesign.

------------------------------------------------------------------------

# 86. NEW MODEL ADDITION

Adding a model should primarily require:

``` text
Model Registry
+
Adapter support
+
Capabilities
+
Pricing
+
Credits
+
Plan access
+
Health
+
Fallback
+
License/attribution review
```

The UI should render it automatically from normalized registry data.

------------------------------------------------------------------------

# 87. NO PROVIDER LOCK-IN

The architecture must survive a provider becoming:

-   too expensive
-   unavailable
-   unreliable
-   restricted
-   deprecated

Eligible workloads should be able to use another provider/model.

------------------------------------------------------------------------

# 88. NO MODEL LOCK-IN

Where practical, maintain multiple models per capability.

Example:

``` text
Coding
 ├── OpenAI
 ├── Claude
 ├── DeepSeek
 ├── Qwen
 └── Approved open model
```

This improves:

-   reliability
-   price competition
-   user choice
-   fallback
-   resilience

------------------------------------------------------------------------

# 89. PERFORMANCE

AI UI must remain responsive during:

-   streaming
-   large file uploads
-   model comparison
-   model search
-   long conversations

Use where appropriate:

-   pagination
-   virtualization
-   debounced search
-   lazy loading
-   async jobs
-   streaming

Do not render thousands of model records simultaneously.

------------------------------------------------------------------------

# 90. TESTING STRATEGY

## Unit

Test:

-   Model Registry
-   Provider Registry
-   adapters
-   entitlement
-   credits
-   cost engine
-   router
-   fallback
-   health

## Integration

Test:

``` text
User
 ↓
Gateway
 ↓
Router
 ↓
Adapter
 ↓
Provider mock
 ↓
Usage
 ↓
Credits
```

## E2E

Test:

-   Free user
-   Basic user
-   Pro user
-   premium model
-   insufficient credits
-   provider failure
-   fallback
-   streaming
-   file upload
-   vision
-   model switching
-   compare

------------------------------------------------------------------------

# 91. UI QA

## Visual

-   [ ] Matches `/tools`
-   [ ] Matches Mega Menu
-   [ ] Same background system
-   [ ] No unrelated gradients
-   [ ] Typography consistent
-   [ ] Icons consistent
-   [ ] Borders consistent
-   [ ] Radius consistent
-   [ ] Spacing consistent

## Navigation

-   [ ] Header consistent
-   [ ] Sidebar consistent
-   [ ] Active state correct
-   [ ] No collision
-   [ ] Mobile navigation works

## Profile

-   [ ] Avatar opens dropdown
-   [ ] Dropdown anchored
-   [ ] Dropdown is overlay
-   [ ] Does not enter document flow
-   [ ] Escape works
-   [ ] Outside click works
-   [ ] Keyboard works

## Projects

-   [ ] Correct page header
-   [ ] New Project CTA correct
-   [ ] Empty state proportional
-   [ ] shadcn Dialog
-   [ ] No browser prompt
-   [ ] Validation

------------------------------------------------------------------------

# 92. AI MODEL QA

-   [ ] Provider configured
-   [ ] Model registered
-   [ ] Capability correct
-   [ ] Plan access correct
-   [ ] Credit cost correct
-   [ ] Health works
-   [ ] Streaming tested
-   [ ] Errors normalized
-   [ ] Fallback tested
-   [ ] Cost protection tested
-   [ ] Usage recorded
-   [ ] Credits settled
-   [ ] Secrets remain server-side
-   [ ] License reviewed
-   [ ] Commercial use reviewed
-   [ ] Attribution reviewed
-   [ ] Privacy reviewed

------------------------------------------------------------------------

# 93. CODING AGENT IMPLEMENTATION ORDER

## P0 --- Inspect and preserve

1.  Inspect repository.
2.  Identify `/tools` design tokens.
3.  Identify Mega Menu components.
4.  Identify existing shadcn components.
5.  Identify auth.
6.  Identify subscription/billing.
7.  Identify database.
8.  Identify storage.
9.  Identify current AI routes.
10. Do not replace working infrastructure unnecessarily.

## P1 --- AI foundation

11. Provider Registry
12. Model Registry
13. Capability Registry
14. Normalized request/response
15. Provider Adapter interface
16. AI Gateway
17. Model Router
18. Entitlement Service
19. Credit Service
20. Cost Engine
21. Spend Guard
22. Usage Meter
23. Health Service
24. Fallback Service

## P2 --- providers

25. First provider
26. Second provider
27. Additional providers
28. Open-model adapter
29. Future-provider abstraction
30. Configuration validation
31. Health checks

## P3 --- workspace

32. Model selector
33. Auto
34. Chat
35. Streaming
36. Model switching
37. Attachments
38. Vision
39. Files
40. Compare
41. Usage display

## P4 --- business

42. Plans
43. Entitlements
44. Credits
45. Ledger
46. Cost tracking
47. Spend guard
48. Usage
49. Billing

## P5 --- UI

50. Unify Dashboard shell
51. Remove unrelated backgrounds
52. Normalize icons
53. Normalize spacing
54. Normalize borders/radius
55. Fix profile dropdown
56. Replace browser prompts
57. Improve empty states
58. Responsive
59. Accessibility

## P6 --- verify

60. Unit tests
61. Integration tests
62. E2E tests
63. Financial safety tests
64. Provider failure tests
65. Entitlement tests
66. Responsive QA
67. Visual regression
68. Production configuration verification

------------------------------------------------------------------------

# 94. CODING AGENT RULES

The coding agent must:

1.  Read this document before implementing AI architecture.
2.  Inspect existing code before creating files.
3.  Reuse existing components.
4.  Reuse existing design tokens.
5.  Reuse existing auth/billing/credits infrastructure.
6.  Avoid duplicate services.
7.  Keep provider-specific logic out of frontend.
8.  Never expose secrets.
9.  Never bypass server-side entitlement.
10. Never bypass credits.
11. Never introduce unrelated UI libraries.
12. Never introduce a Dashboard-only theme.
13. Use shadcn/ui.
14. Use Lucide.
15. Preserve working routes and features.
16. Prefer incremental changes.
17. Add tests for critical business logic.
18. Do not fabricate integrations.
19. If capability/pricing/license is uncertain, mark it for
    verification.
20. Never claim integration is complete until it is actually tested.

------------------------------------------------------------------------

# 95. DO-NOT-GUESS RULE

If something exists in the repository:

``` text
Inspect first
Understand second
Modify third
```

Never:

``` text
Assume
Rewrite
Replace
```

Do not invent:

-   provider API endpoints
-   model IDs
-   prices
-   free inference
-   commercial rights
-   model capabilities
-   licenses

When uncertain, make the implementation configurable and explicitly mark
the item for verification.

------------------------------------------------------------------------

# 96. PRODUCT DIFFERENTIATION

ToolHub AI should differentiate through:

1.  One interface for many providers.
2.  One conversation across model switching.
3.  Auto routing.
4.  Model comparison.
5.  Tool + model integration.
6.  Files + AI.
7.  Projects + AI.
8.  Creative workspace.
9.  Useful free tools.
10. Premium professional UX.
11. Cost-aware routing.
12. Future agent architecture.

The goal is not to imitate ChatGPT, Gemini, Claude, or Vercel.

The goal is to build a stronger, coherent ToolHub AI product.

------------------------------------------------------------------------

# 97. LONG-TERM ECOSYSTEM

``` text
ToolHub AI
│
├── AI Workspace
│   ├── Chat
│   ├── Reasoning
│   ├── Coding
│   ├── Vision
│   ├── Research
│   ├── Files
│   └── Agents
│
├── Creative Workspace
│   ├── Image Generation
│   ├── Image Editing
│   ├── Product Photography
│   └── Creative Workflows
│
├── Tool Ecosystem
│   ├── Image
│   ├── Developer
│   ├── Productivity
│   └── Utility
│
├── Model Ecosystem
│   ├── ToolHub Experiences
│   ├── OpenAI
│   ├── Google
│   ├── Anthropic
│   ├── DeepSeek
│   ├── Qwen
│   ├── Meta
│   ├── xAI
│   ├── Mistral
│   ├── Open Models
│   └── Future Providers
│
└── Business Layer
    ├── Subscriptions
    ├── Credits
    ├── Usage
    ├── Billing
    ├── Provider Budgets
    └── Analytics
```

------------------------------------------------------------------------

# 98. FINAL DEFINITION OF DONE --- ARCHITECTURE

-   [ ] Ten capability categories supported
-   [ ] Provider Registry
-   [ ] Model Registry
-   [ ] Capability Registry
-   [ ] Provider Adapter architecture
-   [ ] AI Gateway
-   [ ] Model Router
-   [ ] Entitlement Service
-   [ ] Credit Wallet
-   [ ] Credit Ledger
-   [ ] Cost Engine
-   [ ] Spend Guard
-   [ ] Rate Limiting
-   [ ] Usage Meter
-   [ ] Provider Health
-   [ ] Fallback
-   [ ] Secure secrets
-   [ ] License/commercial review
-   [ ] Privacy review
-   [ ] Model lifecycle
-   [ ] Benchmarking
-   [ ] Monitoring
-   [ ] Tests
-   [ ] No uncontrolled paid API request

------------------------------------------------------------------------

# 99. FINAL DEFINITION OF DONE --- UI

-   [ ] Clearly ToolHub AI
-   [ ] `/tools` language preserved
-   [ ] Mega Menu language preserved
-   [ ] shadcn/ui
-   [ ] Lucide
-   [ ] Same colors/backgrounds
-   [ ] No separate dashboard theme
-   [ ] No accidental gradients
-   [ ] Header/sidebar unified
-   [ ] Profile dropdown correctly layered
-   [ ] Project creation uses Dialog
-   [ ] Responsive
-   [ ] Accessible
-   [ ] Loading/error/success states
-   [ ] Scalable model selector
-   [ ] Official provider identities preserved
-   [ ] Open-model attribution supported
-   [ ] Premium UX is subtle
-   [ ] No design drift

------------------------------------------------------------------------

# 100. FINAL BUSINESS SAFETY CHECKLIST

-   [ ] No frontend provider API calls
-   [ ] No secrets in client bundle
-   [ ] No secrets in logs
-   [ ] No unauthorized premium requests
-   [ ] No client-controlled credit deduction
-   [ ] No unlimited expensive requests
-   [ ] No uncontrolled retries
-   [ ] Provider monthly budget
-   [ ] Warning threshold
-   [ ] Restriction threshold
-   [ ] Emergency protection
-   [ ] User rate limits
-   [ ] Model rate limits
-   [ ] Provider rate limits
-   [ ] Usage audit trail
-   [ ] Cost audit trail

------------------------------------------------------------------------

# 101. FINAL CODING AGENT INSTRUCTION

Before changing the repository, the coding agent must:

1.  Read this entire specification.
2.  Inspect the current repository architecture.
3.  Identify existing compatible functionality.
4.  Identify design tokens and `/tools` patterns.
5.  Identify Mega Menu patterns.
6.  Identify existing AI/provider code.
7.  Identify existing subscription/credit/billing code.
8.  Produce a safe implementation plan.
9.  Implement incrementally.
10. Reuse existing infrastructure.
11. Run type checks/lint/tests.
12. Verify UI visually.
13. Verify server-side financial protection.
14. Verify provider secrets.
15. Verify entitlement.
16. Verify responsive behavior.
17. Verify no design drift.

**Do not rewrite the project merely to introduce the multi-model
architecture.**

------------------------------------------------------------------------

# 102. FINAL PRODUCT PRINCIPLE

ToolHub AI should feel simple to users and sophisticated behind the
scenes.

``` text
                         TOOLHUB AI
                              |
        +---------------------+---------------------+
        |                     |                     |
   Tool Ecosystem       Model Ecosystem       Business Layer
        |                     |                     |
      Tools              Model Registry        Subscriptions
      Workflows          Provider Registry     Credits
      Creative           Model Router          Usage
      Productivity       Fallback              Cost
                          Health                Spend Guard
        |                     |                     |
        +---------------------+---------------------+
                              |
                       Unified AI Workspace
                              |
                          User Experience
```

The user sees:

> **One polished ToolHub AI product.**

Behind the scenes ToolHub manages:

> **tools + models + providers + routing + cost + subscriptions +
> credits + usage + reliability + security.**

------------------------------------------------------------------------

# 103. FINAL STATEMENT

**One Product. Many Models. One Consistent Experience.**

ToolHub AI must become a professional AI workspace where users can
access the best eligible models and capabilities through one coherent
interface, while ToolHub retains control over security, cost, credits,
subscriptions, reliability, provider routing, and future expansion.

The platform must be:

-   professional
-   scalable
-   provider-agnostic
-   financially controlled
-   secure
-   accessible
-   responsive
-   visually consistent
-   premium without unnecessary decoration
-   ready for future models
-   ready for future providers
-   ready for future agents

**End of Master Specification.**
