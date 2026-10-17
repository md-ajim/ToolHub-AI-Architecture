# 22 — UI Design AI Guide (Editor Workspace Final Update)

**Project:** Multi-Tool Utility / Micro-SaaS Platform  
**Version:** 1.2  
**Status:** Mandatory AI UI Implementation Guide

---

# 1. Critical Instruction

The AI Coding Agent must understand that:

```text
A public tool page
```

and:

```text
An interactive editor workspace
```

are different UI experiences.

Do not place a professional editor inside a small marketing card.

---

# 2. Editor Trigger

For complex image tools:

```text
Public Tool Page
↓
Use Tool / Upload
↓
Open Editor
↓
Full-Screen Workspace
```

The editor becomes the primary application view.

---

# 3. Do Not Build This

Do NOT create:

```text
Global Website Header
+
Breadcrumb
+
Huge H1
+
SEO text
+
Small Editor Card
```

for the interactive editor route.

---

# 4. Build This

Use:

```text
Full-Screen Editor
├── Workspace Header
├── Tool Rail
├── Canvas
├── Contextual Inspector
└── Bottom Context Bar
```

---

# 5. Canvas Rule

On editor entry:

```text
Load Image
↓
Fit to Workspace
```

The image should normally be fully visible.

The editor must not intentionally crop the visible image simply because the canvas is too small.

---

# 6. Canvas Interaction

Where applicable:

```text
Zoom
Pan
Fit
100%
Selection
Crop
Resize
Transform
```

Provide exact numeric controls when precision is needed.

---

# 7. Fullscreen Rule

A professional editor must provide a focus-oriented workspace.

Support:

```text
Enter Fullscreen
Exit Fullscreen
```

The editor must preserve the editing state while toggling focus/fullscreen.

---

# 8. Public Navigation vs Editor Navigation

Public pages:

```text
Mega Menu
Global Search
Pricing
Blog
Dashboard
```

Editor:

```text
Back
Tool/File
Undo
Redo
Save
Share
Help
Theme
Export
```

Do not mix these navigation systems.

---

# 9. UI Quality Rule

Do not declare an editor complete because:

```text
Canvas renders
Crop works
Resize works
Export works
```

Also verify:

```text
Workspace hierarchy
Canvas size
Panel proportions
Visual balance
Dark mode
Light mode
Mobile
Tablet
Fullscreen
Touch
Keyboard
Loading
Error
Success
```

---

# 10. Visual QA Loop

Mandatory:

```text
Implement
↓
Run App
↓
Render / Screenshot
↓
Inspect
↓
Fix
↓
Render Again
↓
Final QA
```

Pay special attention to:

```text
Canvas visibility
Panel width
Toolbar density
Inspector readability
Whitespace
Alignment
Button hierarchy
Mobile usability
```

---

# 11. Brand Ownership

Competitor screenshots may inspire:

```text
Canvas workflow
Contextual inspector
Tool rail
Undo/Redo
Export
Zoom
```

But the implementation must use:

```text
Platform Brand
Platform Tokens
Platform Components
Platform Typography
Platform Icons
Platform Motion
```

Do not copy another company's UI.

---

# 12. AI Image Tool Integration

AI tools inside the editor must behave like native editing capabilities.

Examples:

```text
Background Removal
Object Removal
Enhancement
Upscaling
Restoration
AI Background
```

They must use the shared editor system.

Do not create separate unrelated AI pages when an editor interaction provides a better workflow.

---

# 13. Editor Complexity Rule

Use:

```text
Level 1 → Simple Utility
Level 2 → Interactive Editor
Level 3 → Advanced Editor
```

Do not add advanced layers/history systems to simple tools unless needed.

---

# 14. Final AI Rule

When asked:

```text
Create an image editor
```

the agent must interpret it as:

> Build a professional, full-screen, responsive, brand-owned editing workspace according to the editor design system and component architecture.

It must NOT interpret it as:

> Put a small image editor inside a normal webpage.
