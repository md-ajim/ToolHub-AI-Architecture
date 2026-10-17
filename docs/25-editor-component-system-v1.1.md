# 25 --- Editor Component System

**Updated Version:** 1.1\
**Supersedes:** Master\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v1.1 Addendum --- Scalable Editor Component Contract

Recommended shared primitives:

-   `ApplicationHeader`
-   `WorkspaceToolRail`
-   `ToolRailSearch`
-   `ToolCategory`
-   `ToolItem`
-   `ContextualInspector`
-   `CanvasViewport`
-   `WorkspaceStatusBar`
-   `ProcessingIndicator`
-   `VersionHistory`
-   `BeforeAfterCompare`
-   `OpenWith`
-   `ExportPanel`

``` text
Tool Definition
↓
Tool Registry
↓
Tool Rail
↓
Tool Handler
↓
Inspector
↓
Canvas Operation
↓
History
↓
Export
```

Extend reusable components instead of creating one-off UI patterns.

------------------------------------------------------------------------

## ToolHub AI --- Reusable Professional Editor Components

> **Status:** Master component specification\
> **Goal:** Build a scalable editor component architecture that can
> support current tools and future software-level editing capabilities.

------------------------------------------------------------------------

# 1. Architecture Principle

The editor must be built from reusable primitives rather than one-off
tool pages.

``` text
EditorShell
 ├── EditorHeader
 ├── EditorToolRail
 ├── EditorCanvas
 ├── EditorInspector
 ├── EditorStatusBar
 └── EditorOverlays
```

Tool-specific features plug into this architecture.

------------------------------------------------------------------------

# 2. Core Components

## EditorShell

Responsibilities:

-   viewport layout
-   responsive behavior
-   workspace state
-   global keyboard handling

------------------------------------------------------------------------

## EditorHeader

Responsibilities:

-   navigation
-   project title
-   undo/redo
-   save state
-   export
-   share

------------------------------------------------------------------------

## EditorToolRail

Responsibilities:

-   tool discovery
-   active tool
-   grouping
-   tooltips
-   keyboard shortcuts
-   desktop/mobile adaptation

------------------------------------------------------------------------

## EditorCanvas

Responsibilities:

-   rendering
-   selection
-   zoom
-   pan
-   transforms
-   overlays
-   crop
-   guides
-   direct manipulation

------------------------------------------------------------------------

## EditorInspector

Responsibilities:

-   contextual controls
-   section groups
-   inputs
-   sliders
-   toggles
-   AI actions
-   tool-specific configuration

------------------------------------------------------------------------

## EditorStatusBar

Responsibilities:

-   zoom
-   image dimensions
-   processing state
-   save state
-   selected object information

------------------------------------------------------------------------

# 3. Selection System

Centralize selection state.

``` text
Selection
├── none
├── object
├── text
├── background
├── group
└── multi-select
```

All contextual components should derive their behavior from the
selection model.

------------------------------------------------------------------------

# 4. Tool Registry

Tools should be registered through a centralized definition.

Example conceptual structure:

``` ts
{
  id: "background-remove",
  category: "ai",
  label: "Remove Background",
  icon: "...",
  requiresSelection: false,
  premium: true,
  inspector: "BgRemoveInspector",
  shortcut: "...",
}
```

The implementation may use the project's established TypeScript
conventions.

------------------------------------------------------------------------

# 5. Inspector Architecture

Do not place every tool's UI in one giant conditional component
indefinitely.

Prefer composable inspectors:

``` text
Inspector
 ├── Section
 │    ├── Control
 │    └── Control
 ├── Section
 └── Action
```

Tool-specific inspectors may be registered dynamically.

------------------------------------------------------------------------

# 6. Reusable Control Components

Required reusable primitives:

-   Slider
-   NumberInput
-   Select
-   Combobox
-   Toggle
-   ColorPicker
-   SegmentedControl
-   Button
-   IconButton
-   Popover
-   Tooltip
-   Dropdown
-   Accordion
-   Tabs
-   Sheet
-   Dialog
-   CommandMenu

Use shadcn/ui where appropriate.

------------------------------------------------------------------------

# 7. Image Controls

Reusable image editing controls:

-   CropControl
-   ResizeControl
-   RotateControl
-   FlipControl
-   PositionControl
-   ScaleControl
-   OpacityControl
-   BlurControl
-   AdjustmentControl
-   FilterControl
-   ShadowControl
-   OutlineControl
-   BlendControl

------------------------------------------------------------------------

# 8. AI Components

Reusable AI UI:

### AIActionButton

Shows:

-   AI icon
-   action name
-   processing state
-   premium indicator where applicable

### AIProcessingOverlay

Shows:

-   processing state
-   meaningful progress
-   cancel where supported

### AIResultPreview

Supports:

-   before/after
-   accept
-   retry
-   discard
-   continue editing

### AICommandBar

Supports natural-language editing.

------------------------------------------------------------------------

# 9. Layer Components

Required:

-   LayersPanel
-   LayerRow
-   LayerVisibilityButton
-   LayerLockButton
-   LayerDragHandle
-   LayerActions
-   GroupRow

Future:

-   masks
-   clipping
-   nested groups
-   smart objects

------------------------------------------------------------------------

# 10. Canvas Interaction Components

Required:

-   SelectionBox
-   ResizeHandles
-   RotateHandle
-   CropOverlay
-   AlignmentGuide
-   SnapGuide
-   TransformOverlay
-   DropZone
-   Cursor/interaction state

These must be performant and should not unnecessarily trigger global
React re-renders.

------------------------------------------------------------------------

# 11. Export Components

Reusable:

-   ExportButton
-   ExportDialog
-   FormatSelector
-   QualityControl
-   DimensionControl
-   FilenameInput
-   ExportProgress
-   ExportResult

------------------------------------------------------------------------

# 12. History System

Centralized history must support:

``` text
push
undo
redo
clear
checkpoint
restore
```

AI operations should become history checkpoints.

Example:

``` text
Original
↓
Crop
↓
Background Removal
↓
AI Shadow
↓
Enhancement
```

Undo should operate at meaningful user-action boundaries.

------------------------------------------------------------------------

# 13. Project State

Separate state into logical domains.

``` text
EditorState
├── document
├── canvas
├── selection
├── layers
├── history
├── activeTool
├── processing
├── export
└── UI
```

Avoid one giant unstructured context when the application grows.

------------------------------------------------------------------------

# 14. Persistence

The component architecture must support:

-   local temporary state
-   authenticated project persistence
-   autosave
-   recovery
-   version history

Persistence logic should remain separate from presentational components.

------------------------------------------------------------------------

# 15. Responsive Components

Desktop:

``` text
ToolRail | Canvas | Inspector
```

Mobile:

``` text
Header
Canvas
Horizontal ToolRail
Bottom Sheet Inspector
```

Components should adapt without creating duplicate implementations
wherever practical.

------------------------------------------------------------------------

# 16. Accessibility Components

Every reusable component should define:

-   accessible label
-   keyboard behavior
-   focus behavior
-   disabled state
-   loading state
-   error state

Icon-only controls require tooltips and accessible labels.

------------------------------------------------------------------------

# 17. Loading Components

Avoid generic full-page spinners.

Prefer contextual feedback:

``` text
AI Tool → AI processing indicator
Export → Export progress
Image load → Image placeholder
Inspector → Section skeleton
```

The rest of the editor should remain usable whenever possible.

------------------------------------------------------------------------

# 18. Error Components

Reusable:

-   InlineError
-   RetryButton
-   ProcessingError
-   ExportError
-   UnsupportedFileMessage
-   NetworkError
-   PremiumRequiredMessage

Errors must preserve user work whenever possible.

------------------------------------------------------------------------

# 19. Component Design Rule

A component should be reusable when the same interaction appears in
multiple tools.

Do not copy/paste:

-   crop UI
-   export UI
-   AI processing UI
-   sliders
-   tool buttons
-   inspector sections
-   history controls

Create shared primitives.

------------------------------------------------------------------------

# 20. Tool Plugin Model

The component system should allow future tools to be added through
configuration and feature modules.

Conceptually:

``` text
Tool Definition
      ↓
Tool Registry
      ↓
Editor Tool Rail
      ↓
Tool Handler
      ↓
Inspector
      ↓
Canvas Operation
      ↓
History
      ↓
Export
```

This makes future expansion safer.

------------------------------------------------------------------------

# 21. Performance Rules

Avoid:

-   unnecessary global state updates
-   rerendering the entire canvas on every inspector keystroke
-   huge image data in React state when avoidable
-   synchronous heavy processing on the main thread

Prefer:

-   normalized state
-   memoization where useful
-   debouncing
-   workers for suitable client-side processing
-   server-side async jobs for heavy AI
-   preview-resolution processing before final render

------------------------------------------------------------------------

# 22. Testing

Critical components require:

### Unit tests

-   transforms
-   crop coordinates
-   resize calculations
-   history operations
-   entitlement states

### Integration tests

-   upload → edit → export
-   AI processing → result → undo
-   tool switching
-   project recovery

### Visual QA

-   desktop
-   tablet
-   mobile
-   dark mode
-   light mode

------------------------------------------------------------------------

# 23. Design-System Compliance

All components must use:

-   ToolHub semantic tokens
-   established typography
-   spacing scale
-   radius system
-   shadows
-   motion rules
-   shadcn/ui primitives where appropriate

Do not introduce random styles for individual tools.

------------------------------------------------------------------------

# 24. Future Expansion

The component system must be capable of eventually supporting:

-   layers
-   masks
-   text editing
-   shapes
-   templates
-   AI generation
-   AI replacement
-   AI expansion
-   smart backgrounds
-   brand kits
-   batch editing
-   collaborative projects
-   comments
-   version history
-   plugins/integrations

Do not implement all future features prematurely.

Build extensible foundations first.

------------------------------------------------------------------------

# 25. Golden Rule

> **Every new editor feature must look native to the ToolHub AI editor,
> reuse existing primitives where possible, and integrate with
> selection, history, persistence, responsive behavior, accessibility,
> and export.**
