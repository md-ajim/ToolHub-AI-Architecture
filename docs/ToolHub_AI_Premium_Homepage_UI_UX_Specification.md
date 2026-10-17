# ToolHub AI --- Premium Homepage UI/UX Design Specification

**Document Type:** Product UI/UX implementation specification\
**Scope:** ToolHub AI public homepage (`/`)\
**Design Direction:** Premium AI-first platform, Vercel-inspired but not
a Vercel copy\
**Primary UI System:** shadcn/ui\
**Icon System:** lucide-react\
**Brand:** ToolHub AI\
**Status:** Implementation-ready specification

------------------------------------------------------------------------

## 1. Purpose

The ToolHub AI homepage must communicate one clear product idea within
the first few seconds:

> **ToolHub AI is an AI workspace where users can chat, reason, code,
> create, analyze, and use practical tools --- with multiple AI
> providers and models available from one place.**

The homepage must no longer feel like a generic utility-directory
website.

The existing clean ToolHub visual language remains the foundation, but
the information hierarchy becomes **AI-first**.

The homepage should feel:

-   premium
-   modern
-   trustworthy
-   technically capable
-   calm
-   fast
-   useful
-   easy to understand
-   scalable for a large AI ecosystem

Do not turn the homepage into a flashy, generic "AI startup" landing
page.

------------------------------------------------------------------------

# 2. Core Product Positioning

## Primary positioning

> **One AI workspace. Everything you need to create.**

## Supporting message

> Chat, code, create images, analyze documents, automate workflows, and
> get more done with powerful AI models and tools --- all in one place.

## Secondary positioning

> **Multiple models. Powerful tools. One place.**

The homepage must establish that ToolHub AI is more than a chatbot and
more than a collection of small browser utilities.

------------------------------------------------------------------------

# 3. Non-Negotiable Design Principles

## 3.1 ToolHub AI owns its visual identity

Use:

> **Vercel-inspired ≠ Vercel copied**

The visual direction may take inspiration from clean typography, precise
spacing, restrained visual hierarchy, neutral surfaces, strong product
focus, and premium simplicity.

Do NOT copy another company's:

-   exact layout
-   branding
-   logos
-   proprietary visual identity
-   exact component styling
-   exact marketing language

## 3.2 Use shadcn/ui everywhere

Use the existing shadcn/ui design system wherever an appropriate
component exists.

Use it for:

-   Button
-   Card
-   Badge
-   Input
-   Navigation Menu
-   Dropdown Menu
-   Sheet
-   Dialog
-   Tabs
-   Accordion
-   Tooltip
-   Separator
-   Skeleton
-   Avatar
-   Command/search interfaces

Do not introduce a second UI component framework.

## 3.3 Use lucide-react icons

Use `lucide-react` for interface icons.

Do not add another icon package.

Icons must have consistent stroke weight, communicate meaning, remain
accessible, and not replace necessary text.

------------------------------------------------------------------------

# 4. Existing ToolHub Visual Language

The current `/tools` page establishes the baseline visual language and
must remain compatible with the homepage.

Preserve:

-   white/neutral background
-   black/dark primary typography
-   gray secondary typography
-   subtle gray borders
-   restrained shadows
-   rounded cards
-   generous whitespace
-   clean top navigation
-   simple black primary CTA
-   minimal visual noise

The homepage may introduce stronger AI product visuals, but it must
still look like the same ToolHub product.

### Critical rule

There must NOT be an unrelated background or a completely different
visual theme on the homepage.

The `/`, `/tools`, AI Workspace, dashboard, model pages, and other
product surfaces must feel like one product family.

------------------------------------------------------------------------

# 5. Homepage Information Architecture

Recommended order:

1.  Global Header
2.  AI-first Hero
3.  AI Workspace Product Preview
4.  AI Capabilities
5.  Multi-Model Ecosystem
6.  AI Coding / Agent
7.  AI + Tools Ecosystem
8.  Projects / Files / Workflows
9.  Pricing
10. Trust / Privacy / Security
11. Final CTA
12. Footer

The order may be adjusted for performance or experimentation, but the
AI-first hierarchy must remain.

------------------------------------------------------------------------

# 6. Global Header

Keep the header visually consistent with the existing ToolHub
navigation.

Recommended:

``` text
ToolHub AI     Tools ▾    Pricing    Blog

                         Search tools...   Theme   Account
```

Requirements:

-   stable/sticky behavior consistent with the existing application
-   thin bottom border
-   neutral background
-   no oversized navigation
-   compact search control
-   compact account control
-   accessible keyboard navigation

Do not overcrowd the public header.

------------------------------------------------------------------------

# 7. Hero Section

The hero is the most important section.

## Recommended headline

> **One AI workspace.\
> Everything you need to create.**

## Supporting text

> Chat, code, create images, analyze documents, automate workflows, and
> get more done with powerful AI models and tools --- all in one place.

## Primary CTA

> **Start creating**

Route to the real AI Workspace or authenticated entry flow.

## Secondary CTA

> **Explore AI**

Route to the relevant AI/model/capability experience.

------------------------------------------------------------------------

# 8. Hero Visual Direction

Do not rely on a decorative illustration as the main visual.

Show the actual product experience.

Recommended hero visual:

> **A large AI Workspace preview**

Example:

``` text
┌──────────────────────────────────────────────────────────┐
│ ToolHub AI                                         M     │
├──────────────┬───────────────────────────────────────────┤
│              │                                           │
│ New Chat     │       What can I help you create?         │
│ Models       │                                           │
│ Projects     │                                           │
│              │   ┌───────────────────────────────────┐   │
│ Recent       │   │ Ask anything...                   │   │
│              │   │                                   │   │
│              │   └───────────────────────────────────┘   │
│              │                                           │
│              │ Auto  OpenAI  Gemini  Claude  Qwen       │
└──────────────┴───────────────────────────────────────────┘
```

The preview should be based on the actual product UI rather than a fake
marketing illustration.

------------------------------------------------------------------------

# 9. AI Workspace Preview Requirements

The preview should communicate:

-   conversational AI
-   model selection
-   multiple providers
-   projects
-   recent conversations
-   file support
-   modern composer
-   ToolHub AI branding

Keep it visually lightweight.

The goal is:

> "I understand what this product does."

not:

> "I am looking at a screenshot full of controls."

------------------------------------------------------------------------

# 10. AI Capabilities Section

## Heading

> **Everything you need to work with AI**

## Supporting text

> One workspace for conversation, reasoning, coding, vision, creation,
> speech, search, and more.

Display the ten capability categories:

1.  General Chat / LLM
2.  Reasoning
3.  Coding
4.  Vision
5.  Image Generation
6.  Image Editing
7.  Speech-to-Text
8.  Text-to-Speech
9.  Embeddings
10. Video

Use a clean responsive capability grid.

Avoid ten oversized cards.

Each capability may contain:

-   lucide-react icon
-   title
-   one-line description
-   subtle hover state
-   optional "Explore" affordance

------------------------------------------------------------------------

# 11. Multi-Model Ecosystem Section

This is one of ToolHub AI's strongest differentiators.

## Heading

> **Choose the intelligence behind your work**

## Supporting text

> Work with models from multiple providers through one consistent AI
> workspace.

Provider families may include:

-   OpenAI
-   Google / Gemini
-   Anthropic / Claude
-   DeepSeek
-   Qwen
-   Mistral
-   xAI
-   Meta
-   ToolHub AI models

Only show providers/models actually available in the current deployment.

Never create fake availability.

------------------------------------------------------------------------

# 12. Provider Branding Rules

Official proprietary models should retain their actual provider/model
identity.

Examples:

-   OpenAI → OpenAI model name
-   Google → Gemini model name
-   Anthropic → Claude model name
-   DeepSeek → DeepSeek model name
-   Qwen → Qwen model name

For selected open-source/community models offered through ToolHub, a
ToolHub-facing product name may be used where appropriate.

However:

> Never falsely claim that an open-source model was created by ToolHub
> AI.

Technical attribution may remain visible in model details/admin
interfaces when necessary.

------------------------------------------------------------------------

# 13. Model Discovery UI

The homepage does not need to expose the complete model catalog.

Use a curated preview:

``` text
Popular models

OpenAI      ...
Gemini      ...
Claude      ...
DeepSeek    ...
Qwen        ...
ToolHub     ...
```

CTA:

> **Explore all models**

The complete model catalog belongs in the AI Workspace / Models
experience.

------------------------------------------------------------------------

# 14. AI Coding / Agent Section

## Heading

> **Build more than conversations.**

## Supporting copy

> Turn ideas into working projects with AI-powered coding and agent
> workflows.

CTA:

> **Try AI Coding**

Use a realistic code workspace preview containing elements such as:

-   file tree
-   editor
-   AI assistant
-   task/status area
-   generated changes

Do not make this a fake developer screenshot.

Use the same ToolHub visual system.

------------------------------------------------------------------------

# 15. AI + Tools Ecosystem

The existing tools business must remain part of the product.

Reframe it.

## Heading

> **AI for thinking. Tools for doing.**

Two major categories:

### AI Workspace

-   Chat
-   Reasoning
-   Coding
-   Vision
-   Image creation
-   Speech
-   Video

### Tools

-   Image tools
-   PDF tools
-   Text tools
-   Developer tools
-   File tools
-   Utility tools

This communicates that ToolHub AI combines AI capabilities with
practical utilities.

------------------------------------------------------------------------

# 16. Existing Tools Integration

Existing tools continue using the clean utility-card style.

Examples:

-   Image Resizer
-   Image Compressor
-   Password Generator
-   Meta Tag Generator
-   PDF utilities
-   Developer utilities

Do not place dozens of tool cards above the AI hero.

The homepage should feature only a curated subset.

CTA:

> **Explore all tools**

------------------------------------------------------------------------

# 17. Projects / Files / Workflows Section

## Heading

> **Your work, organized.**

## Supporting text

> Keep AI conversations, files, projects, saved outputs, and workflows
> together instead of scattering them across different apps.

Feature:

-   Projects
-   Files
-   Conversations
-   Saved outputs
-   Workflows
-   History

Use a clean product UI preview rather than decorative illustrations.

------------------------------------------------------------------------

# 18. Pricing Section

## Heading

> **Start free. Upgrade when you need more.**

The pricing UI must connect directly to the real entitlement system.

Recommended tiers:

### Free

-   selected free models
-   limited usage
-   basic tools
-   basic workspace

### Pro

-   more models
-   higher limits
-   advanced AI capabilities
-   coding/vision access where configured

### Max / Premium

-   highest configured limits
-   premium model access
-   advanced capabilities
-   priority access where actually supported

Never promise capabilities that are not implemented.

------------------------------------------------------------------------

# 19. Credit and Cost Messaging

The public homepage may explain that AI usage is plan-controlled.

Avoid exposing complicated provider cost formulas.

Recommended language:

> Plans include usage allowances designed for different levels of AI
> work.

Backend entitlement and limits must be authoritative.

Never allow the client to decide entitlement.

------------------------------------------------------------------------

# 20. Trust Section

## Heading

> **Your work stays yours.**

Use only claims supported by the actual implementation.

Possible items:

-   Secure authentication
-   Server-side provider credentials
-   Protected files
-   Usage controls
-   Clear account controls
-   Privacy controls

Do not make unsupported security claims.

------------------------------------------------------------------------

# 21. Final CTA

Recommended:

> **Everything you need to work smarter.**

Supporting text:

> Start with free AI tools and grow into a complete AI workspace when
> you need more.

Primary CTA:

> **Start creating**

Secondary CTA:

> **Explore tools**

Keep the final CTA visually strong but restrained.

------------------------------------------------------------------------

# 22. Footer

Keep the footer minimal.

Recommended groups:

### Product

-   AI Workspace
-   Models
-   Tools
-   Pricing

### Resources

-   Blog
-   Documentation
-   Help

### Company

-   About
-   Contact
-   Privacy
-   Terms

Do not create a massive footer.

------------------------------------------------------------------------

# 23. Color System

Use the existing ToolHub neutral design tokens.

Primary:

-   white / neutral background
-   near-black primary text
-   neutral gray secondary text
-   subtle gray borders

Accent:

-   existing ToolHub brand accent only

Avoid:

-   rainbow gradients
-   neon backgrounds
-   excessive purple/blue AI gradients
-   large colored blobs
-   unrelated dark sections

Small accents may be used for:

-   selected states
-   AI badges
-   focus states
-   important interactive elements

------------------------------------------------------------------------

# 24. Background Rules

Do not create separate unrelated backgrounds for sections.

Use a consistent neutral page canvas.

Sections may be differentiated with:

-   spacing
-   borders
-   subtle surface elevation
-   very light neutral surfaces

Do not use large decorative background effects.

------------------------------------------------------------------------

# 25. Typography

Use the project's existing typography system.

Hierarchy:

-   Hero: very large, bold
-   Section title: large, strong
-   Card title: medium/bold
-   Body: readable neutral gray
-   Metadata: small muted text

Do not use decorative display fonts or excessive font weights.

Typography should communicate technical precision.

------------------------------------------------------------------------

# 26. Spacing

Use consistent spacing tokens.

Recommended rhythm:

-   large section spacing
-   generous hero whitespace
-   compact card internal spacing
-   consistent horizontal container width

Avoid cramped layouts, giant empty spaces without product purpose,
inconsistent card heights, and arbitrary margins.

------------------------------------------------------------------------

# 27. Container Width

Use one consistent max-width container for the homepage.

Follow existing ToolHub design tokens.

The goal is a centered, premium content column.

Do not allow hero content to become excessively wide.

------------------------------------------------------------------------

# 28. Cards

Cards should be:

-   clean
-   subtle
-   bordered
-   lightly rounded
-   low-shadow
-   content-focused

Avoid:

-   heavy glassmorphism
-   excessive shadow
-   giant border radius
-   excessive gradients
-   glowing cards

Hover states should be subtle.

------------------------------------------------------------------------

# 29. Buttons

Primary button:

-   dark/black ToolHub button
-   strong readable text
-   compact height
-   subtle hover state

Secondary button:

-   neutral outlined button

Do not create many competing CTA styles.

Normally use one primary action per section.

------------------------------------------------------------------------

# 30. Responsive Design

The homepage must work at:

-   large desktop
-   desktop
-   laptop
-   tablet
-   mobile

On mobile:

-   navigation collapses appropriately
-   hero headline remains readable
-   product preview remains horizontally safe
-   grids collapse
-   cards remain usable
-   buttons may become full-width where appropriate
-   no horizontal page overflow
-   no clipped dropdowns
-   no overlapping content

------------------------------------------------------------------------

# 31. Accessibility

Requirements:

-   semantic HTML
-   keyboard navigation
-   visible focus states
-   appropriate ARIA labels
-   accessible buttons
-   accessible navigation
-   sufficient contrast
-   reduced-motion support
-   screen-reader-friendly interactive elements

Do not depend on hover alone to communicate important information.

------------------------------------------------------------------------

# 32. Motion

Motion should be minimal.

Allowed:

-   subtle fade
-   small translate
-   button hover
-   card hover
-   menu transitions

Avoid:

-   constant animation
-   distracting auto-playing effects
-   parallax-heavy sections
-   excessive scroll animation

Respect `prefers-reduced-motion`.

------------------------------------------------------------------------

# 33. Performance

The homepage is a public acquisition page.

Prioritize:

-   fast first render
-   optimized images
-   minimal JavaScript
-   lazy loading below-the-fold media
-   no unnecessary client components
-   no heavy animation library
-   no huge hero video unless justified

The hero should remain useful even before below-the-fold content loads.

------------------------------------------------------------------------

# 34. SEO / Metadata

Recommended title:

> ToolHub AI --- One AI Workspace for Work, Creation, and Tools

Recommended description:

> Chat, code, create, analyze, and use powerful AI models and practical
> tools in one workspace.

Use appropriate:

-   Open Graph metadata
-   social metadata where applicable
-   canonical URL
-   semantic heading hierarchy

Do not keyword-stuff.

------------------------------------------------------------------------

# 35. Product Analytics

Track meaningful product interactions where analytics infrastructure
exists.

Potential events:

-   homepage CTA click
-   AI Workspace click
-   model catalog click
-   tools catalog click
-   pricing click
-   capability click
-   coding/agent click
-   signup completion

Do not collect unnecessary personal information.

------------------------------------------------------------------------

# 36. Component Architecture

Prefer reusable components such as:

``` text
components/
  marketing/
    HeroSection
    WorkspacePreview
    CapabilityGrid
    ModelEcosystem
    CodingAgentSection
    ToolsEcosystem
    ProjectsSection
    PricingSection
    TrustSection
    FinalCTA
    MarketingFooter
```

Reuse existing:

-   Button
-   Card
-   Badge
-   Navigation
-   Container
-   Typography
-   model components

Do not duplicate design primitives.

------------------------------------------------------------------------

# 37. Data Architecture

Homepage content should be data-driven where practical.

For capabilities and model providers, avoid scattering hard-coded
content throughout JSX.

Conceptually:

``` ts
capabilities = [
  {
    id: "chat",
    title: "General Chat",
    description: "...",
    icon: MessageSquare
  }
]
```

Provider/model previews should use the existing model registry where
practical.

Do not expose unavailable models.

------------------------------------------------------------------------

# 38. Relationship With AI Workspace

The homepage and AI Workspace must feel like two layers of the same
product.

Homepage:

> Discover ToolHub AI.

AI Workspace:

> Use ToolHub AI.

The transition should feel seamless.

The homepage's workspace preview should visually match the actual AI
Workspace.

------------------------------------------------------------------------

# 39. Relationship With `/tools`

The homepage must preserve the visual language established by `/tools`.

The tools page remains:

> practical utility discovery

The homepage becomes:

> AI platform discovery + ToolHub ecosystem

Do not redesign `/tools` unnecessarily while implementing this homepage
specification.

------------------------------------------------------------------------

# 40. Do Not Do These Things

Never:

-   turn the homepage into a generic SaaS template
-   copy Vercel
-   copy ChatGPT
-   copy Claude
-   copy Gemini
-   introduce random gradients
-   introduce a second icon library
-   introduce a second component library
-   create unrelated backgrounds
-   place huge tool catalogs above the AI hero
-   use fake model availability
-   claim fake proprietary models
-   claim unsupported security features
-   expose provider API keys
-   hard-code secrets
-   create mock model behavior in production
-   add unnecessary animations
-   destroy existing ToolHub navigation
-   break `/tools`
-   create inconsistent dashboard/homepage styling

------------------------------------------------------------------------

# 41. Implementation Strategy

The coding agent should:

1.  Inspect the current homepage.
2.  Inspect the existing `/tools` design.
3.  Inspect the existing AI Workspace.
4.  Inspect existing design tokens.
5.  Reuse existing components.
6.  Implement the homepage incrementally.
7.  Avoid unrelated refactoring.
8.  Verify responsive behavior.
9.  Run lint/build/tests.
10. Fix regressions.

Do not replace the entire frontend blindly.

------------------------------------------------------------------------

# 42. Acceptance Criteria

## Brand

-   ToolHub AI is immediately recognizable.
-   The homepage feels like a first-party product.
-   The visual language is consistent with `/tools`.

## UX

-   A new visitor understands ToolHub AI within seconds.
-   AI Workspace is clearly the primary product.
-   Tools remain discoverable.
-   Multiple AI providers/models are clearly communicated.

## UI

-   shadcn/ui is used.
-   lucide-react is used.
-   no random icon libraries.
-   no unrelated backgrounds.
-   no excessive gradients.
-   spacing is consistent.
-   typography is premium and readable.

## Product

-   Hero links to the real AI Workspace.
-   Model ecosystem reflects real available providers.
-   Tools links point to real tools.
-   Pricing reflects real plan capabilities.

## Technical

-   no secrets in client code
-   no fake availability
-   no broken routes
-   no horizontal overflow
-   no console errors introduced
-   clean production build
-   existing functionality remains intact

------------------------------------------------------------------------

# 43. Final Design Goal

The finished homepage should communicate:

> **ToolHub AI is not just another AI chatbot.**

> **It is a complete AI workspace and practical tools platform where
> users can choose the right intelligence, create, code, analyze,
> organize their work, and get things done --- all from one place.**

The design should feel:

> **simple enough for a new user, powerful enough for a professional,
> and scalable enough for a large AI platform.**

The final result must look like a mature product, not a template.

------------------------------------------------------------------------

# 44. Final Instruction To Coding Agent

Implement this specification against the existing ToolHub AI codebase.

Before changing code:

-   inspect existing implementation
-   reuse existing design system
-   preserve existing functionality
-   preserve `/tools` visual language
-   preserve AI Workspace architecture

Then implement the homepage UI/UX described above.

After implementation run:

``` bash
npm run build
npm run lint
```

Run appropriate backend checks if homepage changes touch shared
application code.

Do not report success unless the implementation has been verified.

If something cannot be implemented because the required backend
capability does not yet exist, keep the UI honest and clearly report the
blocker instead of inventing functionality.
