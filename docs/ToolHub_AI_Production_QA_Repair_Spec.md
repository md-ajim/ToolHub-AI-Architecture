# ToolHub AI Image Editor — Production QA & Repair Specification

## Status

**Production certification: BLOCKED**

The supplied QA screenshots show that the editor UI/layout is present, but the implementation is not yet production-ready. The repair must be completed before calling the system finished.

## Product requirement

Keep the current ToolHub AI editor layout and overall interaction model.

Do **not** replace the editor with a new architecture or redesign the main layout.

The goal is:

- Every visible tool must actually work.
- Every operation must produce the correct result.
- Results must be downloadable.
- Output dimensions and quality must be preserved according to the selected operation.
- Tool state, loading, success, failure, retry, undo/redo and before/after behavior must be reliable.
- The UI must remain clean, consistent and branded as ToolHub AI.
- Broken/placeholder controls and visually broken panels must be fixed.
- No fake success, mock backend, "coming soon" behavior or silent fallback is acceptable for a production tool.

---

# 1. Critical blockers found in QA

The screenshots explicitly show the following blockers.

### 1.1 AI tools are non-functional

The QA report identifies these five tools as broken/mock:

1. Background Remove
2. Passport
3. Upscale
4. Enhance
5. Object Remove

They currently return the original image / fail the intended job contract.

**Required:** Each tool must execute its real operation, return the processed image, update the editor state, and make the result available to export/download.

---

### 1.2 Product and Mockup are placeholders

The QA report says:

- Product — toast only
- Mockup — toast only

**Required:** They must open real tool panels and perform their documented operations. No placeholder-only behavior.

---

### 1.3 Export / Download is broken

The QA report identifies:

- Export is effectively a facade.
- Edited images cannot be exported/downloaded correctly.
- Download fails for edited images because of a cross-origin `<a>` problem.
- Export does not correctly apply format/quality.
- Downloaded files do not reliably open.

**Required:**

- Export the current editor result, not the original source file.
- Download the exact current result.
- Support the selected output format correctly.
- Apply quality settings correctly.
- Never silently change the requested format.
- Generated files must open successfully in standard viewers.
- Object URLs / blobs must be handled correctly and revoked after use.
- Do not depend on cross-origin anchor behavior for edited images.

---

### 1.4 Operation chaining is broken

The QA report says:

> crop → resize → enhance workflows are broken

**Required:** Operations must be composable.

Example:

`Original → Crop → Resize → Enhance → Export`

The final output must contain every preceding operation.

Each operation must use the current editor image/state, not revert to the original source.

---

### 1.5 Result application is broken

The QA report notes that `applyResult` receives a URL and does not correctly convert/use it, causing operations to fall back to the original file.

**Required result contract:**

Every operation must return a normalized result such as:

- Blob/File
- object URL
- image bitmap/canvas result

The frontend must convert the backend result into the editor's canonical image representation before updating state.

Never replace a processed result with the original image because a result URL was not parsed.

---

# 2. JSON/API error handling

The screenshots show this recurring error:

`Unexpected token 'I', "Internal S"... is not valid JSON`

This means the client is attempting to parse a non-JSON backend response as JSON.

**Required:**

Implement one safe API response parser.

It must:

1. Read the response content type.
2. Parse JSON only when the response is JSON.
3. Otherwise read text safely.
4. Convert backend errors into a normalized frontend error object.
5. Never throw a secondary JSON parse error that hides the real backend error.
6. Never expose raw internal backend errors directly to users.

Recommended normalized error shape:

```ts
type ToolError = {
  code: string;
  message: string;
  retryable: boolean;
  status?: number;
};
```

User-facing messages must be concise and actionable.

---

# 3. Loading and error state correctness

The QA report identifies:

- interval leak on failure
- raw backend errors reaching the client
- manual retry only
- loading/error state issues

**Required:**

For every tool:

`idle → loading → success | error`

On success:

- stop polling
- clear timers
- show result
- enable export/download

On failure:

- stop timers
- clear loading state
- show normalized error
- preserve the source/current image
- allow retry

No timer, interval, event listener or subscription may remain active after completion/failure/unmount.

---

# 4. Undo / Redo

QA reports a stale-closure bug.

**Required:**

- Undo must restore the exact previous editor state.
- Redo must restore the exact next state.
- New edits after undo must correctly clear the redo branch.
- No stale React state/closure may corrupt history.
- History must include operation parameters when necessary.
- Failed operations must not create fake history entries.

Test at minimum:

1. Original
2. Crop
3. Resize
4. Undo
5. Redo
6. Enhance
7. Undo
8. New crop
9. Redo must be unavailable after the new branch

---

# 5. Image quality and dimensions

The QA screenshots show failures for:

- resolution preservation
- quality verification
- PNG/JPEG/WebP/AVIF verification
- large-image testing
- operation chaining
- transparency

**Required invariant:**

No operation may unexpectedly reduce resolution or quality.

For every operation record:

- input width
- input height
- output width
- output height
- input MIME
- output MIME
- quality setting
- alpha/transparency state

### Resize

- Respect requested width/height.
- Respect aspect-ratio lock.
- Do not unexpectedly upscale/downscale.
- Do not distort the image unless the user explicitly requests distortion.

### Crop

- Output dimensions must match the selected crop.
- Aspect presets must be exact.
- Freeform crop must preserve the selected rectangle.
- EXIF orientation must be normalized before crop calculations.

### Rotation

- Correctly rotate the bitmap.
- Update dimensions when rotation changes orientation.
- Preserve quality and transparency.

---

# 6. Format correctness

The system must support its documented formats without silent conversion.

Minimum verification:

- PNG
- JPEG/JPG
- WebP
- AVIF (only if actually implemented)

For each format:

1. Export.
2. Download.
3. Re-open the file.
4. Verify MIME/type.
5. Verify width/height.
6. Verify pixel content.
7. Verify transparency where applicable.

### Transparency

PNG/WebP/AVIF must preserve alpha where supported.

JPEG cannot preserve alpha and must use an intentional background conversion.

Never silently strip transparency from a format that supports it.

---

# 7. EXIF / orientation

The QA report specifically notes that EXIF orientation handling is not complete.

**Required:**

Normalize orientation before editing so that:

- preview orientation
- crop coordinates
- resize dimensions
- rotation
- exported pixels

all agree.

Test portrait photos from phones/cameras with EXIF orientation metadata.

---

# 8. AI tool contracts

Every AI tool must follow the same lifecycle:

```text
Select tool
→ validate input
→ submit job
→ show loading
→ poll/receive result
→ validate result
→ apply result
→ update history
→ enable before/after
→ enable export/download
```

Each AI tool must be tested independently.

### Background Remove

Expected:

- foreground retained
- background removed
- alpha preserved
- transparent export works

### Passport

Expected:

- selected country/document preset is applied
- correct crop/aspect is produced
- background processing is real
- output can be downloaded

### Upscale

Expected:

- output resolution actually increases according to the selected scale
- result is not the original image
- dimensions are verified after completion

### Enhance

Expected:

- actual enhancement result
- output is not a byte-identical copy of the original unless the operation explicitly determines no change
- dimensions preserved unless documented otherwise

### Object Remove

Expected:

- selected object/region is removed
- surrounding pixels are reconstructed
- result can be exported/downloaded

---

# 9. Basic tools

At minimum verify:

- Pan
- Resize
- Crop
- Rotate

Each must:

- open correctly
- show correct controls
- update preview
- apply correctly
- preserve history
- support undo/redo
- export/download correctly

The QA report notes a hook bug in basic tools. Fix state/hook dependencies so controls always reflect current editor state.

---

# 10. Product / Mockup / Social / Watermark / Compress

These tools must not be decorative UI.

Each must have:

- working controls
- validation
- real operation
- loading state where needed
- result application
- history integration
- export/download support

Social presets must produce the exact requested dimensions.

Watermark must apply the requested watermark parameters.

Compress must actually reduce file size according to the selected compression settings while preserving the intended visual quality.

---

# 11. Export pipeline

Create one canonical export pipeline used by every tool.

```text
EditorState
→ render current state
→ encode requested format
→ apply quality
→ create Blob
→ validate Blob
→ download/save
```

The export pipeline must never read the original source file directly when edits exist.

Before download, validate:

- Blob exists
- MIME matches requested format
- Blob size > 0
- decoded image is valid
- width/height match current editor state

---

# 12. Before / After

Where applicable:

- Before = image immediately before the selected operation.
- After = exact result of the operation.

The comparison must never accidentally show the original source when multiple operations have already been applied.

---

# 13. UI / visual QA

Keep the current layout.

Fix all visual breakage visible in the supplied screenshots:

- overlapping text
- clipped dropdown labels
- controls extending outside panels
- inconsistent spacing
- broken/hidden labels
- broken right inspector layouts
- awkward empty states
- toast/modal collisions
- inconsistent button sizing
- inconsistent typography
- incorrect disabled/loading states

The screenshots show that some tool panels are visibly broken while dropdowns are open and text is clipped.

**Required:** Every panel must remain visually stable at normal desktop width and during interaction.

---

# 14. Tool rail

The tool rail is a core product surface.

Requirements:

- All registered tools visible.
- No tool-count regression.
- Search works.
- Scrolling works.
- Protected tools remain discoverable.
- Tool names/icons are aligned.
- AI tools are clearly marked.
- Active tool state is obvious.
- No dead entries.
- No placeholder tools unless explicitly documented as disabled.

The QA report currently says **7 tools are broken/placeholder**.

That must become zero.

---

# 15. Theme / accessibility

QA reports:

- dark mode failure due to hardcoded white elements
- accessibility failure
- light/dark only partially tested

Required:

- no hardcoded colors that break themes
- semantic buttons and inputs
- keyboard navigation
- visible focus states
- accessible labels
- correct disabled/loading states
- sufficient contrast
- modal focus handling
- Escape closes dismissible dialogs
- screen-reader-friendly tool names

---

# 16. Security

The QA report identifies backend security concerns:

- PDF tools / AllowAny
- public storage endpoints
- verbose error exposure

**Required before production:**

- authenticated/authorized endpoints where required
- no public access to private generated files
- validate uploaded files
- validate MIME and size
- sanitize filenames
- rate-limit expensive AI operations
- never expose internal stack traces
- never expose secrets
- verify ownership of generated assets
- enforce server-side operation limits

---

# 17. Automated testing

The QA report currently indicates essentially no meaningful frontend test coverage.

Add automated tests for:

### Unit tests

- image state transitions
- export format selection
- dimension calculations
- crop calculations
- resize calculations
- error normalization
- result normalization
- undo/redo reducer/history
- tool registry

### Integration tests

For every tool:

`open → configure → run → result → apply → export`

### Regression tests

At minimum:

1. Crop → Resize → Enhance
2. Resize → Crop → Export
3. Background Remove → PNG Export
4. Upscale → Download
5. Rotate → Crop
6. Enhance → Undo → Redo
7. Multiple operations → Export
8. Transparent PNG → WebP/PNG
9. Large image → operation → export

---

# 18. Visual regression

Add screenshots/visual regression for:

- desktop editor
- mobile editor
- light theme
- dark theme
- tool rail
- right inspector
- modal
- dropdowns
- loading state
- error state
- success state
- before/after
- export dialog

The QA report currently says visual regression is not tested.

---

# 19. Large-image testing

Test at minimum:

- 1920×1080
- 4000×3000
- 6000×4000
- large transparent PNG
- large JPEG

Verify:

- no browser crash
- no uncontrolled memory growth
- correct output dimensions
- reasonable processing time
- correct download
- no corrupted file

---

# 20. Production certification gate

The system is **NOT certified** until all of the following are true:

- [ ] All registered tools work
- [ ] Zero placeholder/dead tools
- [ ] All AI tools use real working backends
- [ ] No mock AI endpoints
- [ ] Export works
- [ ] Download works
- [ ] Downloaded files open
- [ ] Dimensions verified
- [ ] Quality verified
- [ ] PNG verified
- [ ] JPEG/JPG verified
- [ ] WebP verified
- [ ] AVIF verified if implemented
- [ ] Transparency verified
- [ ] EXIF orientation verified
- [ ] Operation chaining verified
- [ ] Undo/redo verified
- [ ] Before/after verified
- [ ] Loading/error/retry verified
- [ ] No timer/interval leaks
- [ ] API response parsing is safe
- [ ] Raw backend errors are hidden
- [ ] Security checks pass
- [ ] Desktop QA passes
- [ ] Mobile QA passes
- [ ] Light theme passes
- [ ] Dark theme passes
- [ ] Accessibility passes
- [ ] Performance passes
- [ ] Large-image tests pass
- [ ] Automated tests pass
- [ ] Visual regression passes
- [ ] Documentation matches implementation

---

# 21. Definition of Done

Do not report "fixed" because a button opens or a toast appears.

A tool is considered **DONE** only when:

1. User opens the tool.
2. User configures it.
3. User executes it.
4. Real processing occurs.
5. Loading state is correct.
6. Result is returned.
7. Result is validated.
8. Result replaces/updates the current editor image correctly.
9. Undo/redo works.
10. Before/after works where applicable.
11. Dimensions are correct.
12. Quality is acceptable.
13. Export uses the processed result.
14. Download succeeds.
15. Downloaded file opens correctly.
16. UI remains visually clean.
17. No console/runtime errors are introduced.
18. Automated regression test exists.

---

# 22. AI Agent execution instruction

Work through the blockers systematically.

**Do not redesign the current editor.**

Use the existing architecture where possible. Repair the contracts between:

- tool registry
- tool UI
- editor state
- operation runner
- backend/API
- result normalization
- history
- export
- download

After each repair:

1. Run the relevant automated tests.
2. Run a real browser interaction test.
3. Verify the resulting image dimensions.
4. Verify the downloaded file.
5. Verify console/network errors.
6. Verify the UI visually.

At the end, run the full production QA matrix again.

**Do not claim 100% complete while any blocker remains.**

The final response from the agent must contain:

- total tools tested
- tools passed
- tools failed
- backend endpoints tested
- export formats tested
- dimensions before/after
- download verification
- automated test result
- visual QA result
- remaining blockers

Production status must be either:

`PRODUCTION READY`

or

`NOT PRODUCTION READY — BLOCKERS REMAIN`

