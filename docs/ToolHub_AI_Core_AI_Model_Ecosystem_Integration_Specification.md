# ToolHub AI — Core AI Model Ecosystem & Integration Specification

**Status:** Approved Core Scope  
**Product:** ToolHub AI  
**Scope:** Initial AI model ecosystem and scalable integration architecture

## 1. Core AI Capability Scope

The initial platform will support exactly these ten capability categories:

1. **General Chat / LLM** — conversation, Q&A, writing.
2. **Reasoning** — complex problems, mathematics, analysis, planning.
3. **Coding** — code generation, debugging, refactoring, coding-agent workloads.
4. **Vision** — image, PDF, and document understanding.
5. **Image Generation** — text → image.
6. **Image Editing** — image → modified image.
7. **Speech-to-Text** — audio → text.
8. **Text-to-Speech** — text → voice.
9. **Embeddings** — semantic search, RAG, document search.
10. **Video** — text/image → video and/or video understanding where real provider/model capability exists.

These are **capability categories, not individual models**. Each category may contain multiple models.

## 2. Strategic Principle

ToolHub AI does **not** need to train its own foundation model for the initial platform.

The initial strategy is to integrate suitable external APIs, open/free models, Hugging Face models, and other legally usable model sources through a controlled ToolHub backend.

ToolHub remains the product and brand layer. Provider/model implementation remains behind the backend abstraction.

## 3. High-Level Architecture

```text
                         TOOLHUB AI
                              |
                 +------------+------------+
                 |                         |
            Tool Registry             Model Registry
                 |                         |
                 +------------+------------+
                              |
                       Model Router
                              |
             +----------------+----------------+
             |                |                |
       Provider Adapter  Provider Adapter  Provider Adapter
             |                |                |
          API Provider     Hugging Face     Other Provider
```

The frontend must never directly call paid model providers.

## 4. Mandatory AI Request Flow

```text
User Request
     ↓
Authentication
     ↓
Subscription / Plan Check
     ↓
Entitlement Check
     ↓
Credit / Usage Check
     ↓
Rate Limit Check
     ↓
Estimated Cost Check
     ↓
Provider Budget Check
     ↓
Model Selection / Routing
     ↓
Provider Adapter
     ↓
AI Model
     ↓
Response
     ↓
Usage Meter
     ↓
Credit Deduction
     ↓
User
```

No paid external AI request may bypass these controls.

## 5. Model Registry

The Model Registry is the source of truth for production models.

Each model should conceptually contain:

```text
id
displayName
capability
provider
status
availability
pricing
creditCost
supportedInputs
supportedOutputs
contextLimit
streamingSupport
toolCallingSupport
planAccess
rateLimit
fallbackModels
enabled
metadata
```

Only verified model records may be exposed to production routing.

## 6. Provider Registry & Adapter Architecture

Providers must be abstracted behind adapters.

```text
Model Router
      ↓
Provider Adapter Interface
      ↓
+-------------+-------------+-------------+
| Provider A  | Provider B  | Provider C  |
| Adapter     | Adapter     | Adapter     |
+-------------+-------------+-------------+
```

Provider-specific API calls must remain inside backend adapters.

A provider can be replaced without redesigning the frontend.

## 7. Model Router

The Model Router is a critical ToolHub service.

It must consider:

- required capability
- model quality
- speed/latency
- cost
- user plan
- credit balance
- provider availability
- model health
- fallback rules
- task requirements

Conceptually:

```text
User Request
 ↓
Required Capability
 ↓
Eligible Models
 ↓
Plan Filter
 ↓
Credit/Cost Filter
 ↓
Availability Filter
 ↓
Quality/Speed Ranking
 ↓
Best Eligible Model
```

## 8. ToolHub Auto

**ToolHub Auto** is a routing experience, not a claim of a proprietary foundation model.

Example:

```text
User → "Analyze this PDF"
       ↓
Detect document/vision task
       ↓
Check plan + credits
       ↓
Select best eligible model
       ↓
Execute
```

## 9. ToolHub Model Experiences

The UI may expose curated ToolHub experiences:

- **ToolHub Auto** — recommended automatic routing
- **ToolHub Light** — fast/low-cost
- **ToolHub Flash** — very fast
- **ToolHub Pro** — advanced capability
- **ToolHub Frontier** — highest capability
- **ToolHub Vision** — vision/document workloads
- **ToolHub Creative** — creative/image workloads
- **ToolHub Voice** — speech workloads
- **ToolHub Code** — coding workloads

These are ToolHub product experiences/routing profiles. They must not be presented as proprietary foundation models unless ToolHub actually operates such models.

## 10. Free Model Strategy

Free users may receive access to genuinely free or appropriately licensed/available models.

However:

> Free model weights do not automatically mean unlimited free inference.

The system must distinguish between:

- free/open model weights
- free API allowance
- paid API inference
- self-hosted inference
- infrastructure cost

Every candidate must be reviewed before entering the free tier.

## 11. Commercial / License Verification

Before production integration, verify:

- model license
- commercial-use permission
- API terms
- redistribution requirements
- attribution requirements
- acceptable-use restrictions
- data/privacy terms
- provider billing terms
- rate limits

A public model is not automatically suitable for commercial SaaS use.

## 12. Paid Models & Subscriptions

Premium models are available according to subscription/entitlement.

Recommended plan structure:

```text
Free
Basic
Pro
Business
Enterprise
```

Exact plan details may be defined separately.

Backend entitlement checks are mandatory.

## 13. Credits / Usage Wallet

Subscription should not imply unlimited expensive AI usage.

Use a credit-based usage system.

Example only:

```text
Pro Plan
1000 AI Credits

Light request       -1
Flash request       -2
Pro request         -8
Frontier request   -20
Image generation   -15
Video generation   -50
```

These values are placeholders and must be calculated from real provider costs and target margins.

## 14. Financial Protection

Before any paid request:

```text
Authentication
 ↓
Plan entitlement
 ↓
Credit balance
 ↓
Estimated provider cost
 ↓
Rate limit
 ↓
Global provider budget
 ↓
Execute
```

If a condition fails, reject or route to an eligible lower-cost/free option.

### Non-negotiable rule

> No AI request may reach an external paid provider until authentication, entitlement, credit availability, rate limit, estimated cost, and provider-budget checks have passed.

This must be enforced server-side.

## 15. Spend Guard

Implement configurable provider spending protection.

```text
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

This protects against bugs, abuse, automation, runaway requests, and unexpected provider costs.

## 16. Rate Limiting

Rate limits should exist at appropriate levels:

- user
- account
- plan
- model
- provider
- tool
- API endpoint

Important limits must be enforced server-side.

## 17. Usage Meter

Track, where applicable:

- request count
- input tokens
- output tokens
- image count/resolution
- audio duration
- video duration
- processing time
- provider
- model
- credits consumed
- estimated cost
- actual cost
- success/failure

This supports billing, analytics, abuse detection, routing, and profitability analysis.

## 18. Cost vs Credit

Keep these separate:

```text
Provider Cost
+
Infrastructure Cost
=
ToolHub Internal Cost

User Credit Cost
=
Revenue / Usage Allocation
```

Do not use one universal credit multiplier for every capability.

## 19. Fallback

Production models should have fallback rules where technically possible.

```text
Primary Model
 ↓ unavailable
Fallback Model
 ↓ unavailable
Secondary Fallback
```

Fallback must respect:

- user plan
- credit balance
- capability
- cost ceiling
- provider availability

Never silently route a user to a significantly more expensive model without authorization.

## 20. Tool Registry vs Model Registry

These must remain separate systems.

```text
Tool Registry
├── PDF tools
├── Image tools
├── Audio tools
├── Video tools
└── Productivity tools

Model Registry
├── General Chat
├── Reasoning
├── Coding
├── Vision
├── Image Generation
├── Image Editing
├── Speech-to-Text
├── Text-to-Speech
├── Embeddings
└── Video
```

Then:

```text
Tool
 ↓
Required Capability
 ↓
Model Router
 ↓
Eligible Model
```

This separation is mandatory for long-term scalability.

## 21. AI Workspace

The AI Workspace should be the unified work environment:

```text
User
 ↓
Choose / Auto-detect task
 ↓
Select tool if needed
 ↓
ToolHub Auto / selected experience
 ↓
Model Router
 ↓
Processing
 ↓
Result
 ↓
Save / Download / Share / History
```

The user should not need to understand provider complexity.

## 22. Security

Provider API keys must never be exposed in frontend code.

Provider credentials must remain server-side using secure secrets management.

Enforce:

- authentication
- authorization
- entitlement checks
- rate limits
- credit checks
- spending limits
- request validation
- structured provider error handling

## 23. Reliability

Support:

- safe retries
- timeouts
- provider health checks
- circuit breakers where appropriate
- fallback models
- graceful degradation
- streaming where supported
- cancellation where supported
- structured errors

Do not endlessly retry paid requests.

## 24. Data & Privacy Review

Before integrating a provider, review:

- input storage
- training/data-use policy
- retention
- geographic processing
- privacy terms
- deletion options
- sensitive-data handling

ToolHub must not claim stronger privacy guarantees than the underlying infrastructure provides.

## 25. Model Approval Process

Do not integrate models merely because they are popular.

Evaluate every candidate for:

1. Capability
2. Quality
3. Speed
4. Cost
5. License
6. Commercial usability
7. API reliability
8. Context length
9. Modalities
10. Tool/function calling
11. Streaming
12. Rate limits
13. Privacy/data policy
14. Provider stability
15. Fallback availability

Only approved models enter the production Model Registry.

## 26. Model Benchmarking

Benchmark according to capability.

### General Chat
- instruction following
- writing quality
- factuality

### Reasoning
- mathematics
- multi-step reasoning
- planning

### Coding
- code correctness
- debugging
- repository tasks

### Vision
- OCR
- document understanding
- visual reasoning

### Image
- prompt adherence
- quality
- editing accuracy

### Speech
- transcription accuracy
- language support

### Embeddings
- retrieval quality
- semantic similarity

### Video
- generation quality
- temporal consistency
- understanding quality

## 27. Model Health

Production models should expose:

```text
Healthy
Degraded
Unavailable
Disabled
Coming Soon
```

The router must not select unavailable or disabled models.

## 28. Model Lifecycle

```text
Discovery
 ↓
Evaluation
 ↓
License Review
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

Historical model references must not be deleted if required for billing or analytics.

## 29. UI/UX Requirements

The model ecosystem must follow the existing ToolHub AI design system.

Mandatory:

- existing ToolHub brand identity
- existing `/tools` visual language
- existing Mega Menu visual language
- shadcn/ui
- Lucide icons
- existing typography
- existing spacing
- existing colors/backgrounds
- subtle borders
- professional responsive behavior

Vercel-inspired means clean, minimal, premium, restrained, precise, and well-structured. It does **not** mean copying Vercel.

The new AI ecosystem must improve the existing UI without replacing or breaking the established ToolHub visual identity.

## 30. Scalable UI Principle

The platform may eventually contain a very large number of tools and models.

The UI must therefore prioritize:

- search
- categorization
- favorites
- recent items
- recommendations
- clear model hierarchy
- progressive disclosure
- compact but readable controls
- consistent workspace navigation

Do not expose an uncontrolled list of hundreds/thousands of raw provider models to ordinary users.

## 31. Free-to-Paid Conversion

Free users should receive useful limited AI access.

Example:

```text
FREE
✓ Limited ToolHub Light
✓ Limited ToolHub Flash
✕ Pro
✕ Frontier
✕ High-cost premium operations
```

Show usage clearly:

```text
You've used 92% of your free AI credits.

[ Upgrade Plan ]
```

Never create unexpected provider charges for the user.

## 32. Initial Rollout

Do not launch with an uncontrolled number of models.

Start with a curated model set covering all ten approved capability categories.

Expand based on:

- user demand
- quality benchmarks
- provider reliability
- cost
- profitability
- latency
- actual usage

The architecture must support expansion without requiring a frontend redesign.

## 33. Definition of Done

- [ ] All ten approved capability categories exist.
- [ ] Model Registry exists.
- [ ] Provider Registry exists.
- [ ] Provider Adapter architecture exists.
- [ ] Model Router exists.
- [ ] Tool Registry and Model Registry are separate.
- [ ] Subscription/entitlement checks exist.
- [ ] Credit/usage system exists.
- [ ] Cost engine exists.
- [ ] Usage meter exists.
- [ ] Rate limiting exists.
- [ ] Provider spend guard exists.
- [ ] Fallback rules exist.
- [ ] API keys are server-side only.
- [ ] License/commercial-use verification is part of model onboarding.
- [ ] Free and premium access is enforced server-side.
- [ ] AI Workspace integrates with the model layer.
- [ ] ToolHub's existing brand/UI system is preserved.
- [ ] shadcn/ui is used.
- [ ] Lucide icons are used.
- [ ] Vercel-inspired principles are followed without copying Vercel.
- [ ] Production models are benchmarked.
- [ ] Model health monitoring exists.
- [ ] Model lifecycle management exists.
- [ ] No uncontrolled paid API request can occur.

## 34. Final Principle

ToolHub AI should not become a simple collection of third-party AI APIs.

The target is:

```text
                    TOOLHUB AI
                         |
       +-----------------+-----------------+
       |                 |                 |
   Tool Ecosystem    Model Ecosystem   Business Layer
       |                 |                 |
       |            Model Registry     Subscriptions
       |            Provider Registry  Credits
       |            Model Router       Usage Meter
       |            Fallback           Cost Engine
       |            Health             Spend Guard
       |                                Rate Limits
       +-----------------+---------------+
                         ↓
                  Unified AI Workspace
                         ↓
                    User Experience
```

The user sees a polished, simple ToolHub AI product.

Behind the scenes, ToolHub manages:

**tools + models + providers + routing + cost + subscriptions + credits + usage + reliability.**

This document is the foundation for the next phase: selecting and verifying the actual models/providers for each of the ten approved capability categories.
