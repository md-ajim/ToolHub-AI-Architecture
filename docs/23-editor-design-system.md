# 23 --- Editor Design System

**Updated Version:** 1.1\
**Supersedes:** Master\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v1.1 Addendum --- Unified ToolHub AI Editor Shell

The editor design system now standardizes one ToolHub AI application
shell.

``` text
ToolHub AI Brand
+
Minimal Application Header
+
Spacious Tool Rail
+
Canvas-First Workspace
+
Stable Professional Inspector
```

-   Left Tool Rail gets professional breathing room and independent
    scrolling.
-   Right Inspector remains the visual/interaction reference.
-   No public marketing navigation inside the editor.
-   Long labels and large tool collections must not collapse the layout.
-   All new tools reuse ToolHub AI tokens, typography, spacing, motion,
    icons and components.
-   Competitors remain capability benchmarks only; their exact UI is not
    copied.

------------------------------------------------------------------------

## ToolHub AI --- Professional Creative Editor Design System

> **Status:** Master editor UI/UX specification\
> **Purpose:** Define the visual language, interaction principles,
> workspace behavior, and design quality standards for the ToolHub AI
> editor.

------------------------------------------------------------------------

## 1. Core Principle

The ToolHub AI editor must behave like a **professional browser-based
creative application**, not like a normal website with an editor
embedded inside a page.

The editor is a product surface in its own right.

### Primary principles

1.  Full-screen application workspace.
2.  Canvas-first interaction.
3.  Direct manipulation whenever possible.
4.  Context-aware tools and inspectors.
5.  AI and manual editing in one workflow.
6.  Persistent undo/redo and history.
7.  Fast visual feedback.
8.  Desktop and mobile must feel intentionally designed.
9.  ToolHub AI branding must remain original.
10. Competitor interfaces may be researched, but must never be copied.

------------------------------------------------------------------------

# 2. Brand Independence

ToolHub AI may study products such as PhotoRoom, Canva, Adobe Express,
and similar professional editors to understand:

-   expected capabilities
-   interaction conventions
-   information architecture
-   workflow quality
-   accessibility expectations
-   professional editing patterns

However, the implementation must use the ToolHub AI design system.

Never copy:

-   exact layouts
-   exact colors
-   exact typography
-   exact icon arrangements
-   proprietary illustrations
-   branded UI patterns
-   screenshots
-   competitor-specific visual styling

### Rule

> **Use industry-standard interaction concepts; create an original
> ToolHub AI visual and interaction language.**

------------------------------------------------------------------------

# 3. Application Shell

The editor should occupy the viewport.

``` text
┌───────────────────────────────────────────────────────────────┐
│ ToolHub AI │ Project │ Undo │ Redo │ Zoom │ Save │ Export    │
├────────────┬────────────────────────────────┬─────────────────┤
│            │                                │                 │
│ Tool Rail  │                                │ Inspector       │
│            │            Canvas              │                 │
│ Select     │                                │ Contextual      │
│ Crop       │                                │ Controls        │
│ Resize     │                                │                 │
│ AI Tools   │                                │                 │
│ Text       │                                │                 │
│ Elements   │                                │                 │
│ ...        │                                │                 │
├────────────┴────────────────────────────────┴─────────────────┤
│ Status / Zoom / History / Keyboard shortcuts                  │
└───────────────────────────────────────────────────────────────┘
```

Avoid placing the primary editor inside a constrained marketing-page
card.

------------------------------------------------------------------------

# 4. Visual Hierarchy

The canvas receives the strongest visual priority.

Priority order:

1.  Canvas/content
2.  Active editing controls
3.  Tool navigation
4.  Contextual inspector
5.  Secondary application controls
6.  Supporting status information

The UI must never visually compete with the image being edited.

------------------------------------------------------------------------

# 5. Color System

Use semantic design tokens rather than hard-coded colors.

Required token families:

-   background
-   foreground
-   muted
-   muted-foreground
-   border
-   input
-   ring
-   primary
-   primary-foreground
-   destructive
-   success
-   warning

Dark and light themes must use the same semantic structure.

Do not create separate editor designs for dark and light mode.

------------------------------------------------------------------------

# 6. Typography

Typography should be:

-   modern
-   highly legible
-   compact in workspace controls
-   clear at small sizes
-   consistent with the global ToolHub AI brand

Avoid oversized marketing typography inside the editor.

Recommended hierarchy:

``` text
Workspace title
Section title
Control label
Input value
Helper text
Status text
```

------------------------------------------------------------------------

# 7. Tool Rail

The tool rail is the primary navigation mechanism inside the editor.

Typical categories:

### Core

-   Select
-   Crop
-   Resize
-   Rotate
-   Flip

### AI

-   Remove Background
-   Object Remove
-   Enhance
-   Upscale
-   AI Background
-   AI Shadow
-   Generative Edit
-   Expand

### Design

-   Text
-   Shapes
-   Elements
-   Templates
-   Background
-   Brand

### Image

-   Adjust
-   Filters
-   Blur
-   Effects
-   Blend

### Output

-   Export
-   Share

Tools must be grouped logically rather than presented as a long
unstructured list.

------------------------------------------------------------------------

# 8. Context-Aware Inspector

The inspector must change according to the active selection.

Examples:

### No selection

-   Canvas
-   Background
-   Document
-   Resize
-   Export

### Image/object selected

-   Transform
-   Position
-   Adjust
-   Effects
-   Shadow
-   Outline
-   Blur
-   Blend
-   AI actions

### Text selected

-   Font
-   Size
-   Weight
-   Alignment
-   Color
-   Spacing
-   Effects
-   Position

### Background selected

-   Solid
-   Gradient
-   Image
-   AI Background
-   Blur
-   Overlay

------------------------------------------------------------------------

# 9. Direct Manipulation

The canvas must support:

-   drag
-   resize handles
-   rotation
-   object selection
-   multi-selection
-   alignment guides
-   snapping
-   keyboard movement
-   zoom
-   pan
-   bounding boxes

Important operations should not require users to discover hidden numeric
inputs.

Numeric controls remain available for precision.

------------------------------------------------------------------------

# 10. AI Interaction

AI must be integrated into the editor rather than separated into
unrelated pages.

Recommended command surface:

``` text
┌─────────────────────────────────────────────┐
│ ✨ Describe an edit...                  ↑  │
└─────────────────────────────────────────────┘
```

Examples:

-   Remove the background.
-   Make the background a premium studio.
-   Add a realistic soft shadow.
-   Make the product brighter.
-   Replace the background with a modern office.
-   Remove the object on the left.
-   Expand the image to a square composition.

AI actions must preserve undo/history.

------------------------------------------------------------------------

# 11. Layers

The editor should support a real layer model.

Minimum operations:

-   select
-   rename
-   reorder
-   hide
-   show
-   lock
-   unlock
-   duplicate
-   delete
-   group
-   ungroup

Future versions may support:

-   masks
-   clipping
-   nested groups
-   blend modes
-   smart objects

------------------------------------------------------------------------

# 12. Feedback and State

Every operation must communicate its state.

States:

-   idle
-   processing
-   success
-   error
-   cancelled
-   queued
-   unavailable
-   premium-required
-   retryable

Never leave the user wondering whether an action worked.

------------------------------------------------------------------------

# 13. Motion

Motion should be subtle and functional.

Use animation for:

-   panel transitions
-   tool activation
-   AI processing
-   object selection
-   success feedback
-   sheet opening
-   drag/drop feedback

Avoid decorative animation that slows editing.

------------------------------------------------------------------------

# 14. Keyboard-first Quality

Desktop editor must support:

-   Ctrl/Cmd + Z
-   Ctrl/Cmd + Shift + Z
-   Delete/Backspace
-   Escape
-   Arrow keys
-   Shift + Arrow
-   Space + drag for panning
-   Zoom shortcuts
-   tool-specific shortcuts where appropriate

Shortcuts must not conflict with browser/system behavior unnecessarily.

------------------------------------------------------------------------

# 15. Accessibility

Required:

-   keyboard navigation
-   visible focus state
-   sufficient contrast
-   semantic buttons
-   tooltips for icon-only controls
-   accessible labels
-   reduced-motion support
-   screen-reader-friendly controls where practical

------------------------------------------------------------------------

# 16. Performance

The editor must feel responsive even during AI processing.

Heavy operations must not block the UI thread.

Use:

-   async jobs
-   optimistic UI where safe
-   progressive feedback
-   thumbnails/previews
-   debounced controls
-   worker/off-main-thread processing where appropriate
-   cancellation where possible

------------------------------------------------------------------------

# 17. Design Quality Gate

A new editor feature is not complete until:

-   desktop layout is polished
-   mobile layout is intentional
-   dark mode works
-   light mode works
-   loading state exists
-   error state exists
-   undo/redo works where applicable
-   accessibility is considered
-   visual QA is performed
-   export remains correct
-   existing tools are not broken

------------------------------------------------------------------------

# 18. Golden Rule

> **The user should feel that they are operating professional creative
> software, not filling out a form on a website.**
