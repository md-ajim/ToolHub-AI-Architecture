# ToolHub AI — Premium AI Workspace & Model UX Specification

## Updated UI/UX + Model Selector + Scalable AI Platform Architecture

> **Purpose:** Implementation specification for the ToolHub AI dashboard/workspace and scalable multi-provider AI model system.
>
> **Design direction:** `shadcn/ui` + clean Vercel-inspired minimalism + ToolHub's own brand identity.
>
> **Important:** Vercel-inspired does **not** mean copying Vercel. ToolHub AI must have its own visual identity, navigation, components, naming, and product experience.

---

## 1. Product Vision

ToolHub AI is a premium AI platform where users can access multiple AI capabilities and multiple AI providers from one unified workspace.

The product should feel:

- premium
- fast
- clean
- trustworthy
- minimal
- modern
- professional
- scalable
- easy for first-time users
- powerful for advanced users

The UI is one of the most important product differentiators. Users should immediately understand that ToolHub AI is a serious AI platform, not a collection of unrelated AI tools.

---

## 2. Non-Negotiable Design Rules

### 2.1 shadcn/ui is mandatory

Use **shadcn/ui** as the primary UI component foundation.

Use its patterns for:

- Button
- Input
- Textarea
- Dropdown Menu
- Select
- Command
- Dialog
- Sheet
- Popover
- Tooltip
- Badge
- Card
- Tabs
- Separator
- Scroll Area
- Avatar
- Progress
- Skeleton
- Alert
- Toast/Sonner
- Sidebar
- Navigation Menu

Do not introduce an unrelated component library that creates a second visual language.

### 2.2 Icons

Use **Lucide React** icons consistently.

Do not randomly mix:

- emoji icons
- unrelated icon libraries
- random SVG styles
- heavy decorative icons

Provider logos may use appropriate provider brand assets where legally and technically appropriate. UI action icons should remain Lucide-based.

### 2.3 Vercel-inspired, not Vercel copied

Use modern developer-platform principles:

- generous whitespace
- strong typography
- subtle borders
- restrained color
- compact controls
- excellent alignment
- minimal decoration

Do **not** copy Vercel branding, logo, exact layout, exact component styling, exact navigation, or wording.

ToolHub must remain visibly its own product.

---

## 3. Brand & Color System

The dashboard/workspace must use the same visual language as the ToolHub AI main product, mega-menu, and tools pages.

### 3.1 No unrelated backgrounds

Do not create a different background for the dashboard.

Do not introduce:

- random gray dashboard backgrounds
- blue page backgrounds
- purple page backgrounds
- gradient-heavy backgrounds
- glassmorphism backgrounds
- unrelated colored panels

Dashboard, workspace, tools, mega-menu, projects, history, and settings must feel like one product.

### 3.2 Recommended palette

Use a neutral/light interface:

- page background: white / very subtle neutral
- surface: white
- foreground: near-black
- muted foreground: neutral gray
- border: subtle neutral border
- primary accent: ToolHub blue/purple accent
- destructive: semantic red only when necessary
- success: restrained green
- warning: restrained amber

Accent colors communicate state; they should not decorate every component.

### 3.3 Dark mode

Dark mode must use the same design tokens rather than becoming a separate product.

---

## 4. Global Application Shell

```text
┌───────────────────────────────────────────────────────────────┐
│ ToolHub AI                         Search  Theme  Bell Avatar │
├───────────────┬───────────────────────────────────────────────┤
│ Workspace     │                                               │
│ navigation    │               Main Content                    │
│               │                                               │
│               │                                               │
└───────────────┴───────────────────────────────────────────────┘
```

### Header

- fixed/sticky where appropriate
- consistent height
- subtle bottom border
- ToolHub branding
- global search where appropriate
- theme control
- notifications
- user avatar
- no oversized header

The header must not compete with the main content.

### Sidebar

Recommended groups:

**WORKSPACE**
- Dashboard
- AI Workspace
- Models

**LIBRARY**
- Favorites
- Projects
- History
- Saved Files

**TOOLS / INSIGHTS**
- Tools
- Usage
- Billing

**ACCOUNT**
- Settings
- Help & Support

The exact labels may evolve, but hierarchy must remain clear.

---

## 5. Dashboard Hierarchy

Avoid making dashboard content visually larger or heavier than navigation.

Hierarchy:

1. Application shell
2. Navigation
3. Page title
4. Supporting description
5. Primary action
6. Content
7. Secondary information

Avoid:

- giant empty cards
- excessive borders
- oversized headings
- unnecessary illustrations
- too many competing colors

---

## 6. AI Workspace — Primary Product Experience

The AI Workspace is the most important user-facing screen.

Goal:

> One workspace. Many models. Many capabilities.

Recommended structure:

```text
Sidebar                    Main Workspace

New Chat                    Greeting
AI Workspace                Short supporting text
Models                      Chat Composer
Projects                    Quick Workflows
Templates                   Suggested prompts
Tools                       Tool actions
Recent
Settings
Help
```

The chat composer should be the visual center without becoming oversized.

---

## 7. Chat Composer

The composer should support future capabilities without requiring a redesign.

Controls:

- Attach file
- Web search
- Model selector
- Send
- optional tools/actions

Example:

```text
┌──────────────────────────────────────────────┐
│ Send a message to start a new chat...        │
│                                              │
│  Attach  Web  Tools             ToolHub Flash│
│                                      Send ↑  │
└──────────────────────────────────────────────┘
```

Use Lucide icons.

Support where available:

- text
- images
- documents
- audio
- model selection
- tools
- multimodal capabilities

---

# 8. Model Selector — Premium V2

The current model selector is a strong foundation.

**Do not replace it with a completely different design.**

Refine it into a scalable premium component.

## Core requirements

The model selector must support:

- Auto
- recently used models
- ToolHub models
- external provider models
- Free models
- Pro models
- Premium models
- locked models
- capability badges
- context length
- model search
- provider grouping
- selected state
- upgrade state
- future 50–100+ models

## Recommended layout

```text
┌──────────────────────────────────────┐
│ Model                                │
│ ┌──────────────────────────────────┐ │
│ │ Search models...              ⌘ F │ │
│ └──────────────────────────────────┘ │
│                                      │
│ RECOMMENDED                          │
│ ┌──────────────────────────────────┐ │
│ │ Auto              Recommended  ✓ │ │
│ │ ToolHub picks the best model    │ │
│ └──────────────────────────────────┘ │
│                                      │
│ RECENTLY USED                        │
│ ToolHub Flash       Free          ✓  │
│ Chat · Files · 16K context          │
│                                      │
│ TOOLHUB MODELS                       │
│ ToolHub Light       Free             │
│ Chat · Files · 8K context           │
│ ToolHub Flash       Free          ✓  │
│ Chat · Files · 16K context          │
│ ToolHub Pro         Pro          🔒  │
│ Chat · Files · 128K context         │
│                                      │
│ PROVIDER MODELS                      │
│ OpenAI                               │
│   GPT ...             Pro         🔒  │
│ Google                               │
│   Gemini ...          Pro         🔒  │
│ Anthropic                            │
│   Claude ...          Premium     🔒 │
│ Qwen                                │
│   Qwen ...             Free         │
│ DeepSeek                             │
│   DeepSeek ...         Free/Pro     │
│                                      │
│ View all models →                   │
└──────────────────────────────────────┘
```

---

## 9. Model Selector Visual Rules

Keep the selector:

- white
- compact
- subtle
- high contrast
- readable
- keyboard accessible
- scrollable

Avoid:

- rainbow provider colors
- huge model cards
- excessive shadows
- giant gradients
- emoji-heavy UI
- oversized logos
- unnecessary animation

Use a small accent highlight for:

- selected model
- Recommended
- active filter

---

## 10. Model Search & Filters

When the model list grows, search is mandatory.

Search should match:

- model name
- provider
- capability
- tier
- aliases

Examples:

- `vision` → vision-capable models
- `coding` → coding-oriented models
- `free` → free models

Use shadcn/ui Command patterns.

Recommended keyboard shortcut:

`⌘/Ctrl + F`

Optional compact filters:

`All | Free | Pro | Premium`

---

## 11. Model Metadata

Every model should use normalized structured metadata.

Example:

```ts
type ModelDefinition = {
  id: string
  displayName: string
  provider: string
  brand: "toolhub" | "provider"
  tier: "free" | "pro" | "premium"
  capabilities: (
    | "chat"
    | "reasoning"
    | "coding"
    | "vision"
    | "image_generation"
    | "image_editing"
    | "speech_to_text"
    | "text_to_speech"
    | "embeddings"
    | "video"
  )[]
  contextWindow?: number
  available: boolean
  requiresSubscription: boolean
  supportsFiles?: boolean
  supportsStreaming?: boolean
  description?: string
  providerModelId: string
}
```

The frontend must not hard-code provider API logic.

---

## 12. Provider Architecture

The platform must be designed for many providers.

Initial examples:

- OpenAI
- Google
- Anthropic
- Qwen
- DeepSeek
- Hugging Face ecosystem
- future providers
- ToolHub-branded models

Architecture:

```text
ProviderRegistry
      │
      ├── OpenAIAdapter
      ├── GoogleAdapter
      ├── AnthropicAdapter
      ├── QwenAdapter
      ├── DeepSeekAdapter
      ├── HuggingFaceAdapter
      └── FutureProviderAdapter
```

Each adapter normalizes provider-specific APIs into ToolHub's internal interface.

---

## 13. Internal AI Gateway

The frontend must **never** call provider APIs directly.

```text
Browser
   ↓
ToolHub API
   ↓
AI Gateway
   ↓
Provider Adapter
   ↓
Provider API
```

This protects:

- API keys
- billing rules
- model access
- subscription checks
- usage accounting
- rate limits
- provider failover
- logging
- abuse prevention

---

## 14. Secret Management

Provider API keys live server-side only.

Example:

```env
OPENAI_API_KEY=
GOOGLE_AI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
QWEN_API_KEY=
HUGGINGFACE_API_KEY=
```

Never expose secrets in:

- frontend JavaScript
- localStorage
- public configuration
- HTML
- client-side source
- API responses

The implementation should be designed so the platform owner only needs to configure provider secrets securely.

---

## 15. Subscription & Cost Protection

This is a critical business requirement.

ToolHub must never accidentally consume paid provider credits for users who are not entitled to use them.

Every inference request:

```text
Authentication
    ↓
Subscription check
    ↓
Model entitlement check
    ↓
Usage / credit check
    ↓
Rate limit check
    ↓
Provider request
    ↓
Usage recording
```

### Free users

Free users can access only explicitly configured free models/capabilities.

Paid provider models must not silently consume the platform owner's paid API account for unauthorized users.

### Paid users

Paid users can access models according to their plan.

Plans can control:

- allowed models
- monthly credits
- rate limits
- context limits
- file limits
- generation limits
- priority
- advanced capabilities

---

## 16. Credit-Based Billing

Recommended:

```text
Subscription
     ↓
Plan
     ↓
Monthly credits
     ↓
Model cost multiplier
     ↓
Usage deduction
```

Model cost must be configurable from the backend/database.

Example:

```ts
{
  modelId: "provider-model-x",
  inputCreditRate: 1,
  outputCreditRate: 3
}
```

Never hard-code commercial pricing in the frontend.

---

## 17. Auto Model

Auto is a major UX feature.

It should select an appropriate available model based on:

- user plan
- task type
- requested capability
- model availability
- usage
- configured cost
- latency
- context requirements

```text
User request
     ↓
Task classification
     ↓
Available models
     ↓
Entitlement filter
     ↓
Capability filter
     ↓
Cost / latency optimization
     ↓
Best model
```

UI copy:

> ToolHub AI picks the best model for your task.

Advanced users can manually select a model.

---

## 18. Initial AI Capability Categories

Design for these ten capability groups:

1. General Chat / LLM
2. Reasoning
3. Coding
4. Vision
5. Image Generation
6. Image Editing
7. Speech-to-Text
8. Text-to-Speech
9. Embeddings
10. Video

Provider/model availability must be detected from actual configured capabilities.

---

## 19. ToolHub Branding Strategy

Major provider models should retain their recognizable provider/model identity where appropriate:

- OpenAI → OpenAI models
- Google → Gemini models
- Anthropic → Claude models
- DeepSeek → DeepSeek models
- Qwen → Qwen models

Open-source/community models exposed through ToolHub infrastructure may be presented as ToolHub-branded offerings **only when licensing, provider terms, and attribution requirements permit it**.

Do not falsely claim a third-party model was created by ToolHub.

Provider attribution must remain accurate.

---

## 20. Hugging Face Integration

Hugging Face is an ecosystem/source integration, not the visual identity of the ToolHub product.

The user-facing experience remains ToolHub-branded.

Backend metadata should preserve:

- source/provider
- original model ID
- license
- capabilities
- inference method
- availability
- cost
- attribution requirements

Do not rename models in ways that violate licensing or attribution requirements.

---

## 21. Model Registry

Create a centralized model registry containing:

```text
model identity
provider
source
provider model ID
ToolHub display name
capabilities
tier
subscription requirements
context window
pricing / credit configuration
availability
license metadata
routing configuration
```

The UI reads this registry.

New models should be addable without rewriting the frontend architecture.

---

## 22. Admin Model Management

Authorized administrators should be able to:

- enable/disable model
- add provider
- configure model ID
- configure display name
- configure tier
- configure capabilities
- configure context size
- configure credit cost
- configure subscription requirements
- configure availability
- set model priority
- set Auto routing priority

This is essential for long-term scalability.

---

## 23. Provider Failure Handling

```text
Provider request
      ↓
Failure
      ↓
Retry policy
      ↓
Alternative configured model/provider
      ↓
User-friendly result
```

Do not expose raw provider errors.

Bad:

> HTTP 429 Provider APIError...

Good:

> This model is temporarily busy. Try again or select another available model.

---

## 24. Streaming

Chat models should support streaming where available.

States:

- preparing
- generating
- streaming
- completed
- failed
- cancelled

Users must be able to stop generation.

---

## 25. Conversation Persistence

Store:

- conversation
- messages
- selected model
- provider
- usage
- timestamps
- attachments
- tool calls
- generation metadata

Users should be able to continue conversations with another model where technically appropriate.

---

## 26. Recent Models

Recommended model selector order:

1. Auto
2. Recently Used
3. ToolHub Models
4. Provider Models
5. View All Models

Recently used models are personalized per user.

---

## 27. Quick Workflows

Provide compact actions such as:

- Email drafting
- Translation
- Summarization
- Code review
- Brainstorming
- Research
- Document analysis

Use subtle pills/buttons.

They should not overpower the composer.

---

## 28. Suggested Prompts

Use clean cards where appropriate:

- Explain quantum computing in simple terms
- Write a Python function
- Brainstorm blog titles
- Create a content plan
- Compare AI models for coding

Cards should use subtle borders and minimal icons.

---

## 29. User Profile Menu

The profile dropdown belongs to the header.

It must not become part of the dashboard content.

```text
Avatar
  ↓
┌─────────────────────────┐
│ User name               │
│ email                   │
│                         │
│ Free / Pro / Premium    │
│                         │
│ Settings                │
│ Billing                 │
│ Help                    │
│ Log out                 │
└─────────────────────────┘
```

It should remain visually separated from the dashboard.

---

## 30. Responsive Design

### Desktop

- sidebar visible
- model selector wide enough for metadata
- centered workspace content

### Tablet

- collapsible sidebar
- responsive content width

### Mobile

- sidebar becomes Sheet/Drawer
- model selector becomes responsive Popover/Sheet
- composer remains usable
- no horizontal overflow

---

## 31. Accessibility

Support:

- keyboard navigation
- focus states
- screen readers
- semantic HTML
- sufficient contrast
- visible selected state
- `aria-label`
- `aria-expanded`
- `aria-selected`
- escape-to-close dialogs/popovers
- reduced motion

---

## 32. Motion

Use subtle motion only.

Good:

- dropdown fade/scale
- sidebar transitions
- button feedback
- loading indicators

Avoid:

- constant floating animations
- excessive gradients
- distracting motion
- long transitions

Recommended duration:

`100–200ms`

---

## 33. Frontend Component Architecture

```text
components/
├── ui/
│   └── shadcn components
│
├── layout/
│   ├── AppShell
│   ├── Header
│   ├── Sidebar
│   └── UserMenu
│
├── ai/
│   ├── ChatComposer
│   ├── ModelSelector
│   ├── ModelSearch
│   ├── ModelItem
│   ├── ModelGroup
│   ├── CapabilityBadge
│   ├── QuickWorkflow
│   └── SuggestedPrompt
│
└── models/
    ├── ModelRegistry
    ├── ProviderBadge
    └── ModelDetails
```

---

## 34. Backend Architecture

```text
API
 ↓
Auth
 ↓
Entitlements
 ↓
Usage
 ↓
AI Gateway
 ↓
Provider Registry
 ↓
Provider Adapter
 ↓
External AI Provider
```

The provider layer must be replaceable.

---

## 35. Database Concepts

Recommended entities:

```text
User
Subscription
Plan
CreditBalance
UsageRecord
Provider
Model
ModelCapability
Conversation
Message
Attachment
Project
SavedFile
Favorite
ProviderCredential
ModelEntitlement
```

Adapt to the existing ORM/database architecture.

---

## 36. Security Requirements

Mandatory:

- server-side provider credentials
- authenticated AI requests
- authorization checks
- rate limiting
- input validation
- output handling
- file validation
- upload size limits
- abuse prevention
- audit logging
- usage tracking
- secure secret storage

Never trust client-provided model tier or permissions.

The backend determines model access.

---

## 37. API Design

Recommended endpoints:

```text
GET    /api/models
GET    /api/models/:id
GET    /api/providers
POST   /api/chat
POST   /api/chat/stream
POST   /api/files
GET    /api/conversations
GET    /api/conversations/:id
POST   /api/conversations
DELETE /api/conversations/:id
GET    /api/usage
GET    /api/subscription
```

Adapt routes to the existing project conventions.

---

## 38. Frontend API Rule

Frontend requests normalized model data:

```text
GET /api/models
```

Example:

```json
{
  "id": "toolhub-flash",
  "displayName": "ToolHub Flash",
  "provider": "ToolHub",
  "tier": "free",
  "capabilities": ["chat", "files"],
  "contextWindow": 16000,
  "available": true
}
```

The frontend must not know provider API keys or provider-specific authentication details.

---

## 39. Error & Empty States

Every major screen needs intentional empty states.

Examples:

**No conversations**

> No conversations yet.  
> Start a new chat to begin.

**No projects**

> No projects yet.  
> Create a project to organize your work.

**No models**

> No models are currently available.  
> Check your plan or try again later.

Never leave unexplained blank space.

---

## 40. Loading States

Use shadcn Skeleton patterns.

Model selector loading:

```text
Search models...

▰▰▰
▰▰▰
▰▰▰
```

Chat generation should use a subtle streaming indicator.

---

## 41. Performance

The model system must remain fast with many models.

Use where appropriate:

- lazy loading
- virtualization for very large lists
- memoized model groups
- server-side filtering
- cached model registry
- streaming responses
- safe optimistic UI

---

## 42. Never Hard-Code the Production Model List

Do not make a permanent production architecture like:

```tsx
const models = [...]
```

A seed configuration is acceptable for initial development.

Production model data must come from the model registry/database.

---

## 43. Business Cost Protection

Before every paid inference:

```text
Is user authenticated?
        ↓
Does plan allow model?
        ↓
Does user have sufficient credits?
        ↓
Is model available?
        ↓
Is provider available?
        ↓
Make request
        ↓
Record actual usage
        ↓
Deduct credits
```

If a required condition fails, do not call the paid provider.

This protects the platform owner from uncontrolled provider costs.

---

## 44. Premium Upgrade UX

Locked model:

```text
ToolHub Pro
Pro 🔒

Advanced model for complex tasks

Requires Pro plan

[ Upgrade ]
```

Users should clearly understand why access is unavailable and what upgrading provides.

---

## 45. Model Comparison

Future-ready feature:

```text
Compare models
──────────────────────────
Model       Speed   Quality  Context
ToolHub     Fast    Good     16K
Provider A  Fast    Excellent 128K
Provider B  Medium  Excellent 200K
```

Use the same ToolHub design system.

---

## 46. AI Workspace UX Principle

Users should not need to understand provider infrastructure.

Simple path:

> Choose what you want to accomplish.  
> ToolHub helps choose how to accomplish it.

Advanced users can manually choose models.

Beginners can use Auto.

---

## 47. Final Model Selector Experience

The compact trigger remains:

```text
ToolHub Flash ▼
```

Opening it:

```text
Model
[ Search models... ]

RECOMMENDED
Auto                         ✓

RECENTLY USED
ToolHub Flash                ✓

TOOLHUB MODELS
ToolHub Light       Free
ToolHub Flash       Free
ToolHub Pro         Pro 🔒

PROVIDER MODELS
OpenAI
  GPT ...           Pro 🔒

Google
  Gemini ...        Pro 🔒

Anthropic
  Claude ...        Premium 🔒

DeepSeek
  DeepSeek ...      Free/Pro

Qwen
  Qwen ...          Free

View all models →
```

The current successful selector remains the foundation; the improvement is in search, grouping, metadata, recent models, scalability, and polished interaction.

---

## 48. Acceptance Criteria

- [ ] shadcn/ui is the primary UI foundation
- [ ] Lucide is used for UI icons
- [ ] dashboard/workspace/tools share the same visual language
- [ ] no unrelated dashboard background exists
- [ ] navigation and content hierarchy are balanced
- [ ] profile menu stays in the header
- [ ] model selector remains compact and premium
- [ ] model selector supports search
- [ ] provider grouping works
- [ ] recent models work
- [ ] Free/Pro/Premium states work
- [ ] locked models show upgrade state
- [ ] capability badges work
- [ ] 50–100+ models are supported architecturally
- [ ] provider APIs are accessed server-side
- [ ] secrets never reach the browser
- [ ] subscription entitlement is checked server-side
- [ ] unauthorized paid provider calls are blocked
- [ ] usage is recorded
- [ ] credits can be deducted
- [ ] provider adapters are replaceable
- [ ] new providers can be added without rewriting the UI
- [ ] model data comes from a registry
- [ ] Auto routing is supported
- [ ] streaming is supported where available
- [ ] mobile layout works
- [ ] keyboard navigation works
- [ ] empty/loading/error states are implemented
- [ ] provider attribution remains accurate
- [ ] licensing/attribution requirements are preserved

---

## 49. AI Coding Agent Instructions

When implementing this specification:

1. Inspect the existing application architecture first.
2. Do not rewrite working functionality unnecessarily.
3. Reuse existing components that already follow the design system.
4. Identify existing shadcn/ui components before creating duplicates.
5. Follow the existing icon convention.
6. Keep ToolHub's existing brand language.
7. Do not introduce unrelated colors.
8. Do not create a separate dashboard visual language.
9. Do not hard-code provider API calls in frontend components.
10. Build Model Selector as a reusable component.
11. Build provider integration behind adapters.
12. Keep model metadata normalized.
13. Implement subscription checks on the backend.
14. Never trust client-side permissions.
15. Never expose API secrets.
16. Add tests for entitlement and routing rules.
17. Test free users against paid models.
18. Test paid users against permitted models.
19. Test provider failures.
20. Test model search/filtering.
21. Test responsive layouts.
22. Test keyboard accessibility.
23. Test multiple providers.
24. Keep architecture ready for future providers/models.
25. Do not stop at a visual mockup; implement the complete working flow supported by the existing project.

---

# 50. Final Design Direction

ToolHub AI should feel like a product users trust.

The goal is not:

> “A website containing many AI APIs.”

The goal is:

> **“One premium AI workspace where many models and AI capabilities become one simple experience.”**

Visual formula:

```text
ToolHub Brand
+
shadcn/ui
+
Vercel-inspired minimalism
+
Excellent typography
+
Subtle borders
+
Consistent spacing
+
Lucide icons
+
Scalable model architecture
+
Secure AI gateway
+
Subscription-aware routing
=
ToolHub AI Premium Experience
```

**Do not sacrifice consistency for novelty.**

The current Model Selector is the foundation. Improve it, make it scalable, make it intelligent, and integrate it into one unified ToolHub AI experience.
