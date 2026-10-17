# 18 — UI/UX Design System (Editor Workspace Final Update)

**Project:** Multi-Tool Utility / Micro-SaaS Platform  
**Version:** 1.2  
**Status:** Final Design Direction

---

# 1. Brand-Owned Product

The entire platform, including the editor, must use one visual identity.

Use:

```text
Platform Typography
Platform Color Tokens
Platform Spacing
Platform Radius
Platform Borders
Platform Shadows
Platform Icons
Platform Motion
Platform Dark Mode
Platform Light Mode
```

Competitor products are references for interaction patterns only.

Do not clone their visual identity.

---

# 2. Two UX Modes

The product has two major visual modes.

## Public Product Mode

Optimized for:

```text
Discovery
SEO
Education
Conversion
```

## Application Workspace Mode

Optimized for:

```text
Focus
Editing
Productivity
Precision
Export
```

Do not mix the two unnecessarily.

---

# 3. Full-Screen Editor

The editor should occupy nearly the entire available viewport.

It is not a centered card.

Bad:

```text
Marketing page
    ↓
Small editor card
```

Correct:

```text
Full viewport
└── Editor workspace
```

---

# 4. Editor Visual Hierarchy

Priority:

```text
1. Canvas
2. Active tool
3. Contextual inspector
4. Primary action
5. Secondary actions
6. Metadata
```

The image should remain the visual focus.

---

# 5. Workspace Surfaces

Use:

```text
Workspace Background
Panel Surface
Elevated Panel
Active Surface
Popover / Dialog
```

Prefer:

```text
Subtle borders
Surface contrast
Controlled shadows
```

Avoid excessive cards and decorative surfaces.

---

# 6. Desktop Editor

Target:

```text
┌──────────────────────────────────────────────────────────────┐
│ Editor Workspace Header                                      │
├────────────┬──────────────────────────────┬──────────────────┤
│ Tool Rail  │                              │ Inspector        │
│            │           Canvas             │                  │
│            │                              │ Contextual       │
│            │        Full Image            │ Controls         │
├────────────┴──────────────────────────────┴──────────────────┤
│ Zoom / Status / Context / Export                             │
└──────────────────────────────────────────────────────────────┘
```

The canvas must receive the majority of the workspace area.

---

# 7. Canvas-First Rule

Default image presentation:

```text
Fit to Workspace
```

The complete source image should normally be visible on entry.

Provide:

```text
Zoom Out
Zoom Level
Zoom In
Fit
100%
```

Users should not need to manually discover how to see the full image.

---

# 8. Editor Header

Compact:

```text
Back
Tool / File
Undo
Redo
Save
Share
Help
Theme
Export
```

No public marketing navigation.

---

# 9. Tool Rail

The tool rail is compact, icon-led, and contextual.

Possible groups:

```text
Transform
Adjust
AI
Design
```

Example:

```text
Transform
Resize
Crop
Rotate
Flip

Adjust
Brightness
Contrast
Saturation

AI
Background
Object Removal
Enhance
Upscale

Design
Watermark
Text
Shapes
```

Do not expose every tool on every editor.

---

# 10. Contextual Inspector

The inspector must only show controls related to the active tool.

Use:

```text
Primary Controls
↓
Secondary Controls
↓
Advanced Controls
```

Advanced settings should collapse.

---

# 11. Editor Bottom Bar

May contain:

```text
Zoom
Fit
Canvas Size
Selection Size
Status
Export
```

Keep it utility-focused.

---

# 12. Mobile Editor

Mobile should use:

```text
Top Workspace Header
Canvas
Bottom Tool Rail
Contextual Bottom Sheet
```

Do not shrink desktop sidebars into tiny columns.

---

# 13. Tablet Editor

Use:

```text
Tool Rail
Canvas
Collapsible Inspector
```

The inspector may become a drawer.

---

# 14. Focus Mode

The editor should support a dedicated focus/fullscreen mode where supported.

Possible action:

```text
Enter Fullscreen
```

and:

```text
Exit Fullscreen
```

The goal is to maximize usable canvas and reduce distraction.

---

# 15. Design Goal

The editor must feel like:

> A professional application workspace.

Not:

> A webpage containing an editor widget.
