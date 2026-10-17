# 19 — Page Design Specification (Editor Workspace Final Update)

**Project:** Multi-Tool Utility / Micro-SaaS Platform  
**Version:** 1.2  
**Status:** Final Page Specification

---

# 1. Public Tool Page vs Editor Page

Every complex image feature must be treated as two related experiences.

```text
Public Tool Page
/tools/[tool]

Interactive Editor
/tools/[tool]/editor
```

---

# 2. Public Tool Page

Example:

```text
/tools/image-rotator
```

Structure:

```text
Global Header
↓
Breadcrumb
↓
H1
↓
Short Description
↓
Tool CTA / Upload
↓
Optional Quick Preview
↓
How It Works
↓
Benefits
↓
FAQ
↓
Related Tools
↓
SEO Content
↓
Footer
```

The user should be able to understand the tool quickly.

---

# 3. Editor Page

Example:

```text
/tools/image-rotator/editor
```

The editor page does NOT use the public marketing layout.

Structure:

```text
┌──────────────────────────────────────────────────────────────┐
│ Workspace Header                                              │
├────────────┬──────────────────────────────┬──────────────────┤
│ Tool Rail  │            Canvas            │ Inspector        │
│            │                              │                  │
│            │         Full Image           │ Contextual       │
│            │                              │ Controls         │
├────────────┴──────────────────────────────┴──────────────────┤
│ Zoom | Fit | Status | Export                                 │
└──────────────────────────────────────────────────────────────┘
```

---

# 4. Editor Header Specification

Required where applicable:

```text
Back
Tool / Project Name
File Name
Undo
Redo
Save
Share
Help / Shortcuts
Theme
Export
```

Keep it compact.

---

# 5. Editor Canvas Specification

On entry:

```text
Image loaded
↓
Fit to Workspace
```

The complete image should normally be visible.

Controls:

```text
Zoom In
Zoom Out
Zoom Level
Fit
100%
Fullscreen
```

---

# 6. Inspector Specification

The inspector is contextual.

Examples:

### Rotate

```text
Rotation Angle
Rotate Left
Rotate Right
Flip Horizontal
Flip Vertical
Apply
Reset
```

### Resize

```text
Width
Height
Unit
Lock Ratio
Presets
Apply
```

### Crop

```text
Aspect Ratio
Free Crop
Position
Rotate
Flip
Apply
```

### AI Background

```text
Remove
Refine
Erase
Restore
Background
Apply
```

---

# 7. Tool Rail

Use grouped capabilities:

```text
Transform
Adjust
AI
Design
```

The rail must remain compact.

---

# 8. Editor Empty State

Before an image is loaded:

```text
Upload Image
or
Choose Sample
```

No unnecessary public marketing content.

---

# 9. Editor Processing State

Example:

```text
Processing...
```

Where measurable:

```text
Progress
```

Where not measurable:

```text
Indeterminate Processing
```

Never create fake progress.

---

# 10. Editor Success State

```text
Operation completed

[Export]
[Continue Editing]
[Start Again]
```

---

# 11. Fullscreen / Focus Experience

Entering focus mode should:

```text
Hide public page chrome
Maximize editor workspace
Maximize canvas area
Retain critical editor controls
```

The user's editing state must not be lost when toggling focus mode.

---

# 12. Mobile Editor Specification

```text
Top Header
↓
Canvas
↓
Bottom Tool Rail
↓
Bottom Sheet Inspector
```

Primary actions must remain reachable.

---

# 13. Public SEO Content Placement

SEO content belongs to:

```text
/tools/[tool]
```

not:

```text
/tools/[tool]/editor
```

The editor should remain focused on the task.

---

# 14. Related Tools

After export or successful completion, relevant next actions can appear:

```text
Resize
Compress
Crop
Watermark
Background Removal
```

Do not interrupt the editing workflow unnecessarily.
