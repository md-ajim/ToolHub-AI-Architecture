# ToolHub AI --- Dashboard UI/UX Design System & Implementation Specification

**Document:** Dashboard UI/UX Update\
**Product:** ToolHub AI\
**Status:** Mandatory implementation specification\
**Design direction:** ToolHub AI branded, premium, clean,
Vercel-inspired\
**Component foundation:** shadcn/ui\
**Primary visual source of truth:** Existing ToolHub AI `/tools` page
and Mega Menu

------------------------------------------------------------------------

## 1. Purpose

The Dashboard is part of the real ToolHub AI product and must not look
like a separate SaaS template or an independently designed application.

The Dashboard, Projects, History, Saved Files, Usage, Billing, Settings,
AI Workspace and related authenticated pages must share one coherent
ToolHub AI design language.

The primary goal is:

> **Premium, clean, professional, highly usable ToolHub AI UI ---
> inspired by modern Vercel-quality product design without copying
> Vercel.**

The existing ToolHub AI `/tools` page and Mega Menu are the visual
source of truth.

------------------------------------------------------------------------

# 2. Non-Negotiable Design Principles

## 2.1 ToolHub AI branding always wins

Do not replace the existing brand identity with a generic dashboard
theme.

The Dashboard must feel like:

``` text
ToolHub AI
    ↓
Same Design System
    ↓
Tools
Mega Menu
Dashboard
Projects
History
Saved Files
Usage
Billing
Settings
AI Workspace
```

Not:

``` text
Marketing UI
    +
Generic SaaS Dashboard
```

------------------------------------------------------------------------

## 2.2 Vercel-inspired ≠ Vercel copied

Vercel-inspired means adopting high-quality product design principles:

-   clean layouts
-   restrained visual treatment
-   excellent typography
-   strong hierarchy
-   subtle borders
-   precise spacing
-   minimal decoration
-   high information density
-   professional interaction states
-   intentional whitespace

It does **not** mean copying:

-   Vercel branding
-   Vercel logo
-   Vercel exact navigation
-   Vercel exact layout
-   Vercel exact components
-   Vercel exact visual identity

ToolHub AI must remain visibly its own brand.

------------------------------------------------------------------------

# 3. Component Foundation --- shadcn/ui

## Mandatory rule

All Dashboard UI must use **shadcn/ui** as the primary component
foundation.

Prefer existing shadcn/ui primitives instead of creating duplicate
custom components.

Use shadcn/ui/Radix-based components where applicable:

-   Button
-   Card
-   DropdownMenu
-   Avatar
-   Tooltip
-   Separator
-   Input
-   Dialog
-   Sheet
-   Command
-   ScrollArea
-   Popover
-   Tabs
-   Badge
-   Skeleton
-   Alert
-   Select
-   Form

If an equivalent existing ToolHub AI component already exists, reuse it
instead of creating another implementation.

### Do not

-   introduce an unrelated component library
-   mix multiple UI systems without a clear reason
-   create duplicate versions of existing primitives
-   build custom dropdown behavior when shadcn/Radix already provides it
-   create arbitrary one-off styling that breaks the design system

------------------------------------------------------------------------

# 4. Design Source of Truth

The following priority order must be respected:

1.  Existing ToolHub AI brand/design tokens
2.  Existing `/tools` page
3.  Existing Mega Menu
4.  Existing shared components
5.  shadcn/ui conventions
6.  Vercel-inspired modern product-design principles

A new Dashboard design must **not override** the existing ToolHub AI
visual language.

------------------------------------------------------------------------

# 5. Color & Background Rules

## 5.1 No Dashboard-specific theme

Do not introduce a separate Dashboard color system.

The Dashboard must inherit the same color and surface system used by the
existing ToolHub AI `/tools` experience and Mega Menu.

### Forbidden unless already part of the existing brand system

-   random colored page backgrounds
-   blue dashboard canvas
-   purple dashboard canvas
-   decorative gradients
-   unrelated tinted surfaces
-   excessive colored cards
-   arbitrary accent colors
-   different background colors between application sections

------------------------------------------------------------------------

## 5.2 Surface hierarchy

Use the existing ToolHub AI surface tokens.

The UI should primarily communicate hierarchy through:

-   typography
-   spacing
-   borders
-   separators
-   subtle surface changes already defined by the brand system

Do not rely on heavy shadows or decorative backgrounds.

------------------------------------------------------------------------

# 6. Global Application Shell

The authenticated application should use one consistent shell.

Recommended structure:

``` text
┌────────────────────────────────────────────────────────────┐
│ ToolHub AI | Global Navigation                         ... │
├────────────────┬───────────────────────────────────────────┤
│                │                                           │
│ Application    │ Application Header / Search               │
│ Sidebar        │                                           │
│                │                                           │
│                │ Main Dashboard Content                    │
│                │                                           │
│                │                                           │
└────────────────┴───────────────────────────────────────────┘
```

The exact dimensions should follow the existing ToolHub AI design system
and responsive requirements.

The important rule is visual cohesion:

> Global header + sidebar + application content must look like one
> product.

------------------------------------------------------------------------

# 7. Global Header

The global header must remain visually connected to ToolHub AI's
existing public navigation.

It should preserve the existing:

-   logo/brand treatment
-   typography
-   navigation style
-   search treatment
-   theme control
-   AI Workspace access
-   Dashboard access
-   Profile access
-   History access
-   Log out behavior

Do not redesign the global header independently for Dashboard.

------------------------------------------------------------------------

# 8. Sidebar

The current information architecture is acceptable and should remain
coherent:

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
-   radius system

as the rest of ToolHub AI.

------------------------------------------------------------------------

# 9. Sidebar Active State

The active navigation item must clearly indicate the current page while
remaining subtle and premium.

Use the existing ToolHub AI brand accent/color tokens.

Do not introduce a new active color specifically for Dashboard.

Example:

``` text
Projects
[existing ToolHub AI active background]
[existing ToolHub AI accent icon]
```

The exact token must come from the existing project design system.

------------------------------------------------------------------------

# 10. Icon System

Use one consistent icon family.

Preferred:

> **Lucide icons through shadcn/ui-compatible components**

Recommended mappings:

  UI action       Icon
  --------------- -------------------
  Dashboard       `LayoutDashboard`
  AI Workspace    `Sparkles`
  Favorites       `Star`
  Projects        `Folder`
  History         `History`
  Saved Files     `File`
  Usage           `Activity`
  Billing         `CreditCard`
  Settings        `Settings`
  Search          `Search`
  Notifications   `Bell`
  Profile         `User`
  Add/Create      `Plus`
  Expand          `ChevronDown`
  Navigate        `ChevronRight`
  Close           `X`

Keep icon:

-   size consistent
-   stroke weight consistent
-   alignment consistent
-   optical spacing consistent

### Forbidden

-   emoji as UI icons
-   mixed icon libraries
-   random inline SVG styles
-   inconsistent stroke widths
-   decorative icons without purpose

------------------------------------------------------------------------

# 11. User Profile Dropdown --- Critical Fix

The screenshot shows a major UI issue:

The profile dropdown visually enters/overlaps the Dashboard content area
instead of behaving as a properly anchored global overlay.

This must be fixed.

## Required behavior

The profile menu must:

-   anchor to the avatar/profile trigger
-   use shadcn/ui `DropdownMenu`
-   use Radix positioning behavior
-   remain an overlay
-   have correct stacking order
-   remain visually above application content
-   avoid becoming part of the Dashboard layout flow
-   avoid clipping
-   avoid collision with viewport edges
-   close when clicking outside
-   close on Escape
-   remain keyboard accessible

Conceptually:

``` text
Global Header
                         [Avatar]
                            ↓
                     ┌───────────────┐
                     │ Profile       │
                     │ Account       │
                     │ Settings      │
                     │ ───────────── │
                     │ Log out       │
                     └───────────────┘

Dashboard content remains underneath and unaffected.
```

The dropdown must never appear as if it is embedded inside the Dashboard
content.

------------------------------------------------------------------------

# 12. User Menu Hierarchy

The account menu should primarily contain account-related actions.

Recommended structure:

``` text
Profile
email@example.com
──────────────────
Profile
Settings
──────────────────
Log out
```

Project creation is primarily a Projects-page action:

``` text
Projects

                              [ + New Project ]
```

If an existing product requirement explicitly requires `New Project` in
the account menu, it may remain, but it must not visually dominate
account actions.

------------------------------------------------------------------------

# 13. Projects Page

The Projects page should inherit the global application shell.

Recommended structure:

``` text
Projects
Organize your recurring work, files, and favorite tools.

                              [ + New Project ]

────────────────────────────────────────────────────────

Projects content / empty state
```

Do not make the Projects page look like a separate application.

------------------------------------------------------------------------

# 14. Empty State

The empty state should be intentionally minimal and premium.

Current concept:

``` text
        [Folder icon]

        No projects yet

Create a project to group related tools,
processed files, and workflows together.

        [ + Create Project ]
```

This is acceptable, but the container must not become unnecessarily tall
just to create whitespace.

Whitespace should feel intentional, not empty.

### Guidelines

-   use a consistent shadcn Card/surface
-   use existing border tokens
-   use existing radius
-   use a single meaningful icon
-   maintain strong text hierarchy
-   keep supporting text readable
-   use the primary action consistently
-   avoid oversized empty containers

------------------------------------------------------------------------

# 15. Page Header Hierarchy

Every Dashboard page should have a predictable hierarchy:

``` text
Page title
Supporting description

Primary action / page controls

Main content
```

Example:

``` text
Projects
Organize your recurring work, files, and favorite tools.

                              [ + New Project ]

[ content ]
```

Avoid:

-   oversized page titles
-   excessive top spacing
-   excessive empty vertical space
-   competing controls
-   inconsistent title sizes between Dashboard pages

------------------------------------------------------------------------

# 16. Navigation vs Content Hierarchy

The global navigation and application content must have a balanced
visual hierarchy.

A common failure is making the application content visually heavier than
the navigation system in a way that makes the shell feel disconnected.

The desired relationship is:

``` text
Global navigation
      ↓
Application navigation
      ↓
Page header
      ↓
Page content
```

Each level should be visually distinct but part of the same system.

------------------------------------------------------------------------

# 17. Footer

The footer must not look like an unrelated layer.

If a global footer is retained, it must integrate with the application
shell.

Use the same:

-   typography
-   border
-   spacing
-   background
-   alignment

as the rest of ToolHub AI.

Avoid a footer that appears to float over or overlap Dashboard content.

------------------------------------------------------------------------

# 18. Responsive Requirements

## Desktop

Use:

-   global header
-   persistent sidebar
-   main content shell

## Tablet

Use:

-   compact global navigation
-   appropriately reduced sidebar width
-   responsive content spacing

## Mobile

Use:

-   compact header
-   sidebar converted to shadcn/ui Sheet/Drawer
-   full-width content
-   touch-friendly controls
-   no horizontal overflow

At every breakpoint:

> Navigation must never collide with page content.

------------------------------------------------------------------------

# 19. Accessibility

The Dashboard must maintain accessible interaction patterns.

Required:

-   keyboard navigation
-   visible focus states
-   accessible labels
-   semantic buttons
-   semantic navigation
-   sufficient text contrast
-   proper dropdown keyboard behavior
-   Escape-to-close overlays
-   screen-reader-friendly icon buttons
-   tooltips for icon-only controls where necessary

Do not use color alone to communicate state.

------------------------------------------------------------------------

# 20. Interaction Rules

Every interactive element must have:

-   default state
-   hover state
-   focus state
-   active state
-   disabled state
-   loading state where applicable

States must use existing ToolHub AI tokens.

Avoid excessive animation.

Motion should be:

-   subtle
-   fast
-   purposeful
-   consistent

------------------------------------------------------------------------

# 21. Typography

Typography must match the existing ToolHub AI brand system.

Do not introduce a separate Dashboard font.

Use a clear hierarchy:

``` text
Page title
   ↓
Description
   ↓
Section heading
   ↓
Body
   ↓
Supporting metadata
```

Avoid unnecessarily heavy typography.

Premium design should come from hierarchy and spacing rather than
oversized text.

------------------------------------------------------------------------

# 22. Spacing

Use a consistent spacing scale.

Do not manually invent unrelated margins on each page.

Prefer the project's existing spacing tokens/utilities.

Common layout rules:

-   consistent page padding
-   consistent sidebar gap
-   consistent section spacing
-   consistent card padding
-   consistent control spacing
-   consistent icon/text gap

------------------------------------------------------------------------

# 23. Borders, Radius & Shadows

Use the existing ToolHub AI/shadcn visual language.

Preferred:

-   subtle borders
-   restrained radius
-   minimal shadows
-   clean surfaces

Avoid:

-   heavy drop shadows
-   excessive rounded cards
-   floating-card-everything design
-   decorative glassmorphism

Premium ≠ more effects.

------------------------------------------------------------------------

# 24. No Design Drift Across Pages

The following pages must share the same shell:

-   Dashboard
-   AI Workspace
-   Projects
-   History
-   Saved Files
-   Usage
-   Billing
-   Settings
-   Profile

A developer must not independently redesign any of these pages.

If a component already exists, reuse it.

If a token already exists, use it.

If a pattern already exists on `/tools` or Mega Menu, follow it.

------------------------------------------------------------------------

# 25. Forbidden Dashboard Patterns

Do not introduce:

-   unrelated dashboard templates
-   random gradients
-   dashboard-specific color palettes
-   excessive card nesting
-   excessive shadows
-   emoji icons
-   mixed icon libraries
-   Vercel clone UI
-   generic SaaS starter-kit styling
-   oversized empty containers
-   floating UI that overlaps content unintentionally
-   browser `alert()`/`prompt()` for polished product interactions
-   inconsistent modal/dropdown implementations
-   page-specific navigation shells

------------------------------------------------------------------------

# 26. Modal & Dialog Rule

Do not use native browser:

``` js
alert()
confirm()
prompt()
```

for production UI.

Use shadcn/ui:

-   Dialog
-   AlertDialog
-   Form
-   Input

For project creation, use a proper branded dialog:

``` text
Create project

Project name
[________________________]

Description (optional)
[________________________]

              Cancel    Create Project
```

The dialog must use the same ToolHub AI/shadcn visual system.

------------------------------------------------------------------------

# 27. Project Creation

The Projects page primary CTA:

``` text
[ + New Project ]
```

must open a proper shadcn/ui Dialog.

Requirements:

-   accessible label
-   keyboard support
-   validation
-   loading state
-   disabled submit state when invalid
-   clear success/error feedback
-   no native browser prompt

------------------------------------------------------------------------

# 28. Layering / Z-Index Rules

Global overlays must have predictable stacking.

Recommended conceptual layers:

``` text
Base application
    ↓
Sticky navigation
    ↓
Dropdown / Popover
    ↓
Dialog
    ↓
Modal overlay
```

Do not solve layering problems by blindly increasing `z-index`
everywhere.

First identify:

-   stacking context
-   positioned parent
-   overflow clipping
-   portal behavior
-   transform/filter contexts

Use Radix/shadcn portals where appropriate.

------------------------------------------------------------------------

# 29. QA Checklist

Before marking Dashboard work complete, verify:

## Visual

-   [ ] Dashboard matches ToolHub AI `/tools`
-   [ ] Dashboard matches Mega Menu design language
-   [ ] No unrelated background colors
-   [ ] No accidental gradients
-   [ ] Typography is consistent
-   [ ] Icons are consistent
-   [ ] Borders are consistent
-   [ ] Radius is consistent
-   [ ] Spacing is consistent

## Navigation

-   [ ] Global header is consistent
-   [ ] Sidebar is consistent
-   [ ] Active state is correct
-   [ ] Navigation does not collide with content
-   [ ] Mobile navigation works

## Profile

-   [ ] Avatar opens dropdown
-   [ ] Dropdown is anchored correctly
-   [ ] Dropdown does not enter document flow
-   [ ] Dropdown does not overlap content incorrectly
-   [ ] Escape closes dropdown
-   [ ] Outside click closes dropdown
-   [ ] Keyboard navigation works

## Projects

-   [ ] Page header is consistent
-   [ ] New Project CTA is correctly positioned
-   [ ] Empty state is proportional
-   [ ] Create Project opens shadcn Dialog
-   [ ] No browser prompt is used
-   [ ] Validation works

## Accessibility

-   [ ] Focus states work
-   [ ] Icon-only buttons have labels/tooltips
-   [ ] Contrast is sufficient
-   [ ] Keyboard navigation works
-   [ ] Dialog/dropdown semantics are correct

## Responsive

-   [ ] Desktop verified
-   [ ] Tablet verified
-   [ ] Mobile verified
-   [ ] No horizontal overflow
-   [ ] Sidebar transitions correctly
-   [ ] Header remains usable

------------------------------------------------------------------------

# 30. Definition of Done

Dashboard UI is considered complete only when:

1.  It visually belongs to ToolHub AI.
2.  It follows the existing `/tools` and Mega Menu design language.
3.  It uses shadcn/ui as the component foundation.
4.  It follows the ToolHub AI color/background system.
5.  It does not introduce a separate dashboard theme.
6.  It is Vercel-inspired but not a Vercel copy.
7.  Global navigation and application navigation feel unified.
8.  Profile dropdown is correctly anchored and layered.
9.  Project creation uses a proper branded dialog.
10. Icons are consistent.
11. Responsive behavior is verified.
12. Accessibility basics are verified.
13. No page introduces design-system drift.

------------------------------------------------------------------------

# 31. Implementation Priority

Fix in this order:

### P0 --- Structural

1.  Unify Dashboard shell with ToolHub AI `/tools`.
2.  Remove dashboard-specific background/surface styling.
3.  Fix global header + sidebar + content relationship.
4.  Fix profile dropdown positioning and stacking.
5.  Replace native browser prompts with shadcn Dialog.

### P1 --- Design System

6.  Enforce shadcn/ui primitives.
7.  Normalize icon system.
8.  Normalize colors.
9.  Normalize borders/radius.
10. Normalize typography.
11. Normalize spacing.

### P2 --- UX Polish

12. Improve empty-state proportions.
13. Improve page-header hierarchy.
14. Improve navigation states.
15. Improve responsive behavior.
16. Improve accessibility.
17. Add interaction/loading/error states.

### P3 --- Verification

18. Desktop QA.
19. Tablet QA.
20. Mobile QA.
21. Visual regression comparison against `/tools` and Mega Menu.
22. Verify no design drift across Dashboard pages.

------------------------------------------------------------------------

# 32. Final Product Principle

The Dashboard must communicate:

> **"This is ToolHub AI."**

Not:

> "This is a generic dashboard template."

The interface should be clean enough to feel premium, restrained enough
to feel professional, and branded enough to be unmistakably ToolHub AI.

The visual philosophy is:

``` text
ToolHub AI Brand
      +
shadcn/ui
      +
Vercel-quality product discipline
      +
ToolHub AI's own visual identity
      =
Premium ToolHub AI Dashboard
```

**Never sacrifice ToolHub AI's own brand identity in pursuit of a
generic "modern" look.**
