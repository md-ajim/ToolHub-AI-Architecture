# 20 — Component Design System (Editor Workspace Final Update)

**Project:** Multi-Tool Utility / Micro-SaaS Platform  
**Version:** 1.2  
**Status:** Final Component Architecture

---

# 1. Editor Components

The editor is a reusable component ecosystem.

Core:

```text
EditorShell
EditorHeader
EditorToolRail
EditorSecondaryPanel
EditorCanvas
EditorInspector
EditorToolbar
EditorBottomBar
EditorZoomControls
EditorHistory
EditorLayers
EditorExportPanel
EditorBeforeAfter
EditorStatusBar
EditorFullscreen
```

---

# 2. EditorShell

Owns:

```text
Full-screen layout
Responsive layout
Panel arrangement
Workspace context
Theme integration
Keyboard handling
```

It must not contain image-tool business logic.

---

# 3. EditorHeader

Components:

```text
EditorBackButton
EditorTitle
EditorFileName
EditorUndoRedo
EditorSave
EditorShare
EditorHelp
EditorThemeSwitcher
EditorFullscreen
EditorExport
```

---

# 4. EditorToolRail

Purpose:

```text
Primary editor navigation
```

Must support:

```text
Active
Hover
Focus
Disabled
Premium
```

It should be data-driven.

---

# 5. EditorCanvas

Owns:

```text
Image rendering
Zoom
Pan
Selection
Transform
Guides
Grid
Before/After
```

Default behavior:

```text
Fit image to available workspace
```

---

# 6. EditorInspector

Displays controls for the active tool only.

Examples:

```text
ResizeInspector
CropInspector
RotateInspector
WatermarkInspector
BackgroundInspector
ObjectRemovalInspector
UpscaleInspector
EnhanceInspector
```

These are feature panels, not separate visual systems.

---

# 7. EditorBottomBar

Contains:

```text
Zoom
Fit
Canvas Information
Status
Export
```

Mobile behavior may transform it into contextual actions.

---

# 8. EditorFullscreen

Must support:

```text
Enter Fullscreen
Exit Fullscreen
```

The component should preserve:

```text
Current Tool
Canvas State
Zoom
Selection
Edit History
```

when entering or leaving focus mode.

---

# 9. Capability Components

Reusable controls:

```text
ResizeControls
CropControls
RotateControls
FlipControls
AdjustControls
FilterControls
WatermarkControls
BackgroundControls
ObjectRemovalControls
UpscaleControls
EnhanceControls
PresetSelector
ExportControls
```

---

# 10. Tool Configuration

Instead of creating a separate editor application for every feature:

```text
EditorShell
+
Capability Configuration
+
Tool-specific Business Logic
```

Example:

```text
Image Resizer
→ Resize + Export

Social Resizer
→ Resize + Crop + Presets + Export

Background Remover
→ AI Background + Refine + Before/After + Export
```

---

# 11. Editor Tool Registry

Conceptual:

```ts
type EditorToolDefinition = {
  id: string
  name: string
  icon: string
  capabilities: string[]
  requiresAI?: boolean
  requiresCredits?: boolean
  premium?: boolean
}
```

---

# 12. Responsive Component Behavior

Desktop:

```text
ToolRail = Vertical
Inspector = Side Panel
```

Tablet:

```text
ToolRail = Vertical
Inspector = Collapsible
```

Mobile:

```text
ToolRail = Horizontal Bottom Rail
Inspector = Bottom Sheet
```

---

# 13. Reuse Rule

Before building a new editor component:

```text
Inspect
↓
Reuse
↓
Variant
↓
Compose
↓
Create only if genuinely necessary
```

Never create a separate editor shell for each tool.

---

# 14. Performance

Do not load advanced editor capabilities when they are not needed.

Examples:

```text
Layers engine
Advanced AI panels
Complex mockup controls
PDF viewers
```

should be lazy-loaded where appropriate.

---

# 15. Accessibility

All editor components must support, where applicable:

```text
Keyboard Navigation
Focus States
Accessible Names
Status Announcements
Reduced Motion
Touch Targets
Equivalent Numeric Controls
```

---

# 16. Final Principle

The editor must be a platform-level reusable system:

```text
One Editor Shell
+
Many Capabilities
+
Many Specialized Tools
```

Not:

```text
Many independent editors
```
