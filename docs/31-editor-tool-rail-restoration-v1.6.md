# ToolHub AI --- Editor Tool Restoration & Professional Tool Rail Update

**Document:** `31-editor-tool-rail-restoration-v1.6.md`\
**Version:** 1.6\
**Status:** Implementation-ready update\
**Supersedes:** The Tool Rail / Editor UI portions of v1.5 only; all
broader product requirements remain active.\
**Purpose:** Restore every existing editor tool, preserve the approved
current layout, expand the left Tool Rail professionally, and provide a
safe implementation contract for an AI coding agent.

------------------------------------------------------------------------

## 1. Executive Decision

The current ToolHub AI editor layout is approved and must be preserved.

The current **right-side Inspector is already professional and must not
be redesigned**.

The primary UI improvement is the **left Tool Rail**.

The current problem is a regression in which the Tool Rail can display:

``` text
Search...
No tools found
All tools
```

while the actual previously available tools are not visible.

This is a **functional regression, not an approved redesign**.

### Absolute rule

> **No existing tool may be deleted, hidden, disconnected, renamed, or
> made unreachable because of this update.**

The first implementation task is therefore:

``` text
Inspect existing implementation
        ↓
Find existing Tool Registry / tool definitions
        ↓
Restore all existing tools
        ↓
Verify every existing tool is discoverable
        ↓
Only then improve/expand the Tool Rail
```

Do not start by replacing the tool system with a new hard-coded list.

------------------------------------------------------------------------

# 2. Source Documentation Alignment

This update is based on and must remain consistent with:

-   `31-editor-interaction-usability-qa-v1.5(1).md`
-   `29-mega-menu-information-architecture.md`
-   the existing ToolHub AI editor architecture and design system

The existing documentation already establishes:

-   existing tools must not be removed;
-   the right Inspector is locked;
-   the left Tool Rail should become spacious;
-   the Tool Registry is the single source of truth;
-   the Tool Rail must independently scroll;
-   Tool Search must search the registry;
-   the canvas remains visually dominant;
-   ToolHub AI's own brand must remain intact;
-   competitor products are capability/usability benchmarks only.

This document **adds restoration safeguards and implementation order**
so that those requirements cannot be lost during refactoring.

------------------------------------------------------------------------

# 3. Approved Layout --- DO NOT CHANGE

The approved editor structure remains:

``` text
┌──────────────────────────────────────────────────────────────┐
│                    FOCUSED EDITOR HEADER                     │
├───────────────────────┬───────────────────────────┬──────────┤
│                       │                           │          │
│     TOOL RAIL         │                           │ INSPECTOR│
│     spacious          │          CANVAS           │  LOCKED  │
│     branded           │       visual priority     │  DESIGN  │
│                       │                           │          │
│                       │                           │          │
├───────────────────────┴───────────────────────────┴──────────┤
│                    STATUS / ZOOM / PROGRESS                  │
└──────────────────────────────────────────────────────────────┘
```

### Preserve

-   focused editor header;
-   current canvas position and visual priority;
-   current right Inspector;
-   current professional visual language;
-   ToolHub AI brand;
-   existing spacing, typography, colors, radius, icon strategy, themes
    and design tokens.

### Improve

-   left Tool Rail width;
-   tool discoverability;
-   tool search;
-   category hierarchy;
-   internal scrolling;
-   active/hover/focus states;
-   scalability;
-   existing-tool restoration.

### Do not

-   redesign the right Inspector;
-   replace the editor layout with a competitor layout;
-   add another navigation bar;
-   turn the editor into a marketing page;
-   hide the existing tools behind a generic "More Tools" page;
-   remove tools to make the sidebar cleaner.

------------------------------------------------------------------------

# 4. Existing Tools --- Protected Inventory

The following tools are explicitly protected by the current editor
specification:

``` text
Pan
Resize
Crop
Rotate
Background Remove
Passport
Upscale
Enhance
Object Remove
Social
Product
Mockup
Watermark
```

Also protected:

> **Any additional tool already registered or implemented in the current
> product.**

The agent MUST inspect the codebase and registry to discover the
complete existing inventory before modifying the Tool Rail.

### No destructive cleanup

Do not:

-   delete unused-looking tools;
-   remove duplicate-looking tools without investigation;
-   rename a tool only for UI consistency;
-   move a tool into "coming soon" without evidence;
-   remove a tool because its backend is temporarily unavailable;
-   remove a tool because a new version is being introduced.

If a tool is genuinely deprecated, that is a separate product decision
and requires:

1.  explicit approval;
2.  migration/replacement behavior;
3.  registry status update;
4.  documentation update;
5.  QA confirmation.

------------------------------------------------------------------------

# 5. Tool Registry --- Single Source of Truth

The Tool Registry is authoritative.

Required architecture:

``` text
                    TOOL REGISTRY
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Tool Rail       Mega Menu         Search
        │                │                │
        └────────────────┼────────────────┘
                         │
                 Tools Directory
                         │
                  Category Pages
                         │
                  Related Tools
```

The editor must NOT maintain a separate hard-coded catalog.

Each registry item should provide, where applicable:

``` text
id
display name
icon
category
route
editor route
capability
availability
pricing / premium state
status
ordering
search metadata
aliases
supported input types
supported output types
supported editor contexts
compatible next tools
recent/favorite eligibility
feature flag
analytics identifier
```

### Critical restoration rule

If the registry contains the tools but the UI says:

``` text
No tools found
```

the problem is the rendering/filter/integration path and must be fixed.

Do NOT "solve" the problem by creating a new reduced list.

------------------------------------------------------------------------

# 6. Tool Rail Layout

Recommended desktop width:

``` text
Minimum practical: 220px
Default:           250px
Maximum recommended: 320px
```

The exact value may adapt to viewport and existing design tokens.

Labels must remain readable.

The rail may provide a resize affordance between the rail and canvas.

The user's preferred width may be persisted where the existing
architecture supports it.

------------------------------------------------------------------------

# 7. Tool Rail Structure

Use this conceptual structure:

``` text
┌──────────────────────────────┐
│ 🔍 Search tools...           │
├──────────────────────────────┤
│ QUICK ACCESS                 │
│                              │
│ Pan                          │
│ Resize                       │
│ Crop                         │
│ Rotate                       │
│                              │
│ AI TOOLS                     │
│                              │
│ Background Remove            │
│ Object Remove                │
│ Upscale                      │
│ Enhance                      │
│ ...                          │
│                              │
│ PHOTO                        │
│                              │
│ Adjust                       │
│ Filters                      │
│ Blur                         │
│ Sharpen                      │
│                              │
│ DESIGN                       │
│                              │
│ Social                       │
│ Product                      │
│ Mockup                       │
│ Watermark                    │
│                              │
│ MORE TOOLS                   │
│                              │
│             ↕ Scroll         │
└──────────────────────────────┘
```

The exact list must be generated from the Tool Registry.

**"More Tools" is a discovery action, not a hidden storage location for
existing tools.**

------------------------------------------------------------------------

# 8. Independent Tool Scrolling

The Tool Rail MUST have its own vertical scroll container.

Required:

-   mouse-wheel scrolling;
-   trackpad scrolling;
-   touch scrolling where applicable;
-   keyboard scrolling;
-   scrollbar contained inside the rail;
-   scrollbar must not cover labels;
-   selected tool must remain visible;
-   scrolling must not scroll the entire application;
-   smooth scrolling;
-   correct light/dark behavior;
-   useful scroll-position preservation.

The user should immediately understand:

> "This panel contains more tools."

The canvas and right Inspector must remain stable while the Tool Rail
scrolls.

------------------------------------------------------------------------

# 9. Search

The Tool Rail must contain:

``` text
Search tools...
```

Search MUST query the centralized Tool Registry.

It must support:

-   tool name;
-   category;
-   aliases;
-   keywords;
-   useful synonyms;
-   quick filtering;
-   keyboard interaction;
-   clear/reset;
-   active-state preservation;
-   recent/favorite results where supported;
-   lightweight metadata-only search.

Example:

``` text
Search: background

AI TOOLS
  Background Remove
  Background Generator

BACKGROUND & CUTOUT
  Background Blur
  Background Replacement
```

### No-result state

A genuine no-result state is allowed only when the registry search truly
returns zero matching tools.

It must not occur because:

-   registry data failed to load silently;
-   a category filter is accidentally empty;
-   a feature flag incorrectly hides all tools;
-   a client/server data mismatch occurred;
-   a stale cache is being used;
-   a rendering exception occurred.

If registry loading fails, show a clear **tool loading/error state**,
not a misleading "No tools found".

Example:

``` text
Unable to load tools

Try again
```

------------------------------------------------------------------------

# 10. Tool Discovery Levels

The editor should support:

### Level 1 --- Quick Access

Frequently used or pinned tools.

### Level 2 --- Categorized Tool Rail

All relevant tools available to the editor.

### Level 3 --- Search

Fast discovery of any registered tool.

### Level 4 --- More Tools

Path to the broader ecosystem.

### Level 5 --- Global Tools / Mega Menu

Platform-wide discovery.

Important:

> More Tools must never become the hidden location of the entire editor
> tool ecosystem.

------------------------------------------------------------------------

# 11. Tool Categories

The editor may use relevant groups from the existing documentation:

``` text
Quick Access
Basic
AI Tools
Photo
Background & Cutout
Resize & Crop
Enhancement
Retouching
Product Photography
Social
Design
Templates
Mockups
Batch Processing
Utility
```

The broader platform taxonomy includes:

``` text
Image Editing
AI Image Tools
Background & Cutout
Resize & Crop
Compress & Optimize
Convert
Photo Enhancement
Product Photography
Creative Design
Social Media
Web & Developer
Batch Processing
Templates
Professional Editor
AI Workspace
```

Do not display every category in a cramped editor. Show categories
relevant to the current editor while keeping the full ecosystem
discoverable through the global Tools experience.

------------------------------------------------------------------------

# 12. Tool Rail Visual Quality

The rail must look intentionally designed, not merely enlarged.

Required:

-   readable labels;
-   consistent icon size;
-   clear category hierarchy;
-   controlled vertical spacing;
-   polished active state;
-   subtle hover state;
-   visible keyboard focus;
-   premium/locked indicator where applicable;
-   disabled state;
-   optional recent/favorite indicators;
-   consistent icon/label alignment;
-   no accidental wrapping;
-   no excessive badges;
-   no unnecessary visual noise.

Long labels must not break the layout.

------------------------------------------------------------------------

# 13. Existing Tool Restoration Procedure

The AI coding agent MUST follow this order.

## Step 1 --- Inspect

Inspect:

-   current Tool Registry;
-   existing tool definitions;
-   editor components;
-   Tool Rail components;
-   tool-loading logic;
-   search/filter logic;
-   feature flags;
-   routes;
-   lazy-loading boundaries;
-   existing tool icons;
-   existing category metadata.

Do not create replacements before understanding the current
implementation.

## Step 2 --- Inventory

Produce an internal inventory of:

``` text
Existing registered tools
Existing UI tools
Existing routes
Existing backend operations
Existing hidden/disabled tools
Existing feature-flagged tools
```

Identify discrepancies.

## Step 3 --- Restore

Restore every previously available tool to the Tool Rail.

## Step 4 --- Verify

For every restored tool verify:

``` text
Registry entry
→ Tool Rail
→ Selection
→ Inspector
→ Canvas / workflow
→ Processing
→ Result
→ History
→ Undo/Redo where applicable
→ Export where applicable
```

## Step 5 --- Improve

Only after restoration:

-   improve spacing;
-   improve categories;
-   add search;
-   add scrolling;
-   add favorites/recent;
-   improve active state;
-   improve premium indicators.

## Step 6 --- Expand

Only after existing functionality passes QA, add new tools from the
approved roadmap.

------------------------------------------------------------------------

# 14. New Tool Expansion

The architecture should support growth without requiring another sidebar
redesign.

Existing documentation identifies categories such as:

### Image Editing

-   Image Editor
-   Crop
-   Resize
-   Rotate
-   Flip
-   Adjust
-   Filters
-   Effects
-   Blur
-   Sharpen
-   Add Text
-   Add Shapes
-   Image Overlay

### AI Image Tools

-   AI Image Enhancer
-   AI Image Upscaler
-   AI Background Remover
-   AI Object Remover
-   AI Background Generator
-   AI Image Expand
-   AI Generative Fill
-   AI Image Restoration
-   AI Photo Editor
-   AI Product Image Generator
-   AI Shadow Generator
-   AI Relighting
-   AI Color Enhancement
-   AI Image Cleanup

### Background & Cutout

-   Background Remover
-   Background Changer
-   Background Blur
-   Background Replacement
-   Transparent Background
-   AI Product Background
-   Object Removal
-   Person Removal
-   Text Removal
-   Create Cutout
-   Refine Cutout
-   Edge Refinement

### Resize & Crop

-   Image Resizer
-   Bulk Image Resizer
-   Resize by Dimensions
-   Resize by Percentage
-   Social Media Resizer
-   Smart Crop
-   AI Crop
-   Aspect Ratio Crop
-   Passport Photo Crop
-   Profile Picture Crop
-   Thumbnail Crop

### Compress & Optimize

-   Image Compressor
-   Bulk Image Compressor
-   JPG Compressor
-   PNG Compressor
-   WebP Compressor
-   AVIF Optimizer
-   Image Size Reducer
-   Target File Size Compressor
-   Lossless Compression
-   Web Image Optimizer

### Convert

-   JPG to PNG
-   PNG to JPG
-   JPG to WebP
-   PNG to WebP
-   WebP to JPG
-   WebP to PNG
-   JPG to AVIF
-   PNG to AVIF
-   SVG Converter
-   Image to SVG
-   HEIC Converter
-   BMP Converter
-   TIFF Converter
-   GIF Converter

### Photo Enhancement

-   Photo Enhancer
-   Image Upscaler
-   Face Enhancer
-   Portrait Enhancer
-   Old Photo Restoration
-   Sharpen Image
-   Denoise Image
-   Low-Light Enhancer
-   Color Correction
-   HDR Enhancement
-   Detail Recovery
-   Photo Restoration

### Product Photography

-   Product Background Remover
-   Product Background Generator
-   Product Shadow Generator
-   Product Image Enhancer
-   Product Image Upscaler
-   Product Photo Cleanup
-   Product Scene Generator
-   Product Lighting
-   Product Reflection
-   E-commerce Image Optimizer
-   Marketplace Image Resizer
-   Product Image Batch Processor

These are capability targets/roadmap items. They must not be fabricated
as working features unless the implementation actually exists.

------------------------------------------------------------------------

# 15. Tool Quality Over Tool Count

ToolHub AI may grow from:

``` text
Initial:      30–50 high-quality tools
Medium term:  75–120 tools
Long term:    150+ tools
```

These are capacity targets, not mandatory counts.

Never add tools merely to make the product look large.

Prioritize:

``` text
Usefulness
Reliability
Quality
Workflow integration
Performance
Discoverability
```

over raw feature count.

------------------------------------------------------------------------

# 16. Cross-Tool Workflow

Where compatible:

``` text
Current Result
      ↓
Open With
      ↓
Compatible Tool
      ↓
Continue Editing
```

Example:

``` text
Original
  ↓
Background Remove
  ↓
Enhance
  ↓
Upscale
  ↓
Resize
  ↓
Watermark
  ↓
Compress
  ↓
Export
```

Users should not need to download and re-upload files between compatible
ToolHub AI tools.

------------------------------------------------------------------------

# 17. AI Tool Behavior

AI-heavy tools must provide appropriate:

-   input/prompt;
-   processing state;
-   progress when genuinely measurable;
-   cancel where possible;
-   retry;
-   result preview;
-   compare;
-   accept;
-   reject;
-   save;
-   error recovery.

Heavy AI work must not freeze the editor.

Where appropriate, use background jobs:

``` text
Queued
↓
Processing
↓
Completed / Failed / Cancelled
```

Do not display fake progress percentages.

------------------------------------------------------------------------

# 18. Right Inspector --- LOCKED CONTRACT

The right Inspector is approved and professional.

Do not modify:

-   width;
-   visual language;
-   spacing;
-   typography;
-   hierarchy;
-   overall layout;
-   professional appearance.

New tools may provide contextual controls inside the existing Inspector
system where necessary.

Do not create a second Inspector system.

------------------------------------------------------------------------

# 19. Canvas-First Contract

The canvas remains the visual center.

The implementation must preserve:

-   pan;
-   zoom;
-   fit;
-   selection;
-   direct manipulation;
-   predictable interaction;
-   undo/redo;
-   no accidental scrolling conflicts.

The Tool Rail must never steal canvas space unnecessarily after the
professional width has been established.

------------------------------------------------------------------------

# 20. Performance Requirements

The editor must remain responsive as the tool ecosystem grows.

Prefer:

-   lightweight registry metadata;
-   optimized icons;
-   cached registry data;
-   lazy category content;
-   virtualization for sufficiently large lists;
-   lazy-loading heavy tools;
-   code splitting;
-   editor-shell-first loading.

Opening the editor must NOT initialize every heavy AI implementation.

Search must not load heavy tool implementations merely to display search
results.

------------------------------------------------------------------------

# 21. Accessibility

Required:

-   keyboard navigation;
-   visible focus;
-   Enter to activate;
-   Escape for contextual UI;
-   screen-reader labels;
-   sufficient contrast;
-   touch-friendly targets;
-   accessible tool names;
-   accessible locked/premium states.

Hover must never be the only way to access functionality.

------------------------------------------------------------------------

# 22. Responsive Behavior

### Desktop

``` text
Tool Rail | Canvas | Inspector
```

### Tablet

Support:

-   collapsible Tool Rail;
-   adaptable Inspector;
-   canvas priority;
-   touch-friendly controls.

### Mobile

Do not simply shrink the desktop editor.

Use:

-   contextual panels;
-   bottom sheets where appropriate;
-   tool search;
-   hierarchical tool navigation;
-   touch controls;
-   canvas-first interaction;
-   focused header.

The professional visual language of the current Inspector remains the
reference for responsive patterns.

------------------------------------------------------------------------

# 23. AI Coding Agent --- Mandatory Implementation Rules

Before changing code, the agent MUST:

1.  Read this document.
2.  Read the relevant existing editor documentation.
3.  Inspect the current codebase.
4.  Find the existing Tool Registry.
5.  Find all existing tool definitions.
6.  Compare registry contents with current UI.
7.  Determine why the current UI can show `No tools found`.
8.  Restore existing tools first.
9.  Reuse existing components and state/history infrastructure.
10. Preserve the ToolHub AI design system.
11. Preserve the approved layout.
12. Preserve the right Inspector.
13. Avoid duplicate tool definitions.
14. Avoid hard-coded tool lists.
15. Add new functionality additively.
16. Test desktop and mobile.
17. Test light and dark themes.
18. Test loading/error/success states.
19. Test undo/redo where applicable.
20. Test export where applicable.
21. Perform visual QA.
22. Do not declare completion until the acceptance checklist passes.

------------------------------------------------------------------------

# 24. Forbidden Implementation Behavior

The AI agent MUST NOT:

-   delete existing tools;
-   replace the existing registry with a smaller mock registry;
-   create a temporary hard-coded list as the final solution;
-   redesign the right Inspector;
-   redesign the approved canvas layout;
-   add duplicate navigation bars;
-   hide existing tools exclusively inside "More Tools";
-   remove tools because they are not immediately visible;
-   silently change tool routes;
-   silently rename tools;
-   fabricate tool functionality;
-   mark unfinished tools as available;
-   claim completion without testing actual tool behavior;
-   sacrifice existing functionality for visual cleanliness.

------------------------------------------------------------------------

# 25. Regression Prevention

Before and after the change, compare:

``` text
Existing Tool Count
Existing Registry Entries
Existing Tool Routes
Existing Tool Rail Items
Existing Tool Availability
```

The post-update state must satisfy:

``` text
Post-update existing tools
>=
Pre-update existing tools
```

No existing available tool may disappear.

### Critical regression test

Open the editor with an image loaded.

The Tool Rail must show real tools immediately.

It must NOT show:

``` text
No tools found
```

unless a genuine registry search has zero results.

If the registry cannot load, show an explicit loading/error state and
recovery action.

------------------------------------------------------------------------

# 26. Visual QA Checklist

## Left Tool Rail

-   [ ] Spacious and professional
-   [ ] Approximately 250px default desktop width
-   [ ] Resize affordance works if implemented
-   [ ] Search is prominent
-   [ ] Categories are clear
-   [ ] Independent scrolling works
-   [ ] Scrollbar stays inside the rail
-   [ ] Mouse wheel works
-   [ ] Trackpad works
-   [ ] Touch scrolling works where applicable
-   [ ] Selected tool remains visible
-   [ ] Active state is obvious
-   [ ] Hover state is polished
-   [ ] Keyboard focus is visible
-   [ ] Premium state is clear
-   [ ] Long labels remain readable
-   [ ] No accidental wrapping
-   [ ] Empty search state works
-   [ ] Registry-loading error state works
-   [ ] Large tool collection remains usable
-   [ ] ALL existing tools remain available

## Right Inspector

-   [ ] Current professional layout preserved
-   [ ] Width preserved
-   [ ] Visual hierarchy preserved
-   [ ] Contextual behavior preserved
-   [ ] No unnecessary redesign
-   [ ] Controls remain readable
-   [ ] Apply/action behavior remains clear

## Canvas

-   [ ] Canvas remains visually dominant
-   [ ] Pan works
-   [ ] Zoom works
-   [ ] Fit works
-   [ ] Selection is clear
-   [ ] Direct manipulation is predictable
-   [ ] No accidental scroll conflicts

## Header

-   [ ] Focused editor header
-   [ ] Undo/Redo
-   [ ] Save state
-   [ ] Share
-   [ ] Help/shortcuts
-   [ ] Theme
-   [ ] Export
-   [ ] No public marketing clutter
-   [ ] No duplicate navigation layer

## Architecture

-   [ ] Tool Registry is source of truth
-   [ ] No duplicate tool definitions
-   [ ] Existing components reused
-   [ ] Existing workspace services reused
-   [ ] Heavy tools lazy-load
-   [ ] Large lists remain performant
-   [ ] Documentation matches implementation

------------------------------------------------------------------------

# 27. Definition of Done

This update is NOT complete when the sidebar merely looks better.

It is complete only when:

``` text
Existing tools restored
        ↓
Tool Registry verified
        ↓
Tool Rail integration verified
        ↓
Search verified
        ↓
Independent scrolling verified
        ↓
Tool selection verified
        ↓
Inspector verified
        ↓
Canvas interaction verified
        ↓
Loading/error/success verified
        ↓
History verified
        ↓
Undo/Redo verified
        ↓
Export verified
        ↓
Desktop QA
        ↓
Mobile QA
        ↓
Light/Dark QA
        ↓
Visual QA
        ↓
Performance QA
        ↓
Production ready
```

------------------------------------------------------------------------

# 28. Final Acceptance Contract

The AI coding agent must not report:

> "Done"

until all of the following are true:

-   [ ] Current approved layout remains intact.
-   [ ] Current right Inspector remains intact.
-   [ ] Canvas remains visually dominant.
-   [ ] Every previously available tool is restored.
-   [ ] Existing tool count has not decreased.
-   [ ] Tool Registry is the single source of truth.
-   [ ] Tool Rail is spacious and professional.
-   [ ] Tool Rail scrolls independently.
-   [ ] Search works from the registry.
-   [ ] "No tools found" appears only for a genuine zero-result search.
-   [ ] Registry loading failures have a clear error state.
-   [ ] Categories work.
-   [ ] Active/hover/focus states work.
-   [ ] Premium/locked states are correct.
-   [ ] Long tool names do not break the layout.
-   [ ] New tools are added without removing old tools.
-   [ ] Heavy tools do not unnecessarily block editor startup.
-   [ ] Existing editor state/history infrastructure is preserved.
-   [ ] Undo/Redo works where applicable.
-   [ ] Export works where applicable.
-   [ ] Desktop QA passes.
-   [ ] Mobile/responsive QA passes.
-   [ ] Light/dark QA passes.
-   [ ] Accessibility QA passes.
-   [ ] Performance QA passes.
-   [ ] Visual QA passes.
-   [ ] No duplicate architecture was introduced.
-   [ ] Documentation and implementation agree.

------------------------------------------------------------------------

# 29. Final Product Principle

``` text
TOOLHUB AI BRAND
        +
APPROVED CURRENT LAYOUT
        +
SPACIOUS PROFESSIONAL LEFT TOOL RAIL
        +
ALL EXISTING TOOLS PRESERVED
        +
CENTRAL TOOL REGISTRY
        +
SEARCH
        +
INDEPENDENT SCROLLING
        +
CANVAS-FIRST WORKSPACE
        +
CURRENT RIGHT INSPECTOR PRESERVED
        +
AI CREATIVE TOOLS
        +
CROSS-TOOL WORKFLOWS
        +
AUTOSAVE / HISTORY / RECOVERY
        +
PROFESSIONAL EXPORT
        +
BATCH PROCESSING
        +
SCALABLE TOOL ECOSYSTEM
        +
ACCESSIBILITY
        +
PERFORMANCE
        +
FUTURE-READY ARCHITECTURE
```

> **The design belongs to ToolHub AI.**
>
> **The current approved layout stays.**
>
> **Existing tools stay.**
>
> **The right Inspector stays professional and stable.**
>
> **The left Tool Rail becomes spacious, discoverable, scalable and
> complete.**
>
> **New capabilities are additive.**
>
> **No visual refactor is allowed to cause functional regression.**
>
> **Restore first. Verify second. Improve third. Expand fourth.**

------------------------------------------------------------------------

## Agent Instruction --- Start Here

**Do not modify the UI immediately.**

First inspect the existing implementation and answer internally:

1.  Where is the Tool Registry?
2.  What tools are currently registered?
3.  What tools existed before the current regression?
4.  Why does the Tool Rail currently show `No tools found`?
5.  Is the problem data loading, filtering, feature flags, routing,
    rendering, or registry integration?
6.  Can the existing tools be restored without changing the approved
    layout?

Then implement the smallest safe restoration first.

After restoration passes QA, implement the professional Tool Rail
improvements and only then expand the tool ecosystem.

**Never trade existing working tools for a cleaner-looking sidebar.**
