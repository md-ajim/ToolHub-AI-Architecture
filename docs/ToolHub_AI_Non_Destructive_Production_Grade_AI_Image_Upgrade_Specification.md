# ToolHub AI — Production-Grade AI Image Platform
## Non-Destructive Upgrade & Backward-Compatible Specification

**Purpose:** Upgrade the existing ToolHub AI image editor into a production-grade AI image platform without deleting, hiding, renaming, or breaking existing tools, routes, UI workflows, registry entries, or user functionality.

> **Core rule: This is an additive upgrade, not a rewrite.**

## 1. Existing Product Must Be Preserved

The current Central Tool Registry contains **36 published tools**.

### Image / General Image — 11
- Image Editor
- Image Cropper
- Image Rotator
- Image Watermark
- Image Resizer
- Social Media Resizer
- Image Compressor
- Image Converter
- WebP Converter
- AVIF Converter
- Favicon Generator

### AI Image — 7
- AI Background Remover
- AI Object Remover
- AI Image Enhancer
- AI Image Upscaler
- AI Passport Photo
- Mockup Generator
- Product Image Editor

### Web / Utility — 4
- Link Shortener
- Password Generator
- QR Code Generator
- Resume Builder

### PDF — 6
- PDF Merger
- PDF Compressor
- PDF Splitter
- PDF Rotator
- PDF Protect
- PDF Unlock

### Text — 4
- Word Counter
- Case Converter
- Text Cleaner
- Remove Duplicate Lines

### SEO — 4
- Meta Tag Generator
- Open Graph Generator
- Robots.txt Generator
- Sitemap Generator

**Requirement:** The 36 existing tools must remain available. New tools may be added, but existing tools must not be removed simply because their implementation is upgraded.

---

# 2. Existing Image Editor Must Remain

The current Image Editor Workspace contains 14 operations:

### Existing editing
1. Resize
2. Crop
3. Rotate / Flip
4. Compress
5. Convert
6. Social Media Resize
7. Watermark

### Existing AI processing
8. Background Remove
9. Upscale
10. Enhance
11. Object Remove
12. Passport Photo

### Existing design/product
13. Mockup
14. Product Image Editor

**Do not remove any of these.**

The current canvas, left sidebar, export/download workflow, history controls, zoom, navigation, and existing tool access must remain functional.

The UI may be improved, but functionality must remain backward compatible.

---

# 3. Target Architecture

Use this architecture:

```text
Current Tool Registry
        |
        +-- Existing Utility Tools
        |
        +-- Existing Image Editor
        |      |
        |      +-- Existing operations
        |      +-- New AI capabilities
        |
        +-- Production AI Image Engine
               |
               +-- Provider Adapter Layer
               +-- Async Job / Queue
               +-- Object Storage
               +-- Credits / Billing
               +-- Safety / Moderation
               +-- Monitoring
```

Do not replace the existing editor with a separate application.

---

# 4. Production AI Capabilities

## A. AI Background Removal

Upgrade the existing tool with:
- real subject segmentation
- transparent PNG output
- edge refinement
- preview
- provider-backed processing

Keep the public **AI Background Remover** tool.

## B. AI Object Removal

Upgrade the existing tool with:
- brush selection
- eraser
- rectangle selection
- lasso where practical
- automatic subject/object selection
- mask preview
- AI inpainting
- multiple object removal

Keep the public **AI Object Remover** tool.

## C. Generative Fill / Inpainting

Add:
1. Select an area with a mask.
2. Optionally enter a prompt.
3. Submit generation.
4. Display result/variations where supported.
5. Accept, reject, or continue editing.

Examples:
- `Remove the person in the background`
- `Replace the empty table with a laptop`
- `Add a plant beside the chair`

Do not claim provider capabilities that are not actually available.

## D. AI Background Replacement

Support:
- generated background
- uploaded background
- preset background
- prompt-based background where supported

Always preserve the original image.

## E. AI Image Expansion / Generative Canvas

Support:
- left/right/top/bottom expansion
- all-side expansion
- custom aspect ratio

Existing normal Resize must remain separate.

## F. AI Enhancement

Upgrade the existing enhancer with provider-backed options where available:
- general enhancement
- denoise
- sharpness
- low-light enhancement
- color correction
- face enhancement where supported

## G. AI Upscaling

Upgrade existing AI Upscaler with provider-backed:
- 2x
- 4x
- higher scale only where supported

Show original/output dimensions and credit cost.

Do not call ordinary Lanczos resizing “AI upscaling.”

## H. AI Relighting

Add where provider support exists:
- brightness
- direction
- warmth
- intensity
- studio lighting presets

## I. Product Image AI

Upgrade Product Image Editor for:
- product isolation
- background cleanup
- studio background
- shadow generation
- centering
- lighting correction
- ecommerce-ready output

## J. Mockup Generation

Upgrade Mockup Generator for supported categories such as:
- phone
- laptop
- packaging
- apparel
- poster
- billboard
- device screen

Only expose provider-supported modes.

## K. Passport Photo

Keep the existing tool. Improve processing only where technically supported:
- crop
- background
- face positioning
- dimensions
- output format
- print layout

Country-specific standards must be explicitly configured; never claim universal compliance.

---

# 5. Editor UX

Preserve the current sidebar and categories.

Recommended structure:

### Basic
- Pan
- Resize
- Crop
- Rotate
- Compress
- Convert

### AI Tools
- BG Remove
- Object Remove
- Upscale
- Enhance
- Passport

### AI Generate
- Generative Fill
- Remove & Replace
- Background Generator
- Expand Canvas
- AI Relight

### Design
- Social
- Product
- Mockup
- Watermark

The exact visual design can improve, but existing tools must remain discoverable.

---

# 6. Mask / Selection System

Create a reusable selection abstraction.

Selection modes:
- Brush
- Eraser
- Rectangle
- Lasso
- Auto Select
- Subject Select
- Invert

Conceptual data:

```text
mask_id
image_id
coordinates
mask_data
brush_size
feather
opacity
created_at
updated_at
```

Use efficient storage for mask data rather than unnecessarily storing huge binary masks in the relational database.

---

# 7. Non-Destructive Editing

Never overwrite the original upload.

Use a version model:

```text
Original
  |
  +-- Edit 1
  +-- Edit 2
  +-- AI Result 1
  +-- AI Result 2
```

Support:
- undo
- redo
- compare
- reject
- accept
- restore original
- export selected version
- continue editing result

---

# 8. Asynchronous AI Job System

AI work must not depend on a long synchronous HTTP request.

```text
Frontend
  -> API
  -> Create Job
  -> Queue
  -> Worker
  -> Provider Adapter
  -> AI Provider
  -> Object Storage
  -> Job Completed
  -> Frontend
```

Job states:
- queued
- processing
- completed
- failed
- cancelled
- expired

Use the project's existing Celery/queue infrastructure where available.

---

# 9. Provider Adapter Architecture

Do not couple the editor directly to one provider.

Create a common interface conceptually supporting:

```text
remove_background()
remove_object()
inpaint()
generate_background()
expand_image()
upscale()
enhance()
relight()
generate_mockup()
```

Possible providers include OpenAI, Google, Stability AI, Replicate, fal, or other compatible providers, but only configured/supported providers should become active.

Never expose provider API keys to the browser.

---

# 10. Provider Fallback

If a provider fails:

```text
Primary
  -> compatible fallback
  -> final failure
```

Rules:
- fallback must support the same capability
- do not silently change the requested operation
- do not silently downgrade quality
- record provider/model used
- record failure reason
- prevent duplicate charging

---

# 11. Credits & Subscription

Use configurable credit costs.

Suggested defaults:

| Operation | Credits |
|---|---:|
| Background Removal | 1 |
| Enhance | 1 |
| Upscale 2x | 2 |
| Upscale 4x | 3 |
| Object Removal | 2 |
| Generative Fill | 3 |
| Background Generation | 3 |
| Image Expansion | 3 |
| AI Relight | 2 |
| Product AI Edit | 3 |
| Mockup Generation | 4 |

These are configurable defaults, not hard-coded business rules.

### Billing transaction

Before expensive processing:

```text
available -> reserved
```

Success:

```text
reserved -> consumed
```

Failure:

```text
reserved -> refunded
```

Prevent negative balances and duplicate charges.

---

# 12. Plan Entitlements

Keep the existing subscription system and centralize entitlements.

### Free
Useful basic tools plus limited AI access.

### Pro
More credits, advanced AI editing, generative tools, higher limits.

### Business
Large credit allocation, team workflows, batch processing, priority queue, API access where implemented.

### Max
Highest limits and queue priority.

Do not hard-code plan checks into many UI components.

---

# 13. Upload & Storage

Validate server-side:
- extension
- MIME type
- file signature
- decodability
- dimensions
- size

Object storage should hold:
- originals
- edited versions
- masks
- temporary files
- generated results
- thumbnails

Use signed URLs for private assets.

Add cleanup/retention policies for temporary files.

---

# 14. Security

Implement:
- authentication
- authorization
- ownership checks
- signed asset URLs
- rate limiting
- upload validation
- server-side provider secrets
- abuse protection
- audit logs

Never expose provider secrets in frontend code.

---

# 15. Safety / Moderation

Use provider safety controls where available.

Add:
- abuse rate limiting
- suspicious usage detection
- reporting
- configurable moderation policy

Do not bypass provider safety mechanisms.

---

# 16. Progress UX

Use real job stages:

```text
Uploading...
Preparing image...
Creating mask...
AI processing...
Finalizing...
Complete
```

For queues:

```text
Queued
Processing
```

Do not fabricate percentage progress when the provider does not provide real progress.

---

# 17. Result UX

Show:
- before/after
- preview
- output dimensions
- file size
- operation
- provider/model where appropriate
- credits consumed
- Download
- Continue Editing
- Edit Again
- Save to Project

AI results must be editable inside the same workspace.

---

# 18. History

Store an operation history conceptually containing:

```text
operation_id
image_id
parent_version_id
operation_type
provider
model
parameters
status
created_at
result_asset
credit_cost
```

Support:
- undo
- redo
- restore
- compare
- branch from a previous version

---

# 19. Batch Processing

Business users should eventually be able to:
- remove backgrounds from many products
- upscale multiple images
- resize image sets
- apply watermarks in bulk

Use server-side batch jobs, not hundreds of simultaneous browser requests.

Support:
- batch ID
- child jobs
- progress
- partial failure
- retry
- export

---

# 20. Tool Registry Compatibility

Do not change existing public tool IDs/slugs unless absolutely necessary.

If implementation changes:

```text
Existing public tool
      -> New backend implementation
```

Keep public URLs working.

New capabilities may be registered as additional tools without overwriting existing records.

---

# 21. Explore All Tools

The current Explore All Tools page must continue to support:
- search
- category filters
- Most Popular
- All Tools
- pagination
- footer navigation

New AI tools may be added through the same registry.

Recommended optional categories:
- Generative AI
- AI Editing
- AI Background
- AI Product Photography

Do not create unnecessary category fragmentation.

---

# 22. SEO

Each public AI tool should have:
- unique title
- meta description
- canonical URL
- useful explanatory content
- FAQ where appropriate
- related-tool links
- structured metadata where appropriate

Potential routes:

```text
/tool/ai-background-remover
/tool/ai-object-remover
/tool/ai-image-upscaler
/tool/ai-image-enhancer
/tool/ai-generative-fill
/tool/ai-background-generator
```

Do not create thin SEO pages consisting only of an editor button.

---

# 23. API / Job Model

Use existing project routing conventions. Conceptual endpoints:

```text
POST /api/image-ai/jobs
GET  /api/image-ai/jobs/:id
POST /api/image-ai/jobs/:id/cancel
POST /api/image-ai/jobs/:id/retry
GET  /api/image-ai/jobs/:id/result
POST /api/image-ai/masks
GET  /api/image-ai/masks/:id
GET  /api/image-ai/capabilities
```

Do not duplicate existing endpoints unnecessarily.

---

# 24. Idempotency

Every expensive AI operation must support idempotency.

Example:

```text
Request A -> Job 123
Request A again -> Job 123
```

Do not create duplicate provider charges.

---

# 25. Cost Controls

Track:
- provider cost
- credit consumption
- queue latency
- job duration
- retries

Configure:
- per-operation credit cost
- plan limits
- provider budget
- global daily budget
- maximum dimensions
- concurrent-job limits
- rate limits

Never perform expensive fallback processing silently after a budget limit.

---

# 26. Performance

Do not use AI providers for basic operations such as:
- crop
- rotate
- simple resize
- basic compression
- format conversion
- watermark

Keep these efficient using existing/local/server-side image processing.

---

# 27. Failure Handling

Handle:
- invalid image
- unsupported format
- image too large
- insufficient credits
- unauthorized tool
- provider timeout
- provider rejection
- provider unavailable
- queue failure
- storage failure
- moderation rejection

Never expose raw stack traces or provider secrets.

Retry only transient failures. Do not automatically retry invalid requests, policy rejection, or insufficient credits.

---

# 28. Testing / Regression Protection

Before release verify:

### Existing product
- all 36 tools still appear
- all existing routes work
- Image Editor opens
- all 14 editor operations work
- export/download works
- authentication works
- subscription checks work

### AI
- background removal
- object removal
- upscale
- enhance
- generative fill
- background generation
- expansion
- relight
- product editing
- mockup

### Billing
- reservation
- consumption
- refund
- duplicate protection
- insufficient credits
- plan restrictions

### Security
- ownership
- asset access
- upload validation
- rate limiting
- provider key protection

---

# 29. Safe Migration Strategy

## Phase 0 — Inspect & Protect
1. Back up current database.
2. Back up current code.
3. Record the 36 registry tools.
4. Record all current routes.
5. Record all 14 editor operations.
6. Add regression tests.

## Phase 1 — Infrastructure
Add:
- AI job model
- provider adapter interface
- storage integration
- queue integration
- credit reservation/refund
- job status API

Do not change existing editor behavior yet.

## Phase 2 — Upgrade Existing AI
Upgrade one at a time:
1. Background Remove
2. Object Remove
3. Upscale
4. Enhance
5. Passport

Test after every tool.

## Phase 3 — New Generative Features
Add:
1. Generative Fill
2. Background Generator
3. Image Expansion
4. AI Relight

## Phase 4 — Business Features
Add:
1. Product AI
2. Mockups
3. Batch processing
4. Project history

## Phase 5 — Production Hardening
Add:
- monitoring
- cost controls
- moderation
- load tests
- security tests
- provider failover
- cleanup jobs

---

# 30. Database Migration Safety

Never drop existing tables or columns merely because a new implementation is introduced.

Prefer:

```text
ADD new structure
-> migrate
-> verify
-> switch usage
-> monitor
```

Only remove legacy structures after proving that:
1. no code uses them
2. no production data depends on them
3. a backup exists
4. migration has been reviewed

**Any destructive migration requires explicit approval.**

---

# 31. Definition of Done

- [ ] 36 existing tools remain available.
- [ ] Existing public tool routes remain functional.
- [ ] Existing Image Editor remains accessible.
- [ ] All 14 editor operations remain available.
- [ ] Basic image operations still work.
- [ ] Existing subscription behavior is preserved.
- [ ] AI jobs are asynchronous.
- [ ] Real providers are used where configured.
- [ ] Provider keys remain server-side.
- [ ] Credits are enforced server-side.
- [ ] Failed jobs refund reserved credits.
- [ ] Duplicate requests do not duplicate charges.
- [ ] Original images remain unchanged.
- [ ] Results are versioned.
- [ ] Before/after comparison works.
- [ ] History/undo works.
- [ ] Upload validation is server-side.
- [ ] Rate limiting exists.
- [ ] Provider failures are handled.
- [ ] Explore All Tools remains functional.
- [ ] SEO pages remain functional.
- [ ] Existing footer/navigation remains functional.
- [ ] No existing feature is silently removed.

---

# 32. AI Agent Command

Give the coding agent this command together with this specification:

> **Implement this specification as a NON-DESTRUCTIVE upgrade to the existing ToolHub AI codebase.**
>
> Do not rewrite the application. Do not replace the existing Image Editor. Do not delete existing tools. Do not remove existing routes. Do not remove registry entries. Do not remove existing UI controls.
>
> First inspect and map:
> 1. Central Tool Registry
> 2. all 36 published tools
> 3. Image Editor Workspace
> 4. all 14 existing editor operations
> 5. existing AI credits/entitlements
> 6. existing image-processing implementation
> 7. storage
> 8. Celery/queue infrastructure
> 9. authentication/subscription
>
> Then produce a file-by-file migration plan before implementation.
>
> Upgrade existing AI tools instead of replacing them:
> - AI Background Remover
> - AI Object Remover
> - AI Image Upscaler
> - AI Image Enhancer
> - AI Passport Photo
> - Mockup Generator
> - Product Image Editor
>
> Add:
> - Generative Fill / Inpainting
> - AI Background Generation
> - Image Expansion / Generative Canvas
> - AI Relighting
>
> Implement non-destructive versions, masks, asynchronous jobs, provider adapters, idempotency, credit reservation/refund, storage security, rate limiting, and production error handling.
>
> Basic operations such as crop, resize, rotate, compress, convert, and watermark must remain efficient and must not be routed through expensive AI providers.
>
> Do not invent provider APIs. If a provider is not configured or does not support a capability, keep that capability disabled/unavailable rather than creating a fake AI response.
>
> Do not perform destructive database migrations.
>
> Run regression tests for all 36 existing tools and all 14 Image Editor operations before declaring completion.
>
> At the end report:
> - files added
> - files modified
> - migrations
> - API changes
> - provider integrations
> - UI changes
> - preserved functionality
> - tests executed
> - remaining limitations
>
> **If any proposed change would delete, hide, rename, break, or materially alter existing functionality, STOP and report it before applying that change.**

---

# 33. Product Goal

The final platform should become:

```text
Existing ToolHub
       +
Production AI Image Engine
       +
Professional Image Editor
       +
Credits / Subscription
       +
Business Workflows
       =
ToolHub AI Image Platform
```

**Backward compatibility is a release requirement, not an optional enhancement.**
