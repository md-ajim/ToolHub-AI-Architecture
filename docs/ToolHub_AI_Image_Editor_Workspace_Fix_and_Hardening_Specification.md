# ToolHub AI — Image Editor Workspace Stability & UX Fix Specification

**Document Type:** Production Fix & Hardening Specification  
**Scope:** Existing Image Editor Workspace  
**Priority:** High  
**Goal:** Fix the currently identified workspace/layout/result-flow problems **without removing or breaking any existing tools or functionality**.

---

## 1. Core Safety Rule

This is an **incremental fix specification**, not a rewrite.

### MUST NOT

- Remove any existing editor tool.
- Remove any existing tool category.
- Rename existing tools unless strictly required for a bug fix.
- Disable existing tools.
- Replace the current editor workspace with a new layout.
- Rewrite the editor state architecture unnecessarily.
- Remove current canvas, inspector, toolbar, search, export, history, or tool-lock behavior.
- Delete existing registry entries.
- Change existing backend APIs unless required for compatibility.
- Change existing tool pricing/plan behavior as part of this task.
- Introduce placeholder implementations in place of working functionality.

### MUST

- Inspect the current implementation before changing it.
- Preserve all existing behavior that already works.
- Make changes backward-compatible.
- Prefer small, isolated patches.
- Run existing tests/build/type checks after each major change.
- Verify the workspace visually after implementation.

---

# 2. Existing Workspace Context

The current Image Editor Workspace contains:

## Left Tool Rail

Existing tools include:

### Basic Editing

- Pan
- Resize
- Crop
- Rotate / Flip
- Compress
- Convert
- Social Media Resize
- Watermark

### AI Tools

- Background Remove
- Passport Photo
- Upscale
- Enhance
- Object Remove
- Generative Fill
- Background Generate
- Expand
- Relight

### Design / Product

- Social
- Product
- Mockup
- Watermark

The exact current registry remains the source of truth. **Do not remove tools simply because some tools are incomplete.**

---

# 3. Problem A — Tool Rail Does Not Clearly Support Many Tools

## Current Problem

The left tool rail can contain many tools.

When the number of tools increases:

- users may not realize that additional tools exist below the visible area;
- tools can extend beyond the available viewport;
- the workspace becomes difficult to navigate;
- the tool rail can visually compete with the canvas;
- the user may need to scroll the entire page instead of only the tool list.

## Required Solution

Implement an **independently scrollable Tool Rail**.

Only the left tool list should scroll.

The following must remain stable:

- top workspace header;
- canvas;
- right inspector;
- editor state;
- current image;
- zoom/pan behavior.

---

# 4. Tool Rail Scroll UX Requirements

## 4.1 Dedicated Scroll Container

The tool list must be inside a constrained vertical container.

Conceptually:

```text
Workspace
├── Header
├── Main Editor
│   ├── Left Tool Rail
│   │   ├── Search
│   │   └── Scrollable Tool List
│   ├── Canvas
│   └── Inspector
└── Status Bar
```

Only:

```text
Scrollable Tool List
```

should have vertical overflow.

Do NOT make the entire editor workspace scroll vertically just to access tools.

---

## 4.2 Scroll Behavior

Support:

- mouse wheel;
- trackpad;
- touchpad scrolling;
- keyboard navigation where practical;
- native browser accessibility behavior.

Use smooth scrolling where it does not interfere with performance.

Avoid JavaScript-based custom scrolling unless there is a demonstrated need.

Prefer native CSS overflow behavior.

---

# 5. Scrollbar UX

The scrollbar should be:

- visually unobtrusive;
- narrow;
- visible enough to communicate that more tools exist;
- more apparent on hover/focus;
- compatible with light/dark themes;
- accessible;
- non-blocking.

Do not create a large scrollbar that consumes excessive Tool Rail width.

---

# 6. Additional-Tools Visual Cue

A scrollbar alone is not enough.

When additional tools exist below the visible area, provide a subtle visual cue.

Recommended behavior:

```text
┌──────────────┐
│ Enhance      │
│ Object Remove│
│ Generative   │
│ Background   │
│ Expand       │
│              │
│   ↓          │
└──────────────┘
```

Use a subtle bottom fade/gradient or equivalent visual affordance.

The cue should disappear when the user reaches the bottom.

Similarly, if useful, show a top fade when content exists above the current scroll position.

Do not permanently cover tool labels with the gradient.

---

# 7. Tool Rail Search Must Remain

The existing search field must remain functional.

Search should filter the existing registry rather than introducing a separate hardcoded tool list.

Search must:

- match tool names;
- match useful aliases where available;
- preserve locked/pro indicators;
- preserve category context where possible;
- allow clearing quickly;
- show a useful empty state if no tools match.

Do not remove the current search UI.

---

# 8. Category Sections Must Remain

Existing category groupings must remain.

Examples:

- AI TOOLS
- DESIGN
- OUTPUT

The implementation may improve spacing/visual hierarchy, but categories must not be removed merely to make scrolling easier.

---

# 9. Active Tool State

The selected tool must remain clearly highlighted.

Requirements:

- active tool is visually distinguishable;
- active state survives Tool Rail scrolling;
- clicking another tool updates the inspector;
- selected state must come from editor state rather than duplicated local state where possible.

Do not create two competing sources of truth for the selected tool.

---

# 10. Locked / Pro Tools

Existing locked/pro behavior must remain intact.

For locked tools:

- show the existing lock indicator;
- preserve the existing subscription/upgrade behavior;
- do not silently enable paid functionality;
- do not remove the tool from the registry.

The scrollbar implementation must not change entitlement logic.

---

# 11. Problem B — Saved/Processed Image Position

## Current Observed Behavior

The canvas uses a transformed image/canvas coordinate system.

The current architecture uses concepts such as:

```text
pan.x
pan.y
zoom
currentImageUrl
history
```

The canvas transformation is conceptually:

```text
translate(pan.x, pan.y) scale(zoom)
```

The current image/result is therefore displayed inside the centered canvas workspace rather than being stored as a separate page-layout object.

---

# 12. Required Result Position Behavior

After a successful image operation:

1. The processed image becomes the current editor image.
2. The canvas remains centered.
3. The image is fitted appropriately to the available canvas.
4. Existing zoom behavior is preserved where appropriate.
5. Existing pan state must not cause the newly generated result to appear unexpectedly outside the visible canvas.
6. The user must never receive a blank canvas simply because the result changed.
7. The right inspector remains usable.
8. The current image dimensions/status update correctly.

Recommended default after replacing the image:

```text
currentImageUrl = processedResult
pan = safe/default centered position
zoom = calculated fit zoom
```

Do not blindly reset zoom/pan if the existing product UX intentionally preserves them. Determine the correct behavior from the current editor state and tests.

---

# 13. Problem C — Result Application Pipeline

The current result application flow has risk around:

- result URL parsing;
- blob/file conversion;
- stale results;
- original/result confusion;
- history updates.

## Required Architecture

A successful operation should follow:

```text
User Action
   ↓
Validate Input
   ↓
Create Operation ID
   ↓
Submit Operation
   ↓
Loading
   ↓
Poll / Stream Status
   ↓
Success
   ↓
Validate Result
   ↓
Fetch Result
   ↓
Create Valid Image File/URL
   ↓
Replace Current Image
   ↓
Push History Entry
   ↓
Fit Canvas
   ↓
Ready
```

---

# 14. Result Validation

Before replacing the current image:

Verify:

- response exists;
- operation belongs to the current user/session;
- operation ID matches the active operation;
- result URL/file data exists;
- result is actually an image;
- response is not stale;
- result can be fetched successfully.

If validation fails:

- keep the previous image;
- show a meaningful error;
- do not push a broken history entry.

---

# 15. Stale Result Protection

A previous operation must never overwrite a newer operation.

Example:

```text
Operation A → running
Operation B → running

B finishes first
→ apply B

A finishes later
→ DO NOT replace B with A
```

Use an operation identifier/version/request token.

The currently active operation must be authoritative.

---

# 16. History Safety

Every successful result must create a valid history state.

History entries should represent:

```text
Image State
+
Operation Metadata
```

At minimum, avoid pushing:

- undefined URLs;
- invalid blobs;
- failed results;
- stale results;
- duplicate result states.

Undo/redo must continue to work after AI operations.

---

# 17. Operation Lifecycle

Every operation must have a clear lifecycle:

```text
idle
  ↓
validating
  ↓
submitting
  ↓
processing
  ↓
success
  ↓
applied
```

Failure path:

```text
processing
  ↓
error
  ↓
retry / dismiss
```

Cancellation/timeout must not leave the UI permanently stuck.

---

# 18. Polling Cleanup

If polling is used:

- clear the interval when operation succeeds;
- clear it on error;
- clear it on timeout;
- clear it when the component unmounts;
- clear it when a new operation supersedes the old one.

Do not allow multiple polling loops to accumulate.

---

# 19. Retry Behavior

Retry should:

- create a new operation ID;
- not reuse a stale result;
- preserve the original image;
- reset only the operation state;
- provide clear progress feedback.

A failed operation must never corrupt the editor image.

---

# 20. Problem D — Export Reliability

The export flow must reliably export the **current editor result**, not accidentally export an old source image.

## Required

Before export:

1. determine the current image state;
2. ensure pending processing is complete;
3. obtain the correct current image/blob;
4. apply requested output settings;
5. generate the downloadable file;
6. trigger download;
7. clean up temporary object URLs safely.

---

# 21. Object URL Safety

Do not revoke an object URL too early.

Unsafe pattern:

```text
createObjectURL()
→ click download
→ immediately revoke
```

Use a safe lifecycle that gives the browser enough time to initiate the download before cleanup.

Always clean up temporary URLs to prevent memory leaks.

---

# 22. Export Formats

Preserve currently supported formats.

If format/quality controls exist, ensure:

- JPEG quality is applied correctly;
- PNG remains lossless;
- WebP works where supported;
- filename extension matches actual output format;
- exported dimensions match the current image state.

Do not silently change output format.

---

# 23. Problem E — Placeholder / Empty Tool Rail Sections

If the current Tool Rail contains sections such as:

```text
Recent
Favorites
```

but they return empty placeholder content, do not leave broken-looking UI.

Choose one of:

### Option A — Implement

If the product intends to support Recent/Favorites, implement them properly.

### Option B — Hide Until Ready

If they are not yet functional, do not display misleading empty headings.

Do not remove actual registered tools.

---

# 24. Problem F — Inspector Placeholder States

Inspect the current Editor Inspector for:

- “Coming soon” controls;
- fake controls;
- non-functional buttons;
- hardcoded values;
- mock operation behavior.

For each:

1. identify whether it is expected production functionality;
2. if functional, connect it to real editor state;
3. if not yet supported, clearly label it as unavailable or hide the control until implemented.

Never make a button appear functional when it does nothing.

---

# 25. Tool Registry Integrity

The central tool registry remains the source of truth.

Do not duplicate tool definitions in:

- Tool Rail;
- search;
- inspector;
- routing;
- permissions;
- recent tools.

The UI should consume registry metadata.

Recommended conceptual structure:

```text
centralToolRegistry
        ↓
Tool Discovery
        ↓
Tool Rail
        ↓
Selected Tool
        ↓
Inspector
        ↓
Operation Engine
```

---

# 26. Tool/Inspector Consistency

For every registered tool:

```text
Tool exists
↓
Tool can be discovered
↓
Tool can be selected
↓
Correct inspector opens
↓
Inputs are validated
↓
Operation executes
↓
Result is applied
↓
History updates
↓
Export works
```

If a tool cannot complete this flow, document its current state rather than silently pretending it is production-ready.

---

# 27. Error Handling

Errors must be normalized.

The frontend should not assume only one backend response shape.

Support meaningful extraction from:

```text
error.message
error.detail
response.data.message
response.data.error
```

or the actual response contract used by the project.

Never show:

```text
undefined
[object Object]
Network Error
```

when a useful user-facing message is available.

---

# 28. Image Loading Safety

When replacing the current image:

- handle image load errors;
- handle broken URLs;
- revoke temporary URLs appropriately;
- avoid replacing a valid image with an invalid result;
- show loading state while the new image is loading;
- restore the previous image if the new result cannot be loaded.

---

# 29. Canvas Fit Behavior

After a valid result is applied:

```text
result loaded
      ↓
measure canvas
      ↓
calculate fit zoom
      ↓
center image
      ↓
render
```

The image must not appear:

- outside the canvas;
- at 0× zoom;
- at an unusably large scale;
- clipped unexpectedly;
- as a broken image placeholder.

Preserve manual zoom/pan behavior after the initial fit.

---

# 30. Responsive Behavior

The Tool Rail must remain usable at:

- desktop;
- laptop;
- smaller desktop widths;
- tablet-sized widths where supported.

At narrow widths:

- do not let the Tool Rail cover the canvas;
- do not let the inspector overlap the canvas;
- preserve access to all tools;
- allow the Tool Rail to scroll independently.

---

# 31. Accessibility

Tool Rail must support:

- keyboard focus;
- visible focus state;
- accessible tool names;
- buttons instead of clickable non-semantic containers where appropriate;
- screen-reader labels for icon-only controls;
- locked/pro status where meaningful.

The scrollbar must not be the only way to discover tools.

---

# 32. Performance

Avoid:

- unnecessary rerenders of the entire workspace while scrolling;
- expensive image decoding during Tool Rail scroll;
- recreating tool arrays on every render without need;
- unnecessary polling;
- unreleased object URLs;
- duplicate network requests.

Tool Rail scrolling should remain smooth even with a large registry.

---

# 33. Suggested Component Responsibilities

Inspect the actual project structure first.

Likely areas include:

```text
EditorToolRail
EditorCanvas
EditorContext
useEditorOperation
EditorInspector
ExportDialog
centralToolRegistry
```

Do not assume filenames are unchanged. Locate the current equivalents before editing.

---

# 34. Implementation Order

Implement in this order:

## Phase 1 — Tool Rail

- dedicated vertical scroll;
- preserve all tools;
- preserve search;
- preserve categories;
- preserve active state;
- preserve locked state;
- add scroll cue;
- responsive behavior.

## Phase 2 — Result Pipeline

- operation IDs;
- stale result protection;
- result validation;
- safe image replacement;
- history correctness;
- polling cleanup.

## Phase 3 — Canvas Positioning

- safe fit-to-canvas;
- centered result;
- no broken/blank result;
- preserve intended zoom/pan UX.

## Phase 4 — Export

- current-result correctness;
- safe object URL lifecycle;
- output format correctness;
- download reliability.

## Phase 5 — Placeholder Cleanup

- Recent/Favorites;
- inspector mock controls;
- misleading empty states.

## Phase 6 — QA

- type check;
- lint;
- unit tests;
- integration tests;
- production build;
- manual visual verification.

---

# 35. Testing Requirements

## Tool Rail

Test:

- 5 tools;
- 15 tools;
- 30+ tools;
- long tool names;
- locked tools;
- active tool near bottom;
- search result near bottom;
- keyboard navigation;
- scrollbar;
- mouse wheel;
- trackpad;
- responsive viewport.

## Result Pipeline

Test:

- successful operation;
- failed operation;
- timeout;
- retry;
- two operations started quickly;
- old result finishing after new result;
- invalid result URL;
- failed image fetch;
- empty result;
- history undo/redo.

## Canvas

Test:

- portrait image;
- landscape image;
- square image;
- very large image;
- very small image;
- transparent PNG;
- AI result;
- repeated operations.

## Export

Test:

- PNG;
- JPEG;
- WebP if supported;
- changed dimensions;
- AI result;
- repeated exports;
- export immediately after operation completion.

---

# 36. Acceptance Criteria

The implementation is complete only when all of the following are true:

### Tool Rail

- [ ] Existing tools are preserved.
- [ ] Existing categories are preserved.
- [ ] Search works.
- [ ] Tool Rail independently scrolls.
- [ ] Canvas does not scroll because Tool Rail content is long.
- [ ] Inspector does not move unexpectedly.
- [ ] Scroll cue communicates additional tools.
- [ ] Active/locked states remain correct.

### Image Result

- [ ] Successful result replaces the current image.
- [ ] Result is centered/fitted correctly.
- [ ] Broken result cannot overwrite a valid image.
- [ ] Stale result cannot overwrite a newer result.
- [ ] History contains valid states.
- [ ] Undo/redo works.

### Operations

- [ ] Loading state is reliable.
- [ ] Success state is reliable.
- [ ] Error state is reliable.
- [ ] Timeout is handled.
- [ ] Retry is safe.
- [ ] Polling is cleaned up.

### Export

- [ ] Current image is exported.
- [ ] Correct dimensions are exported.
- [ ] Correct format is exported.
- [ ] Download works repeatedly.
- [ ] Temporary object URLs are cleaned safely.

### UI Quality

- [ ] No misleading placeholder controls.
- [ ] No broken empty sections.
- [ ] No layout overflow caused by long tool lists.
- [ ] No console errors introduced.
- [ ] No TypeScript errors introduced.
- [ ] No existing working functionality regresses.

---

# 37. Regression Protection

Before merging:

```text
git diff
git status
typecheck
lint
unit tests
integration tests
production build
```

Also manually verify:

```text
Upload
→ Edit
→ AI operation
→ Result
→ Undo
→ Redo
→ Export
→ New operation
→ Tool Rail scroll
→ Search tool
→ Select locked tool
```

---

# 38. Important Agent Instruction

The implementing AI agent must follow this rule:

> **Inspect first, patch second.**

Before modifying code:

1. Locate the actual current components.
2. Trace image state from upload to canvas.
3. Trace operation submission to result application.
4. Trace history updates.
5. Trace export.
6. Trace Tool Rail rendering and scrolling.
7. Trace registry → Tool Rail → Inspector → operation mapping.
8. Identify tests that already exist.
9. Make the smallest safe patch.

Do not rewrite the workspace based only on this specification.

---

# 39. Final Product Goal

The final Image Editor Workspace should feel like a stable professional editor:

```text
┌─────────────────────────────────────────────────────────────┐
│                     Workspace Header                         │
├───────────────┬─────────────────────────────┬───────────────┤
│ Search        │                             │               │
│               │                             │   Inspector   │
│ Pan           │                             │               │
│ Resize        │                             │               │
│ Crop          │           CANVAS            │               │
│ Rotate        │                             │               │
│────────────── │                             │               │
│ AI Tools      │                             │               │
│ BG Remove     │                             │               │
│ Upscale       │                             │               │
│ Enhance       │                             │               │
│ Object Remove │                             │               │
│ Generate      │                             │               │
│ Expand        │                             │               │
│ ...           │                             │               │
│      ↓ scroll │                             │               │
├───────────────┴─────────────────────────────┴───────────────┤
│                     Status / Output                          │
└─────────────────────────────────────────────────────────────┘
```

The most important principle is:

**Improve and harden the existing editor; do not replace it.**

Existing tools, existing user workflows, existing registry entries, and existing working behavior must survive this upgrade.
