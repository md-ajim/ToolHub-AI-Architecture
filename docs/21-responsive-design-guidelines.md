# 21 — Responsive Design Guidelines

**Project:** Multi-Tool Utility / Micro-SaaS Platform  
**Version:** 1.1  
**Status:** Production Specification  
**Depends On:** `18-ui-ux-design-system.md`, `19-page-design-specification.md`, `20-component-design-system.md`

---

## 1. Purpose
**Update:** Added the brand-owned Image Editor Workspace system and related responsive, component, route, AI, and storage rules.

This document defines the responsive design rules for the entire platform.

The website must provide a premium, consistent experience across:

```text
Mobile
Tablet
Laptop
Desktop
Large Desktop
```

Responsive design is not a separate mobile version. The same product experience must intelligently adapt to the available viewport.

---

## 2. Core Principles

```text
Mobile First
+
Fluid Layouts
+
Responsive Components
+
Progressive Enhancement
+
Touch Friendly
+
Accessible
```

Do not simply shrink desktop layouts for mobile.

---

## 3. Breakpoints

Use the existing Tailwind CSS breakpoint system unless a documented requirement demands otherwise:

```text
base → mobile
sm   → 640px
md   → 768px
lg   → 1024px
xl   → 1280px
2xl  → 1536px
```

Prefer content-driven breakpoints over device-specific hacks.

---

## 4. Supported Viewports

Test representative sizes:

```text
320 × 568
375 × 667
390 × 844
430 × 932
768 × 1024
1024 × 768
1280 × 800
1440 × 900
1536 × 864
1920 × 1080
```

Also test both portrait and landscape where relevant.

---

## 5. Container System

Public pages should use a consistent centered container.

Recommended concept:

```text
w-full
max-width
mx-auto
responsive horizontal padding
```

Approximate horizontal padding:

```text
Mobile  → 16px
Tablet  → 24px
Desktop → 32px
```

Exact values must come from the global design-token system.

---

## 6. Content Width

Avoid excessively wide text and tool interfaces.

Recommended:

```text
Marketing Content → max-w-7xl
Reading Content   → max-w-3xl / max-w-4xl
Tool Workspace    → max-w-6xl / max-w-7xl
Dashboard         → max-w-screen-2xl
```

Choose the smallest appropriate container for readability.

---

## 7. Responsive Grid

Use CSS Grid and Tailwind responsive utilities.

Typical pattern:

```text
Mobile  → 1 column
Tablet  → 2 columns
Desktop → 3–4 columns
```

Example:

```text
grid-cols-1
sm:grid-cols-2
lg:grid-cols-3
xl:grid-cols-4
```

Do not force dense multi-column layouts onto small screens.

---

## 8. Tool Cards

Desktop:

```text
3–4 columns where appropriate
```

Tablet:

```text
2–3 columns
```

Mobile:

```text
1 column
```

Tool cards must preserve:

```text
Readable title
Readable description
Visible CTA
Consistent visual hierarchy
```

---

## 9. Mega Menu

The Mega Menu is a core responsive component.

Desktop:

```text
Full Mega Menu
```

Tablet:

```text
Condensed Mega Menu
```

Mobile:

```text
Navigation Drawer
+
Accordion Categories
```

Never squeeze the desktop Mega Menu into a mobile viewport.

The same navigation data must power all layouts.

---

## 10. Header

Desktop:

```text
Logo
Mega Menu
Search
Theme
Auth
User Menu
```

Tablet:

```text
Logo
Tools
Search
Theme
Menu
```

Mobile:

```text
Menu
Logo
Search
User
```

The header must remain usable at narrow widths.

---

## 11. Mobile Navigation

Use a drawer.

Recommended structure:

```text
Menu Drawer
├── Main Navigation
├── Tools
│   ├── Image
│   ├── AI
│   ├── PDF
│   └── ...
├── Popular Tools
├── Pricing
├── Resources
└── Account
```

Large tool categories should use accordions.

---

## 12. Typography

Typography must scale smoothly.

Use:

```text
Responsive Tailwind utilities
clamp()
Global typography tokens
```

Avoid excessively large mobile headings.

Long titles must wrap naturally without overflow.

---

## 13. Buttons

Desktop buttons may be inline.

Mobile buttons may become stacked or full width:

```text
Desktop:
[Upload Image] [Try Sample]

Mobile:
[Upload Image]
[Try Sample]
```

Do not force multiple large CTAs into one narrow row.

---

## 14. Touch Targets

Interactive controls should generally provide at least:

```text
44 × 44px
```

of usable touch area.

Applies to:

```text
Buttons
Icon Buttons
Menu Items
Checkboxes
Switches
Navigation Controls
```

---

## 15. Forms

Desktop:

```text
Two columns where appropriate
```

Mobile:

```text
Single column
```

Example:

```text
Desktop:
Width | Height

Mobile:
Width
Height
```

Forms must remain usable with a virtual keyboard.

---

## 16. Tool Workspace

The tool workspace is a critical responsive area.

Desktop:

```text
┌─────────────────────────────────────┐
│ Tool Header                         │
├──────────────────┬──────────────────┤
│ Input / Preview  │ Settings         │
├──────────────────┴──────────────────┤
│ Result                              │
└─────────────────────────────────────┘
```

Mobile:

```text
Tool Header
↓
Input
↓
Settings
↓
Processing
↓
Result
```

Do not force side-by-side panels on narrow screens.

---

## 17. File Uploader

Desktop:

```text
Large drop zone
```

Mobile:

```text
Compact drop zone
+
Browse button
```

Support touch interaction.

Required states:

```text
Idle
Dragging
Selected
Uploading
Processing
Success
Failed
Rejected
Limit Reached
```

---

## 18. Image Tools

Desktop:

```text
Preview + Controls
```

Tablet:

```text
Preview
Controls
```

Mobile:

```text
Preview
↓
Controls
↓
Actions
```

Do not allow controls to create accidental horizontal overflow.

---

## 19. Before / After

Desktop:

```text
Horizontal comparison
```

Mobile:

```text
Full-width comparison
```

The slider handle must have a sufficiently large touch target.

Where necessary, provide:

```text
Side-by-side
```

as an alternative.

---

## 20. PDF Tools

Desktop:

```text
Preview + Controls
```

Tablet:

```text
Preview
Controls
```

Mobile:

```text
Preview
Settings
Actions
```

Avoid unnecessary horizontal scrolling.

---

## 21. Tables

Large tables must have a mobile strategy.

Allowed patterns:

```text
Horizontal Scroll
Card/List Transformation
Pagination
Priority Columns
```

Do not simply compress a large desktop table until it becomes unreadable.

---

## 22. Dashboard

Desktop:

```text
Sidebar
Main Content
```

Tablet:

```text
Collapsed Sidebar
Main Content
```

Mobile:

```text
Drawer
Main Content
```

Dashboard cards:

```text
Desktop → 3–4 columns
Tablet → 2 columns
Mobile → 1 column
```

---

## 23. Admin Panel

Desktop should optimize for information density.

Mobile should optimize for:

```text
Priority
Readability
Primary Actions
```

Dense admin tables may transform into cards/lists on mobile.

---

## 24. Pricing

Desktop:

```text
3–4 pricing cards
```

Tablet:

```text
2 columns
```

Mobile:

```text
1 column
```

The recommended plan must remain clearly identifiable.

---

## 25. Pricing Comparison

Desktop:

```text
Feature Comparison Table
```

Mobile:

```text
Scrollable Table
```

or:

```text
Feature Groups
Accordion
```

Never create a tiny unreadable comparison table.

---

## 26. Footer

Desktop:

```text
Multi-column
```

Tablet:

```text
Reduced columns
```

Mobile:

```text
Stacked sections
```

Group large tool catalogs by category instead of listing hundreds of tools individually.

---

## 27. Modals

Desktop:

```text
Centered Dialog
```

Mobile:

```text
Full-width Dialog
```

or:

```text
Bottom Sheet
```

depending on the use case.

Mobile dialogs must:

```text
Fit the viewport
Scroll correctly
Have accessible close controls
Trap focus
```

---

## 28. Drawers

Drawers must:

```text
Respect viewport height
Support scrolling
Trap focus
Close with Escape
Provide visible close control
```

Use for:

```text
Navigation
Filters
Advanced Settings
Mobile Options
```

---

## 29. Search

Desktop:

```text
Inline Search
```

Mobile:

```text
Dedicated Search View
```

Search results must remain readable on narrow screens.

---

## 30. Command Palette

Desktop:

```text
Centered Command Palette
```

Mobile:

```text
Near Full-Screen Interface
```

Touch interaction must be supported.

---

## 31. Horizontal Overflow

Avoid accidental page-level horizontal scrolling.

Intentional horizontal scrolling is acceptable for:

```text
Code Blocks
Large Tables
Certain Comparison Interfaces
```

Never allow accidental overflow from:

```text
Header
Hero
Cards
Forms
Navigation
```

---

## 32. Images

Images must be responsive.

Use:

```text
Next.js Image where applicable
width: 100%
height: auto
object-fit
responsive containers
```

Do not use fixed dimensions that break mobile layouts.

---

## 33. Code Blocks

Developer tools may contain long code.

Use:

```text
Horizontal scrolling
Copy button
Syntax highlighting
```

Do not wrap code aggressively when it damages readability.

---

## 34. Toasts

Desktop:

```text
Corner Notification
```

Mobile:

```text
Full-width or Near Full-width
```

Toasts must not cover critical controls.

---

## 35. Sticky Elements

Potential sticky elements:

```text
Tool Action Bar
Dashboard Filters
Mobile Action Bar
```

Never allow sticky UI to cover important content.

Respect mobile safe-area insets where needed.

---

## 36. Mobile Action Bar

For important tool actions, a bottom action area may be used:

```text
┌─────────────────────────────────┐
│ Download          Start Again   │
└─────────────────────────────────┘
```

Use only where it genuinely improves usability.

---

## 37. Spacing

Use global design tokens.

Conceptually:

```text
Large Desktop → Generous
Desktop        → Comfortable
Tablet         → Moderate
Mobile         → Compact
```

Mobile should remain comfortable, not cramped.

---

## 38. Hero Sections

Desktop:

```text
Large Heading
Description
CTA
Visual
```

Mobile:

```text
Heading
Description
CTA
Visual
```

Two-column desktop heroes should naturally stack on narrow screens.

---

## 39. Feature Grids

Typical:

```text
Desktop → 3 columns
Tablet → 2 columns
Mobile → 1 column
```

Test long descriptions and uneven content.

---

## 40. FAQ

Desktop:

```text
FAQ List / Two-column where appropriate
```

Mobile:

```text
Accordion
```

Do not put important FAQ content inside unnecessarily constrained nested scroll areas.

---

## 41. Filters

Desktop:

```text
Sidebar Filters
```

Mobile:

```text
Filter Button
↓
Filter Drawer
```

Do not permanently occupy valuable mobile screen space with filters.

---

## 42. Advanced Settings

On mobile, advanced controls should generally collapse:

```text
Basic Settings

Advanced Settings ▼
```

Do not overwhelm first-time users.

---

## 43. History

Desktop:

```text
Table
```

Mobile:

```text
Cards / List
```

Primary actions must remain accessible.

---

## 44. Authentication

Desktop:

```text
Centered Auth Card
```

Mobile:

```text
Full-width Auth Layout
```

Inputs must remain comfortable when the virtual keyboard is open.

---

## 45. Error Pages

Responsive error pages should contain:

```text
Status
Heading
Explanation
Primary CTA
Secondary CTA
```

Avoid oversized illustrations that push actions below the viewport.

---

## 46. Accessibility

Responsive behavior must preserve:

```text
Keyboard Navigation
Visible Focus
Screen Reader Support
Touch Targets
Color Contrast
Reduced Motion
Zoom Support
```

---

## 47. Browser Zoom

Test at:

```text
100%
125%
150%
200%
```

Critical functionality must remain usable at 200% browser zoom.

---

## 48. Orientation

Support:

```text
Portrait
Landscape
```

especially for:

```text
Mobile
Tablet
Image Editors
PDF Tools
Dashboards
```

---

## 49. Safe Areas

For mobile devices with display cutouts or gesture areas, use safe-area spacing where necessary.

Example:

```css
padding-bottom: env(safe-area-inset-bottom);
```

Do not place critical fixed controls directly against device edges.

---

## 50. Responsive Assets

Use responsive assets where appropriate.

Prefer:

```text
Next.js Image
srcset
Responsive Sizing
Lazy Loading
```

Do not load unnecessarily large desktop assets on mobile.

---

## 51. Performance

Responsive design must not mean shipping two separate applications.

Avoid:

```text
Duplicate Desktop Components
Duplicate Mobile Components
Large Hidden DOM Trees
Unnecessary Client JavaScript
Desktop-only Modules on Mobile
Mobile-only Modules on Desktop
```

Prefer CSS, responsive variants, and composition.

---

## 52. Responsive Component Rule

Prefer:

```text
One Component
+
Responsive CSS
+
Variants
+
Composition
```

Avoid:

```text
DesktopToolCard
MobileToolCard
```

Prefer:

```text
ToolCard
```

with responsive styling.

---

## 53. Content Priority

When space becomes limited:

```text
1. Primary Action
2. Essential Information
3. Navigation
4. Secondary Information
5. Decorative Content
```

Decorative content should disappear before critical functionality.

---

## 54. Mobile Content Reduction

Do not blindly hide desktop content.

Ask:

```text
Is it essential?
Can it move?
Can it collapse?
Can it become an accordion?
Can it become a secondary action?
```

---

## 55. Data Consistency

The same source of truth must power:

```text
Desktop Navigation
Tablet Navigation
Mobile Navigation
Tool Cards
Pricing
Dashboard
History
Search
```

Responsive presentation may differ, but business data must remain consistent.

---

## 56. AI Coding Agent Rules

Before implementing responsive UI, the AI agent must:

```text
1. Read 18-ui-ux-design-system.md
2. Read 19-page-design-specification.md
3. Read 20-component-design-system.md
4. Read this responsive design specification
5. Inspect existing responsive components
6. Reuse existing design tokens
7. Use Tailwind responsive utilities
8. Avoid duplicate desktop/mobile components
9. Test mobile and desktop states
10. Test long content
11. Test light and dark themes
12. Test keyboard accessibility
13. Check horizontal overflow
14. Check 200% zoom
15. Verify touch targets
```

A page is not complete merely because it looks correct on desktop.

Responsive behavior is part of the feature itself.

---

## 57. Responsive QA Checklist

```text
[ ] No accidental horizontal overflow
[ ] Header works on mobile
[ ] Mega Menu works on desktop
[ ] Mobile navigation drawer works
[ ] Tool cards are responsive
[ ] Tool workspace is responsive
[ ] File uploader works with touch
[ ] Forms stack correctly
[ ] Buttons remain usable
[ ] Tables have a mobile strategy
[ ] Dashboard works
[ ] Pricing works
[ ] Modals fit viewport
[ ] Drawers scroll correctly
[ ] Images scale correctly
[ ] Code blocks scroll intentionally
[ ] Dark mode works
[ ] Light mode works
[ ] Keyboard navigation works
[ ] 200% zoom remains usable
[ ] Landscape works
[ ] Safe areas handled
[ ] Loading states work
[ ] Error states work
[ ] Empty states work
```

---

## 58. Definition of Done

A component or page is responsive-complete only when these have been considered and tested:

```text
Mobile
Tablet
Desktop
Large Desktop
Landscape
Dark Mode
Light Mode
Keyboard
Touch
200% Zoom
Loading
Error
Empty
Long Content
```

---

## 59. Final Principle

The platform must feel like one product regardless of viewport.

The target is:

```text
Same Design Language
+
Same Component System
+
Same Navigation Logic
+
Adaptive Layout
+
Adaptive Interaction
+
Excellent Mobile UX
+
Excellent Desktop UX
```

Responsive design is not:

```text
Desktop Design
+
Smaller Screen
```

It is:

```text
One Product
+
Intelligent Adaptation
```

---

# Image Editor Responsive Update — v1.1

The editor has three intentional responsive modes.

## Desktop

```text
Workspace Header
Tool Rail
Canvas
Inspector
Bottom Context Bar
```

## Tablet

```text
Workspace Header
Tool Rail
Canvas
Collapsible Inspector
Bottom Context Bar
```

## Mobile

```text
Top Header
Canvas
Bottom Tool Rail
Contextual Bottom Sheet
```

## Mobile editor rules

```text
Canvas remains dominant
Controls remain touch-friendly
Inspector becomes a bottom sheet
Critical actions remain reachable
Numeric controls are available for precision
```

Touch operations such as pan, zoom, crop, and resize must remain usable. Where gesture precision is poor, expose equivalent numeric controls.

The desktop editor must never be treated as a scaled-down mobile design.
