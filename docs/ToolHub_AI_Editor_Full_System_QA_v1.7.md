# ToolHub AI — Editor Full-System QA, Repair & Production Certification
## Version 1.7 — Agent Execution Specification

> **Status:** Mandatory implementation + QA specification  
> **Purpose:** Verify, repair, polish, and certify the ToolHub AI creative editor so that every registered tool is discoverable, functional, exportable, visually consistent, and production-ready.
>
> **Important:** This document is additive. Existing approved documentation remains authoritative unless this document explicitly strengthens a requirement.

---

# 1. Mission

The AI coding agent must treat the current editor as a **professional ToolHub AI application**, not as a collection of simple web tools.

The goal is not merely to make buttons clickable.

A tool is considered complete only when the complete workflow works:

```text
Tool visible
  ↓
Tool opens
  ↓
Inspector renders correctly
  ↓
Input is accepted
  ↓
Operation executes
  ↓
Loading/progress state works
  ↓
Success result is displayed
  ↓
Result preserves required quality/resolution
  ↓
Undo/Redo works where applicable
  ↓
Before/After works where applicable
  ↓
Export/Download works
  ↓
Downloaded file is valid
  ↓
Downloaded file has correct dimensions/quality/format
  ↓
UI remains clean and branded
  ↓
Desktop + mobile + light + dark QA passes
```

**Do not report “Done” until the entire chain has passed.**

---

# 2. Existing Approved Layout — LOCKED

The current approved editor layout must remain.

```text
┌──────────────────────────────────────────────────────────────┐
│                    FOCUSED EDITOR HEADER                     │
├───────────────────────┬───────────────────────────┬──────────┤
│                       │                           │          │
│     TOOL RAIL         │                           │ INSPECTOR│
│     spacious          │          CANVAS           │  LOCKED  │
│     branded           │       visual priority     │  DESIGN  │
│                       │                           │          │
├───────────────────────┴───────────────────────────┴──────────┤
│                    STATUS / ZOOM / PROGRESS                  │
└──────────────────────────────────────────────────────────────┘
```

## Preserve

- focused editor header
- current canvas position
- canvas visual priority
- current right Inspector design
- ToolHub AI brand
- current typography
- current spacing system
- current colors
- current radius/shadow system
- current icon language
- current theme system

## Improve only where required

- left Tool Rail usability
- tool discoverability
- search
- category organization
- independent scrolling
- responsive behavior
- broken controls
- broken dropdowns
- error handling
- loading states
- export reliability
- output quality
- accessibility
- performance

## Never do

- redesign the right Inspector
- add a second application navigation bar
- copy Canva/Adobe/PhotoRoom UI
- hide existing tools behind “More Tools”
- remove tools to make the sidebar look cleaner
- replace the Tool Registry with a smaller hard-coded list
- trade functionality for visual cleanliness

---

# 3. Protected Tool Inventory

The following tools are explicitly protected:

1. Pan
2. Resize
3. Crop
4. Rotate
5. Background Remove
6. Passport
7. Upscale
8. Enhance
9. Object Remove
10. Social
11. Product
12. Mockup
13. Watermark
14. Compress

**Important:** This is not necessarily the complete inventory.

The agent MUST inspect the actual Tool Registry/codebase and create a complete inventory of every registered/implemented tool.

### Rule

```text
Registry tools >= currently visible tools
```

Never allow a UI refactor to reduce the registered tool count.

If additional tools exist in the registry, they must also be tested.

---

# 4. Tool Registry — Single Source of Truth

The Tool Registry must be authoritative.

The editor must not maintain a separate reduced hard-coded catalog.

Every tool definition should contain, where applicable:

```text
id
displayName
icon
category
route
editorRoute
capability
availability
pricing/premium state
status
ordering
search metadata
aliases
supported input types
supported output types
supported editor contexts
compatible next tools
feature flag
analytics identifier
```

Required architecture:

```text
                  TOOL REGISTRY
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    Tool Rail       Search        Mega Menu
        │              │              │
        └──────────────┼──────────────┘
                       │
                Tools Directory
                       │
                 Category Pages
```

If the registry contains tools but the UI says:

```text
No tools found
```

the agent must fix the registry → UI integration.

Do not solve the problem by creating a smaller replacement list.

---

# 5. Immediate Problems Visible in Current Screenshots

The supplied screenshots show several concrete issues that must be treated as defects.

## P0 — AI Processing Failure

Visible error:

```text
Processing Failed
Unexpected token '|', "Internal S"... is not valid JSON
```

This strongly indicates that at least one client path is attempting to parse a non-JSON response as JSON.

### Required repair

The frontend/backend contract must be made robust.

The client must:

1. inspect HTTP status;
2. inspect `Content-Type`;
3. parse JSON only when appropriate;
4. safely handle text/plain responses;
5. safely handle HTML/proxy/server error responses;
6. preserve the raw server message for diagnostics;
7. show a human-readable UI error;
8. provide Retry;
9. never lose the current image/project state.

Preferred UI:

```text
We couldn't process this image right now.

[ Try Again ]

View technical details
```

Never expose raw parser errors as the primary user message.

---

## P0 — Export/Download Reliability

Every tool that creates an output must be able to:

- produce a valid result;
- preview the result;
- export the result;
- download the result;
- reopen the downloaded result where appropriate;
- preserve expected dimensions;
- preserve expected format;
- preserve transparency where applicable;
- preserve expected quality.

A successful UI notification without a valid downloaded file is a failure.

---

## P1 — Inspector Dropdown Layout

The screenshots show dropdown content in tools such as Passport and Social extending/clipping around the Inspector boundary.

### Required repair

All select/dropdown controls must:

- fit the Inspector;
- never be clipped;
- never create horizontal overflow;
- remain readable;
- support keyboard navigation;
- have a visible selected state;
- work at 100% browser zoom;
- work at reduced viewport widths;
- use a portal/popover strategy when necessary;
- remain visually native to ToolHub AI.

Do not increase the right Inspector width simply to hide this problem.

---

## P1 — Tool Panel Visual Consistency

All tool panels must use the same ToolHub AI component primitives.

Check:

- title
- description
- icon
- AI badge
- premium badge
- labels
- inputs
- selects
- sliders
- buttons
- helper text
- cost information
- loading state
- success state
- error state

No individual tool may look like a separate product.

---

## P1 — “Share Coming Soon”

If Share is not implemented:

- do not make it look like a broken control;
- clearly mark it as planned/coming soon;
- do not allow an action that fails silently.

If the feature is already intended to be functional, implement and test it.

---

# 6. Complete Tool Discovery Audit

Before changing code, the agent must inspect:

- Tool Registry
- tool configuration
- tool routes
- editor routes
- feature flags
- entitlement logic
- tool handlers
- backend endpoints
- API clients
- export utilities
- history system
- canvas state
- file processing pipeline

Then generate an internal table:

| Tool | Registry | Visible | Opens | Backend | Success | Undo | Export | Download | Quality | UI |
|---|---|---|---|---|---|---|---|---|---|---|
| Pan | | | | N/A | | | | | | |
| Resize | | | | | | | | | | |
| Crop | | | | | | | | | | |
| Rotate | | | | | | | | | | |
| Background Remove | | | | | | | | | | |
| Passport | | | | | | | | | | |
| Upscale | | | | | | | | | | |
| Enhance | | | | | | | | | | |
| Object Remove | | | | | | | | | | |
| Social | | | | | | | | | | |
| Product | | | | | | | | | | |
| Mockup | | | | | | | | | | |
| Watermark | | | | | | | | | | |
| Compress | | | | | | | | | | |

Add every additional registry tool to this matrix.

---

# 7. Tool-by-Tool Functional QA

Every tool must be tested individually.

## 7.1 Pan

Verify:

- mouse drag
- Space + drag where supported
- middle mouse where supported
- cursor feedback
- no accidental image modification
- zoom compatibility

## 7.2 Resize

Verify:

- current width/height shown correctly
- width/height calculations
- aspect-ratio lock
- free resize
- preset sizes
- preview
- no accidental quality degradation beyond expected processing
- export dimensions exactly match selected dimensions

## 7.3 Crop

Verify:

- free crop
- aspect presets
- custom ratio
- drag handles
- move crop region
- numeric X/Y/width/height where supported
- reset
- cancel
- apply
- undo
- export

The crop rectangle must never exceed valid image bounds.

## 7.4 Rotate

Verify:

- 90° clockwise
- 90° counter-clockwise
- custom angle if supported
- flip if supported
- preview
- dimensions after rotation
- transparent/canvas handling
- undo
- export

## 7.5 Background Remove

Verify:

- image upload
- AI request
- processing state
- result
- transparent background
- replacement/background options where implemented
- before/after
- retry
- undo
- export PNG
- transparency survives download

## 7.6 Passport

Verify every supported country/preset.

At minimum test:

- Bangladesh Passport
- USA Passport
- UK Passport
- Schengen Visa
- India OCI/Visa

Verify:

- preset selection
- dimensions
- crop ratio
- background handling
- face positioning
- output size
- export
- download

No dropdown clipping.

## 7.7 Upscale

Verify:

- input image
- upscale action
- processing state
- success
- output dimensions
- output quality
- no unexpected downscaling
- before/after
- retry
- export
- download

If the selected multiplier is 2×:

```text
outputWidth = inputWidth × 2
outputHeight = inputHeight × 2
```

unless the product specification explicitly defines another behavior.

## 7.8 Enhance

Verify:

- enhancement controls
- preview
- before/after
- processing
- success
- undo
- export
- output quality

## 7.9 Object Remove

Verify:

- object selection
- mask/selection visibility
- process
- result
- retry
- undo
- before/after
- export

## 7.10 Social

Verify all presets.

At minimum:

- Instagram Square
- Instagram Portrait
- Instagram Story
- Facebook Post
- X/Twitter Post
- LinkedIn Post

Verify exact target dimensions.

No clipped dropdown options.

## 7.11 Product

Verify every product preset currently registered.

Check:

- product image input
- background workflow
- composition
- output dimensions
- export
- download

## 7.12 Mockup

Verify:

- template selection
- image placement
- scaling
- positioning
- preview
- export
- downloaded output

## 7.13 Watermark

Verify:

- text/image watermark
- position
- opacity
- size
- repeat/tile where supported
- preview
- undo
- export

## 7.14 Compress

Verify:

- compression quality
- output size
- image dimensions
- format
- visual quality
- download
- no accidental resolution reduction

Compression must reduce file size without unexpectedly changing dimensions unless the user explicitly selects resize.

---

# 8. Resolution & Quality Integrity — CRITICAL

This is a mandatory certification area.

The system must distinguish:

```text
Preview resolution
≠
Source resolution
≠
Export resolution
```

A low-resolution preview must never silently become the exported image.

## Required test

For each suitable tool:

```text
Input:
2000 × 1200

Perform operation

Export

Verify:
expected output width
expected output height
actual downloaded width
actual downloaded height
```

Record:

```text
input dimensions
preview dimensions
processing dimensions
output dimensions
file size
format
quality setting
```

## Rules

### Crop

Expected dimensions must match the selected crop.

### Resize

Expected dimensions must exactly match user selection.

### Rotate

Dimensions must correctly reflect rotation/canvas behavior.

### Upscale

Output dimensions must reflect the requested upscale factor.

### Enhance

Must not silently reduce dimensions unless documented.

### Background Remove

Must preserve original dimensions unless the tool specification says otherwise.

### Social

Must output the selected preset dimensions.

### Passport

Must output the documented physical/pixel dimensions.

### Compress

Must not reduce dimensions unless resize is explicitly selected.

---

# 9. Download Verification

For every export-capable tool:

1. click Export;
2. wait for completion;
3. verify browser download;
4. verify file exists;
5. verify filename;
6. verify extension;
7. verify MIME type;
8. verify file can be opened;
9. verify dimensions;
10. verify transparency where applicable;
11. verify no corruption;
12. verify output matches preview.

Do not accept:

```text
UI says Exported
```

as proof.

The actual downloaded file must be inspected.

---

# 10. Export Matrix

Minimum export coverage:

| Format | Test |
|---|---|
| PNG | valid image + transparency |
| JPG/JPEG | valid image + quality |
| WebP | valid image + quality |
| AVIF | only if implemented |
| SVG | only for compatible vector content |

For each format test:

- dimensions
- file integrity
- quality
- transparency behavior
- metadata behavior
- filename
- download

---

# 11. Before / After

AI and enhancement tools should provide a reliable comparison where appropriate.

Supported interaction may include:

- before/after toggle
- press/hold
- split slider
- side-by-side

Rules:

- original must remain recoverable;
- preview comparison must not overwrite the source;
- comparison must not create accidental history entries;
- comparison must not alter export dimensions.

---

# 12. Undo / Redo & History

Every major reversible editing action must integrate with history.

Test:

```text
Original
 ↓
Edit A
 ↓
Edit B
 ↓
Undo → A
 ↓
Undo → Original
 ↓
Redo → A
 ↓
Redo → B
```

Verify:

- crop
- resize
- rotate
- watermark
- AI operations
- object removal
- enhancement
- background removal
- other registered reversible tools

Where an operation cannot be reversed technically, the UI must clearly communicate that behavior.

---

# 13. Error Handling

All tools require:

```text
Idle
Loading
Success
Error
Retry
```

Errors must be human-readable.

Bad:

```text
Unexpected token '|'
Internal Server Error
JSON parse error
```

Good:

```text
We couldn't process this image right now.

[ Try Again ]

View details
```

Technical details may expose:

- request ID
- HTTP status
- safe server message
- operation ID

Never expose secrets, API keys, stack traces, tokens, or internal credentials.

---

# 14. API Response Safety

Every API client must safely handle:

- JSON success
- JSON error
- text error
- HTML error
- empty response
- malformed JSON
- 400
- 401
- 403
- 404
- 409
- 413
- 422
- 429
- 500
- 502
- 503
- timeout
- network failure

Do not blindly run:

```js
response.json()
```

when the response contract does not guarantee JSON.

Centralize response/error parsing instead of implementing different parsing logic in every tool.

---

# 15. Loading & Processing UX

AI processing must not freeze the entire editor unnecessarily.

Show:

```text
Processing...
```

or an appropriate contextual progress state.

Where useful:

- estimated progress
- current processing step
- cancel
- retry
- remaining credits
- operation cost

The canvas should remain usable when technically safe.

---

# 16. Credit / Premium UX

For AI tools:

- show estimated cost before processing;
- clearly indicate premium tools;
- never charge twice because of a retry;
- prevent duplicate submissions;
- show insufficient-credit state clearly;
- preserve the current project if the operation fails.

Example:

```text
Upscale
AI image upscaling

Estimated cost: 2 AI Credits

[ Upscale Image ]
```

After completion:

```text
2 credits used
Operation complete
```

---

# 17. Duplicate Submission Protection

Double-clicking an AI action must not create duplicate jobs.

During processing:

- disable or safely lock the action;
- show processing state;
- ignore duplicate submissions;
- restore the control after success/failure.

Retry must create a new attempt only when appropriate.

---

# 18. File Safety

Verify:

- unsupported file types are rejected gracefully;
- oversized files show a useful message;
- corrupted files do not crash the editor;
- zero-byte files are handled;
- unusual filenames work;
- Unicode filenames work;
- large images do not freeze the browser;
- temporary files are cleaned up according to the storage policy.

---

# 19. Visual QA — ToolHub AI Brand

Every tool must look native to ToolHub AI.

Check:

- typography
- spacing
- icons
- buttons
- borders
- radius
- shadows
- badges
- labels
- helper text
- empty states
- loading states
- error states
- success states

No random one-off CSS.

Use the existing design tokens and reusable components.

---

# 20. Right Inspector — LOCKED

Do not redesign the Inspector.

Only fix defects required for functionality, such as:

- clipping
- overflow
- inaccessible controls
- broken dropdowns
- broken responsive behavior

The Inspector must remain visually consistent with the approved design.

---

# 21. Left Tool Rail

The Tool Rail must be scalable.

Recommended desktop width:

```text
Minimum: 220px
Default: 250px
Maximum: 320px
```

Required:

- internal scrolling
- search
- categories
- readable labels
- active state
- hover state
- focus state
- premium/AI indicators
- tool count scalability
- no disappearing tools
- no accidental horizontal overflow

The canvas remains visually dominant.

---

# 22. Tool Search

Search must use the Tool Registry.

Search should support:

- exact tool name
- partial name
- aliases
- category
- keywords

Examples:

```text
remove bg
→ Background Remove

make bigger
→ Upscale

passport
→ Passport

instagram
→ Social
```

`No tools found` is valid only when there are genuinely zero results.

---

# 23. Tool Rail Scrolling

When the number of tools grows:

- Tool Rail scrolls independently;
- Canvas remains stable;
- Inspector remains stable;
- header remains stable;
- page itself should not become the only scroll container.

Test with:

```text
15 tools
25 tools
50 tools
100 tools
```

The architecture must remain usable.

---

# 24. Responsive QA

Test at minimum:

```text
1920×1080
1440×900
1280×800
1024×768
768×1024
390×844
375×812
```

Mobile must be intentionally designed.

Do not simply squeeze desktop UI into mobile.

Where applicable:

```text
Header
Canvas
Horizontal Tool Rail / Tool Drawer
Bottom Sheet Inspector
```

---

# 25. Theme QA

Test:

- Light mode
- Dark mode

Verify:

- contrast
- disabled states
- borders
- icons
- text
- canvas controls
- selected states
- dropdowns
- error messages
- premium badges

No hard-coded colors that break themes.

---

# 26. Accessibility QA

Every control must have:

- accessible name
- keyboard behavior
- focus state
- disabled state
- loading state
- error state

Icon-only controls require:

- tooltip
- accessible label

Keyboard tests:

- Tab
- Shift+Tab
- Enter
- Space
- Escape
- Arrow keys for selects/sliders
- editor shortcuts

Focus must never disappear inside dropdowns or dialogs.

---

# 27. Performance QA

Measure:

- editor initial load
- image load
- tool switching
- canvas zoom
- canvas pan
- crop dragging
- inspector updates
- dropdown opening
- AI request start
- AI result display
- export
- download

Avoid:

- unnecessary full-editor rerenders;
- huge image data in React state where avoidable;
- synchronous heavy processing on the main thread;
- duplicate API calls.

Use:

- memoization where useful;
- debouncing;
- workers for suitable client-side work;
- async server jobs for heavy AI;
- preview-resolution processing followed by correct final-resolution export.

---

# 28. Large Image QA

Test with:

```text
800×600
1920×1080
4000×3000
6000×4000
very large supported image
```

Verify:

- upload succeeds;
- preview loads;
- editor remains responsive;
- tools operate;
- memory does not grow uncontrollably;
- export succeeds;
- output dimensions remain correct.

A preview may be downsampled for performance.

The final export must not accidentally use that preview bitmap.

---

# 29. Cross-Tool Workflow QA

Test realistic workflows:

### Workflow A

```text
Upload
→ Crop
→ Resize
→ Enhance
→ Export
```

### Workflow B

```text
Upload
→ Background Remove
→ Watermark
→ Export PNG
```

### Workflow C

```text
Upload
→ Upscale
→ Social preset
→ Export
```

### Workflow D

```text
Upload
→ Object Remove
→ Enhance
→ Export
```

### Workflow E

```text
Upload
→ Passport
→ Export
```

Verify that each operation feeds the next operation correctly.

---

# 30. Regression Protection

Before and after every major refactor, compare:

- tool count
- registry count
- routes
- editor routes
- export routes
- API endpoints
- history behavior
- tool visibility
- premium states

A refactor is rejected if an existing capability disappears without an explicitly approved deprecation.

---

# 31. Automated Testing

The agent should add or repair tests for:

## Unit

- crop coordinate calculations
- resize calculations
- aspect ratio calculations
- rotation dimensions
- export dimension calculations
- quality settings
- entitlement states
- history operations
- API response parsing

## Integration

- upload → edit → export
- AI processing → result
- AI processing → failure → retry
- tool switching
- undo/redo
- project recovery
- download

## E2E

At minimum:

```text
Open editor
Upload image
Select every registered tool
Run representative operation
Verify success/error states
Export
Verify download
Verify output dimensions
```

---

# 32. Visual Regression

Capture visual snapshots for:

- empty editor
- uploaded image
- Pan
- Crop
- Resize
- Passport
- Upscale
- Enhance
- Object Remove
- Social
- Product
- Mockup
- Watermark
- Compress
- processing
- success
- error
- dropdown open
- large tool list
- long tool names
- mobile
- light mode
- dark mode

No unrelated visual regression may be accepted.

---

# 33. Console / Network QA

Before certification:

- no unexpected console errors;
- no repeated failed requests;
- no unhandled promise rejections;
- no JSON parse errors;
- no CORS failures;
- no 404 tool assets;
- no broken image requests;
- no duplicate AI jobs;
- no failed export requests.

Network failures must be handled gracefully.

---

# 34. Security QA

Verify:

- users cannot bypass entitlement checks;
- premium operations are authorized server-side;
- download URLs are protected appropriately;
- user files cannot be accessed by another user;
- unsafe filenames are sanitized;
- API errors do not expose secrets;
- server stack traces are not exposed;
- client-side credit display cannot be trusted for billing.

---

# 35. Billing / Credit Safety

For paid AI operations:

```text
Request created
→ Job idempotency
→ Processing
→ Successful result
→ One charge
```

Failure must not create unintended duplicate charges.

Retry must be idempotent where appropriate.

---

# 36. Export Integrity Certification

For every tested output, record:

```text
Tool:
Input file:
Input format:
Input dimensions:
Operation:
Expected dimensions:
Actual dimensions:
Expected format:
Actual format:
Expected transparency:
Actual transparency:
Quality:
File size:
Download successful:
File opens:
Result visually correct:
PASS / FAIL
```

A single unexpected resolution reduction is a **FAIL** until explained and approved.

---

# 37. Known Screenshot Defect Checklist

The agent must specifically verify and repair:

- [ ] JSON parsing failure
- [ ] raw internal error shown to user
- [ ] Retry behavior
- [ ] Passport dropdown clipping
- [ ] Social dropdown clipping
- [ ] inspector overflow
- [ ] tool panel spacing
- [ ] inconsistent controls
- [ ] output/download verification
- [ ] quality/resolution integrity
- [ ] all tool visibility
- [ ] tool search
- [ ] tool rail scrolling
- [ ] no broken “No tools found”
- [ ] no accidental missing tools
- [ ] Share state is honest and consistent

---

# 38. Definition of Done

A tool is **NOT DONE** when:

- the endpoint works;
- the button appears;
- a spinner appears;
- a result appears in memory;
- the UI looks good.

A tool is DONE only when:

```text
Tool definition
→ Tool Rail
→ Inspector
→ Input
→ Operation
→ Loading
→ Error
→ Success
→ History
→ Undo/Redo
→ Before/After where applicable
→ Export
→ Download
→ Output integrity
→ Desktop QA
→ Mobile QA
→ Theme QA
→ Accessibility QA
→ Performance QA
→ Visual QA
```

---

# 39. Production Certification Gate

The AI agent MUST NOT report:

> Done / Complete / Production Ready

unless all applicable checks are passing.

Final gate:

- [ ] Tool Registry verified
- [ ] Complete tool inventory verified
- [ ] No tool count regression
- [ ] All protected tools visible
- [ ] All registered tools discoverable
- [ ] Tool search works
- [ ] Tool Rail scroll works
- [ ] Right Inspector preserved
- [ ] Canvas remains dominant
- [ ] Every tool opens
- [ ] Every tool's controls work
- [ ] Every backend operation works
- [ ] Loading states work
- [ ] Error states work
- [ ] Retry works
- [ ] No JSON parse failures
- [ ] No unhandled API response format failures
- [ ] Undo/Redo works
- [ ] Before/After works where applicable
- [ ] Export works
- [ ] Download works
- [ ] Downloaded files open
- [ ] Dimensions verified
- [ ] Resolution preserved where required
- [ ] Quality verified
- [ ] Transparency verified where applicable
- [ ] PNG verified
- [ ] JPG/JPEG verified
- [ ] WebP verified
- [ ] AVIF verified if implemented
- [ ] Premium/credit logic verified
- [ ] Duplicate submission prevented
- [ ] Large images tested
- [ ] Desktop QA passed
- [ ] Mobile QA passed
- [ ] Light mode passed
- [ ] Dark mode passed
- [ ] Accessibility passed
- [ ] Performance passed
- [ ] Security checks passed
- [ ] Console clean
- [ ] Network failures handled
- [ ] Visual regression passed
- [ ] ToolHub AI branding consistent
- [ ] No competitor UI copied
- [ ] No duplicate architecture introduced
- [ ] Documentation matches implementation

---

# 40. Failure Policy

If any mandatory check fails:

```text
DO NOT declare complete.
```

Instead report:

```text
FAILED
Tool:
Stage:
Expected:
Actual:
Root cause:
Fix:
Retest required:
```

After the fix, rerun the affected test and all dependent regression tests.

---

# 41. Required Agent Workflow

The AI coding agent must follow this order:

## Phase 1 — Inspect

Do not modify UI immediately.

Inspect:

- registry
- components
- routes
- handlers
- API clients
- backend endpoints
- state/history
- export
- file processing
- design tokens
- tests

## Phase 2 — Inventory

Produce the complete tool list.

Compare:

```text
Registry
vs
Tool Rail
vs
Routes
vs
Implemented handlers
```

## Phase 3 — Repair P0/P1 defects

Fix:

1. processing/API response failures;
2. export/download failures;
3. resolution/quality issues;
4. broken dropdowns/overflow;
5. missing tools;
6. broken registry integration.

## Phase 4 — Functional QA

Run the complete tool matrix.

## Phase 5 — Visual QA

Polish every tool panel using shared ToolHub AI components.

## Phase 6 — Regression QA

Run:

- desktop
- mobile
- light
- dark
- accessibility
- performance
- visual regression
- console/network checks

## Phase 7 — Certification

Only after all mandatory gates pass, produce the final QA report.

---

# 42. Final Product Standard

ToolHub AI should feel like:

> **A professional creative application with AI-powered editing, not a website containing a list of image tools.**

The product priorities are:

```text
Reliability
    ↓
Output correctness
    ↓
Usability
    ↓
Visual quality
    ↓
Performance
    ↓
Feature depth
```

A beautiful UI with broken tools is unacceptable.

A technically correct tool with poor UX is also unacceptable.

The final standard is:

```text
ToolHub AI Brand
+
Approved Current Layout
+
Complete Tool Registry
+
All Existing Tools Preserved
+
Professional Tool Rail
+
Stable Right Inspector
+
Canvas-First Workspace
+
Reliable AI Processing
+
Correct Resolution
+
Correct Export
+
Verified Download
+
Undo / Redo
+
Before / After
+
Autosave / Recovery
+
Accessibility
+
Performance
+
Security
+
Cross-Tool Workflows
+
Production QA
```

## Golden Rule

> **Restore first. Verify second. Repair third. Polish fourth. Expand fifth. Certify last.**

Never sacrifice an existing working capability for a cleaner-looking interface.

