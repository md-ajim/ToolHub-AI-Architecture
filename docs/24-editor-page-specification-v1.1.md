# 24 --- Editor Page Specification

**Updated Version:** 1.1\
**Supersedes:** Master\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v1.1 Addendum --- Spacious Editor Page Contract

``` text
┌───────────────────────────────────────────────────────────────┐
│ Minimal ToolHub AI App Header                                 │
├────────────────┬──────────────────────────────┬───────────────┤
│ Spacious Tool  │            Canvas            │ Stable        │
│ Rail + Search  │                              │ Inspector     │
│ + Categories   │                              │               │
│ + Scroll       │                              │               │
└────────────────┴──────────────────────────────┴───────────────┘
```

The editor must remove unnecessary public website chrome, preserve the
right Inspector model, give the left Tool Rail professional space, keep
the canvas dominant, and remain usable with large tool collections.

------------------------------------------------------------------------

## ToolHub AI --- Full-Screen Editor Page

> **Status:** Master page specification\
> **Scope:** Every ToolHub AI tool that requires interactive image
> editing.

------------------------------------------------------------------------

# 1. Editor Page Philosophy

The editor route is an application workspace.

It must not behave like a normal marketing/tool landing page after
editing begins.

### Standard transition

``` text
Tool Landing Page
        ↓
Upload / Select Image
        ↓
Editor Workspace
        ↓
Edit
        ↓
Export / Save
```

Once the workspace opens, marketing content should not interfere with
the editing surface.

------------------------------------------------------------------------

# 2. Route Structure

Example:

``` text
/tools/image-resizer
/tools/image-resizer/editor
/tools/background-remover
/tools/background-remover/editor
/tools/image-enhancer
/tools/image-enhancer/editor
```

The exact routing convention must remain consistent with the project
route architecture.

------------------------------------------------------------------------

# 3. Full-Viewport Layout

Desktop:

``` text
┌───────────────────────────────────────────────────────────────┐
│ Application Header                                            │
├────────────┬────────────────────────────────┬─────────────────┤
│ Tool Rail  │           Canvas               │ Inspector       │
│            │                                │                 │
│            │                                │                 │
│            │                                │                 │
├────────────┴────────────────────────────────┴─────────────────┤
│ Workspace Status Bar                                          │
└───────────────────────────────────────────────────────────────┘
```

The workspace should use the available viewport height.

Do not center the editor inside a small card.

------------------------------------------------------------------------

# 4. Application Header

Header responsibilities:

### Left

-   ToolHub AI brand
-   back/home control
-   project/document name

### Center

-   optional document title
-   save/sync status
-   editing state

### Right

-   undo
-   redo
-   zoom
-   theme where applicable
-   history
-   share
-   export

Do not overload the header with unrelated website navigation.

------------------------------------------------------------------------

# 5. Tool Rail

The left rail contains editing capabilities.

Requirements:

-   icons
-   labels where space permits
-   active state
-   tooltip
-   category grouping
-   scroll support
-   keyboard accessibility

The rail should remain visually stable while the inspector changes.

------------------------------------------------------------------------

# 6. Canvas Area

The canvas is the primary surface.

Requirements:

-   centered composition
-   fit-to-screen
-   zoom
-   pan
-   checkerboard transparency where relevant
-   selection bounds
-   crop overlay
-   snapping guides
-   safe margins where applicable
-   before/after preview where relevant

The image must remain visually large.

------------------------------------------------------------------------

# 7. Canvas Toolbar

A compact floating or bottom toolbar may provide:

-   zoom out
-   zoom level
-   zoom in
-   fit
-   fullscreen
-   compare/before-after

Do not permanently cover important image content.

------------------------------------------------------------------------

# 8. Inspector

Desktop inspector:

-   persistent
-   scrollable
-   context-aware
-   resizable where appropriate
-   sectioned
-   collapsible

The inspector should not become a modal dialog for ordinary editing.

------------------------------------------------------------------------

# 9. Mobile Layout

Mobile must become an application workspace, not a scaled-down desktop.

Recommended structure:

``` text
┌───────────────────────────┐
│ Header                    │
├───────────────────────────┤
│                           │
│         Canvas            │
│                           │
├───────────────────────────┤
│ Horizontal Tool Rail      │
└───────────────────────────┘
```

When a tool is selected:

``` text
Bottom Sheet
      ↓
Tool-specific Inspector
```

The canvas remains visible behind the sheet whenever practical.

------------------------------------------------------------------------

# 10. Tool-Specific Editor Entry

Each tool should open with a useful initial state.

Examples:

### Background Remover

1.  Image loaded
2.  Background removal preview
3.  Object selected
4.  Cutout controls available
5.  Background options available

### Image Resizer

1.  Image loaded
2.  Current dimensions shown
3.  Aspect ratio control
4.  Resize preview
5.  Export settings

### Image Enhancer

1.  Original preview
2.  Enhancement controls
3.  Before/after comparison
4.  AI processing action
5.  Export

------------------------------------------------------------------------

# 11. AI Processing UX

When an AI task starts:

``` text
User Action
↓
Immediate visual acknowledgement
↓
Processing state
↓
Progress/step information where meaningful
↓
Preview/result
↓
Accept / Retry / Undo
```

Never freeze the entire editor unnecessarily.

------------------------------------------------------------------------

# 12. Premium UX

If a premium capability is unavailable to the user:

Do not simply show a dead/disabled button.

Provide:

-   capability explanation
-   expected benefit
-   preview when possible
-   clear upgrade action
-   current plan information

Example:

``` text
✨ AI 4K Upscale

Enhance your image to high-resolution output.

[ Try Premium ]
```

The user should understand the value before seeing the paywall.

------------------------------------------------------------------------

# 13. Export Experience

Export must be a first-class workflow.

Possible controls:

-   format
-   quality
-   dimensions
-   transparency
-   compression
-   filename
-   metadata options where applicable

Common formats:

-   PNG
-   JPG/JPEG
-   WebP
-   AVIF where supported
-   SVG only for compatible vector content

------------------------------------------------------------------------

# 14. Save and Recovery

For authenticated users, support:

-   project save
-   autosave
-   recovery
-   version/history
-   last edited timestamp

For unauthenticated users, maintain temporary local/session state where
practical.

------------------------------------------------------------------------

# 15. Empty and Error States

Required states:

### Empty

Explain what to do.

### Unsupported file

Explain supported formats.

### Too large

Explain limits and alternatives.

### AI failure

Explain that processing failed and provide retry.

### Network failure

Allow retry without losing the current workspace.

### Export failure

Preserve the project and allow another attempt.

------------------------------------------------------------------------

# 16. Before/After Comparison

AI image tools should support a visual comparison when technically
appropriate.

Interaction options:

-   split slider
-   toggle
-   press/hold
-   side-by-side

The comparison must not destroy the current editing state.

------------------------------------------------------------------------

# 17. No Intrusive Modal Editing

Avoid this pattern:

``` text
Click tool
↓
Huge modal
↓
Edit inside modal
↓
Close
↓
Return to editor
```

Prefer:

``` text
Click tool
↓
Inspector updates
↓
Canvas remains active
↓
Edit directly
```

Use modal/dialog/sheet only when the interaction genuinely requires it.

------------------------------------------------------------------------

# 18. Editor Completion Criteria

A page is production-ready when:

-   workspace fills available viewport
-   image is clearly visible
-   tools are discoverable
-   inspector is contextual
-   direct manipulation works
-   keyboard controls work
-   responsive behavior is intentional
-   AI states are handled
-   export works
-   undo/redo works
-   visual QA passes

------------------------------------------------------------------------

# 19. Primary UX Goal

> **Minimize the distance between intention and result.**

If the user thinks:

> "I want this object brighter."

They should be able to select the object and reach the relevant control
immediately.

------------------------------------------------------------------------

# 20. Page-Level Rule

Every new editor page must reuse the unified editor shell unless there
is a documented product reason not to.

Do not create separate one-off editor layouts for individual tools.
