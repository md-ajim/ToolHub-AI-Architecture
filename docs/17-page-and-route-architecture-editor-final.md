# 17 --- Page & Route Architecture (Editor Workspace Final Update)

**Updated Version:** 1.3\
**Supersedes:** 1.2\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v1.3 Addendum --- Public Experience vs Focused Application Shell

The route architecture is explicitly split into:

``` text
PUBLIC / SEO
/tools/[tool]

FOCUSED APPLICATION
/tools/[tool]/editor
```

The focused application route must never inherit the full public
marketing navigation stack.

### Application-shell contract

``` text
Compact App Header
↓
Workspace Navigation / Tool Rail
↓
Canvas / Conversation / Main Workspace
↓
Contextual Inspector / Controls
```

No duplicate public header + secondary navigation + workspace navigation
stack is permitted.

Public `Pricing`, `Blog`, marketing `Tools`, and similar destinations
stay outside focused workspaces.

------------------------------------------------------------------------

**Project:** Multi-Tool Utility / Micro-SaaS Platform\
**Document:** Page & Route Architecture\
**Version:** 1.2\
**Status:** Final Architecture Update

------------------------------------------------------------------------

# 1. Critical Product Decision

The platform must clearly separate:

``` text
PUBLIC SEO EXPERIENCE
```

from:

``` text
INTERACTIVE APPLICATION EXPERIENCE
```

A tool may therefore have two related routes:

``` text
/tools/[tool]
```

and, for complex editing workflows:

``` text
/tools/[tool]/editor
```

The first is the public SEO/product page.

The second is the focused full-screen application workspace.

------------------------------------------------------------------------

# 2. Public Tool Page

Example:

``` text
/tools/image-resizer
```

This page exists for:

``` text
SEO
Organic Traffic
Tool Discovery
Education
Conversion
Internal Linking
```

Recommended structure:

``` text
Global Header
↓
Breadcrumb
↓
H1
↓
Description
↓
Tool Introduction / CTA
↓
Optional Preview
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

The public page should not sacrifice usability just to add SEO content.

------------------------------------------------------------------------

# 3. Editor Workspace Route

Complex tools may have:

``` text
/tools/[tool]/editor
```

This is an application workspace.

It should NOT contain the normal public website experience.

Do not show:

``` text
Full marketing header
Breadcrumb trail
Large SEO hero
Long SEO paragraphs
FAQ
Public footer
Marketing CTA sections
```

Instead show:

``` text
Editor Header
Tool Rail
Canvas
Inspector
Context Bar
Export
```

------------------------------------------------------------------------

# 4. Full-Screen Editor Principle

When the user enters the editor, the editor becomes the primary product.

Concept:

``` text
Browser Viewport
└── Editor Workspace
    ├── Header
    ├── Tool Rail
    ├── Canvas
    ├── Inspector
    └── Bottom Context Bar
```

The editor should use essentially the full available viewport.

The editor must not appear as a small card inside a normal marketing
page.

------------------------------------------------------------------------

# 5. Editor Navigation

The editor uses a focused workspace header.

Possible controls:

``` text
Back
Tool / Project Name
File Name
Undo
Redo
Save
Share
Help / Keyboard Shortcuts
Theme
Export
```

Do not reuse the full public navigation as the editor's main navigation.

------------------------------------------------------------------------

# 6. Public Page → Editor Flow

Recommended:

``` text
Google Search
↓
Public Tool Page
↓
Use Tool / Upload
↓
Editor Workspace
↓
Edit
↓
Export
↓
Download / Save
```

For simple tools:

``` text
Public Tool Page
↓
Inline Tool Workspace
```

For complex tools:

``` text
Public Tool Page
↓
Open Editor
↓
Full-Screen Editor
```

------------------------------------------------------------------------

# 7. Canonical and SEO Strategy

The public URL remains the primary SEO URL:

``` text
/tools/[tool]
```

The editor route:

``` text
/tools/[tool]/editor
```

is primarily an application route.

Do not duplicate the entire public SEO page inside the editor.

Where appropriate, the editor route can use an application-oriented
indexing strategy.

------------------------------------------------------------------------

# 8. Tool Complexity

Use three levels:

``` text
Level 1
Simple Utility
Upload + Settings + Result

Level 2
Interactive Editor
Canvas + Contextual Controls + Export

Level 3
Advanced Editor
Canvas + History + Layers + AI + Projects
```

Do not force every tool to use Level 3.

------------------------------------------------------------------------

# 9. Strong Editor Candidates

``` text
Image Resizer
Image Cropper
Social Media Resizer
Watermark Tool
Background Remover
Object Remover
Photo Enhancer
Image Upscaler
Passport Photo Maker
Product Image Editor
Mockup Generator
Collage Maker
Advanced Image Editor
```

Simple conversion or text utilities should remain simpler.

------------------------------------------------------------------------

# 10. Navigation Principle

The public website uses:

``` text
Mega Menu
Global Search
Categories
Popular Tools
Featured Tools
```

The editor uses:

``` text
Editor Tool Rail
Contextual Inspector
Workspace Actions
```

These are two different navigation systems serving different goals.

------------------------------------------------------------------------

# 11. Final UX Rule

The user must feel:

``` text
Public Page
→ "I found a useful tool."

Editor
→ "I am now inside the product."
```

That distinction is mandatory.
