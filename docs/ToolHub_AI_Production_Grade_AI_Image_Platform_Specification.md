# ToolHub AI — Production-Grade AI Image Platform Specification
## Version 2.0 — Implementation Specification

> Upgrade the existing Image Editor and AI Image Processing system into a real production-grade AI image platform.

## 1. Core Objective

The current system contains a basic image editor and AI image-processing actions, but some operations are currently mock/demo or deterministic image manipulation rather than real AI.

The production system must support:

- Real AI image providers and models
- Provider abstraction and routing
- Free, limited-free, Pro and Business entitlements
- Credit accounting and refunds
- Provider cost protection
- Secure image upload and storage
- Prompt-based image editing
- Background removal and replacement
- Object removal
- Inpainting and generative fill
- Outpainting/image expansion
- Real AI upscaling
- AI enhancement
- Batch processing
- Before/after comparison
- High-resolution export and download
- Background jobs, progress, retry and failure recovery
- Usage analytics and audit logging
- Automated tests and production observability

A feature is **not production-ready merely because its UI exists**. It is production-ready only when the backend performs the real operation, the provider integration is real, entitlement and credits are enforced server-side, errors are handled, results are stored safely, downloads work, and tests cover the important success/failure cases.

---

## 2. Existing Limitations That Must Be Removed

### 2.1 Mock image model

`ToolHub Image Edit (Mock)` must never be presented as a real production AI model.

If retained for development, label it clearly as Mock/Development only and hide it from production users.

### 2.2 Background removal

Replace simplistic pixel-based background removal with a real segmentation/background-removal model or provider.

Support transparent PNG output, high-resolution results, better edges, and subject detection.

### 2.3 Upscaling

A normal Lanczos resize is not AI upscaling.

Use a real super-resolution model/provider and clearly distinguish:

`Resize` vs `AI Upscale`.

Only advertise 2×/4×/4K when the actual provider output supports it.

### 2.4 Enhancement

Replace fixed contrast/sharpness/color manipulation with real AI enhancement or clearly label the operation as a standard image filter.

### 2.5 Object removal

The existing fixed center-circle behavior is not acceptable.

Implement actual selection/masking and context-aware inpainting.

### 2.6 Prompt editing

Prompt suggestions must invoke a real image-editing provider.

Examples:

- Remove the object on the left.
- Replace the background with a modern office.
- Make the background transparent.
- Change the shirt color to black.
- Expand this image to a square.
- Make this product photo look like a premium studio photograph.

The prompt box must never be decorative.

---

## 3. Product Positioning

ToolHub AI Image should not be positioned merely as another image generator.

Recommended positioning:

> **An AI-powered image workspace for creating, editing, transforming, optimizing and processing images.**

Core pillars:

1. Generate
2. Edit
3. Remove
4. Replace
5. Enhance
6. Upscale
7. Transform
8. Batch Process
9. Export

---

## 4. Image Platform Categories

### Generate
- Text to Image
- Image to Image
- Style Transformation
- Product Image Generation
- Social Media Image
- Marketing Creative
- Thumbnail
- Poster
- Illustration

### Edit
- AI Edit
- Generative Fill
- Object Remove
- Object Replace
- Background Replace
- Inpainting
- Outpainting
- Recolor
- Relight where supported

### Improve
- Background Remove
- Upscale
- Enhance
- Sharpen
- Denoise
- Face enhancement where supported

### Convert
- JPG → PNG
- PNG → JPG
- WebP conversion
- AVIF where supported
- Image → PDF
- PDF page → Image

### Utility
- Resize
- Crop
- Rotate
- Flip
- Compress
- Metadata removal
- Watermark
- Batch resize
- Batch compression
- Batch conversion

---

## 5. Provider Architecture

Do not hard-code providers into UI components.

Use:

```text
ImageService
 ├── ProviderRegistry
 ├── CapabilityRegistry
 ├── ModelRegistry
 ├── ModelRouter
 ├── CostController
 ├── EntitlementService
 ├── CreditService
 ├── JobService
 └── StorageService
```

Provider adapters should expose only capabilities actually supported by that provider/model.

Conceptually:

```text
BaseImageProvider
 ├── generate()
 ├── edit()
 ├── inpaint()
 ├── outpaint()
 ├── remove_background()
 ├── remove_object()
 ├── upscale()
 └── enhance()
```

Possible providers may include OpenAI, Google, compatible image providers, Hugging Face-compatible providers, self-hosted open models, and future providers. Do not assume every provider supports every operation.

---

## 6. Model Registry

Each model should have normalized metadata:

```text
id
provider
display_name
internal_model_id
capabilities[]
tier
active
max_resolution
supported_input_formats[]
supported_output_formats[]
cost_per_operation
queue_priority
quality_score
speed_score
availability
```

The public UI should use friendly model names. Internal provider identifiers should not be unnecessarily exposed.

---

## 7. Model Routing

Users may select:

- Auto
- Specific model
- Specific provider where permitted

Auto routing should consider:

1. Requested capability
2. User plan
3. Available credits
4. Provider availability
5. Image resolution
6. Input format
7. Quality
8. Speed
9. Provider cost
10. Provider health

The router must never select a model outside the user's entitlement.

If the user explicitly selects a model, do not silently switch to another model.

For Auto mode, eligible fallback models may be used when a provider fails.

---

## 8. Free / Pro / Business Model

### Free

Allow sustainable free/open models and basic tools with server-side limits.

Example limits are configuration examples only:

```text
Generations: 3/day
AI edits: 5/day
Upscale: 2/day
Background removal: 5/day
Batch size: 3
```

### Free Unlimited

Only mark a capability unlimited when its cost is genuinely sustainable, such as a self-hosted open model or predictable near-zero-cost local processing.

Never promise unlimited usage of a third-party API simply because its current free tier exists.

### Pro

- Premium image models
- Higher resolution
- Larger limits
- Advanced editing
- More credits
- Batch processing
- Priority queue
- Better export options

### Business

- Team usage
- Shared projects
- Shared credits
- Central billing
- Usage analytics
- Admin controls
- Large batch processing
- Higher limits
- Priority processing
- API access where available

---

## 9. Credits and Cost Protection

Every paid AI operation must pass server-side cost checks.

Flow:

```text
Request
 ↓
Authentication
 ↓
Plan Entitlement
 ↓
Model Entitlement
 ↓
Credit Check
 ↓
Provider Cost Check
 ↓
Create Job
 ↓
Reserve Credits
 ↓
Provider Call
 ↓
Success → Commit
Failure → Refund
```

Use transaction-safe reservation/commit/refund logic and prevent negative balances or race-condition double spending.

Example:

```text
reserved = 5

success → consumed 5
failure → refund 5
```

---

## 10. Provider Budget Guard

Protect the owner's money with:

- Per-provider daily budget
- Per-provider monthly budget
- Per-model budget
- Per-user daily spending limit
- Per-plan spending ceiling
- Organization spending limit
- Emergency kill switch

When a budget is exceeded, stop paid provider calls and expose a controlled unavailable state.

Admin metrics should include:

- Provider spend
- Estimated spend
- Requests
- Failures
- Cost per operation
- Cost per user
- Cost per plan
- Margin estimate

---

## 11. Image Upload Security

Backend validation must include:

- Extension
- MIME type
- Magic bytes/file signature
- File size
- Pixel dimensions
- Actual decoding
- Malformed files
- Decompression-bomb protection

Do not trust filename or MIME header alone.

Example configurable limits:

```text
AI input: 25 MB
Standard image tools: 50 MB
Maximum pixels: configurable
```

Backend is authoritative; frontend limits are only UX.

---

## 12. Supported Formats

At minimum:

Input:
- JPG/JPEG
- PNG
- WebP

Optional where safely supported:
- GIF
- TIFF
- BMP
- HEIC/HEIF

Output:
- PNG
- JPG
- WebP

Preserve transparency when supported.

Do not silently convert transparent PNG to JPG.

---

## 13. Resolution Integrity

The platform must never silently reduce resolution.

Record:

```text
input_width
input_height
output_width
output_height
input_bytes
output_bytes
model
provider
operation
```

Display resolution clearly:

```text
Original: 4000 × 3000
Output:   4000 × 3000
```

Do not claim “4K” when the system merely resized the image to 4K without AI reconstruction.

---

## 14. Before / After

Provide:

- Side-by-side
- Split slider
- Zoom
- Fit to screen
- Actual size
- Reset
- Compare

Show original and output dimensions.

---

## 15. Professional Image Editor UI

Preserve the existing ToolHub AI design system.

Use:

- shadcn/ui
- clean neutral palette
- ToolHub brand colors
- Vercel-inspired principles, **not Vercel copied**
- existing `/tools` visual language
- existing Mega Menu visual language
- consistent typography
- spacing
- borders
- approved icon system

Avoid random backgrounds, excessive colors, unrelated gradients, inconsistent shadows, oversized navigation, and disconnected controls.

### Recommended layout

```text
┌──────────────────────────────────────────────┐
│ ToolHub AI        Image Editor      Account  │
├────────────┬──────────────────────┬──────────┤
│ Tools      │                      │ Settings │
│ Generate   │       Canvas         │ AI Model │
│ Edit       │                      │ Prompt   │
│ Remove     │                      │          │
│ Enhance    │                      │ Run      │
│ Upscale    │                      │          │
│ Convert    │                      │          │
├────────────┴──────────────────────┴──────────┤
│ Before / After │ Resolution │ Credits │ Save │
└──────────────────────────────────────────────┘
```

Mobile must use a responsive tool drawer/bottom sheet without horizontal overflow.

---

## 16. Prompt Editing UX

Provide:

```text
What would you like to change?

[ Remove the object on the left              ]

[ Select area ] [ Brush ] [ Eraser ]

Model: Auto
Resolution: Original
Credits: 2

[ Generate Edit ]
```

Prompt + mask must actually be sent to the provider for operations requiring a mask.

---

## 17. Masking

Implement:

- Brush
- Eraser
- Brush size
- Softness
- Undo/redo
- Clear
- Invert
- Zoom
- Pan
- Mask preview
- Automatic subject selection where supported

Associate the mask securely with the image job.

---

## 18. Background Removal

Production flow:

```text
Upload
 ↓
Validate
 ↓
Create Job
 ↓
Real segmentation/background-removal model
 ↓
Transparent PNG
 ↓
Preview
 ↓
Download
```

Support transparent preview, high-resolution output, and edge quality.

---

## 19. Background Replacement

Flow:

```text
Upload
 ↓
Remove background
 ↓
Enter background prompt
 ↓
Generate
 ↓
Composite
 ↓
Preview
 ↓
Export
```

---

## 20. Object Removal

Use:

```text
Image
 ↓
Brush/select object
 ↓
Create mask
 ↓
Optional prompt
 ↓
Real inpainting model
 ↓
Result
```

Never use the old fixed center-circle implementation.

---

## 21. Generative Fill / Inpainting

Support:

- Mask
- Prompt
- Multiple variants
- Retry
- Undo
- Version history

Original image must remain untouched.

---

## 22. Outpainting

Support:

- Square expansion
- Landscape expansion
- Portrait expansion
- Custom canvas

Expand the canvas; never simply stretch the original image.

---

## 23. AI Upscaling

Clearly distinguish:

```text
Resize
```

from:

```text
AI Upscale
```

Expose only resolutions actually supported by the selected model.

---

## 24. Enhancement

Possible presets:

- Auto
- Product
- Portrait
- Low-light
- Sharpen
- Denoise

Only expose capabilities actually implemented.

---

## 25. Batch Processing

Business users should be able to:

```text
Upload 100 images
 ↓
Select operation
 ↓
Select model
 ↓
Preview first 3
 ↓
Confirm
 ↓
Queue
 ↓
Process
 ↓
Download ZIP
```

Requirements:

- Plan-based batch size
- Progress
- Per-file status
- Retry failed files
- Cancel remaining jobs
- Download successful results
- ZIP export
- Credit estimate before confirmation

---

## 26. Job Queue

Use the existing asynchronous infrastructure where appropriate.

Lifecycle:

```text
queued
processing
completed
failed
cancelled
expired
```

Store user, organization, operation, provider, model, status, progress, input, output, reserved/consumed credits, errors and timestamps.

Long AI processing must not be implemented as a blocking synchronous request.

---

## 27. Progress

Show real processing stages:

```text
Uploading
Validating
Preparing image
Processing with AI
Finalizing
Ready
```

Never fake an exact percentage if the provider does not provide progress.

---

## 28. Retry

Retry only transient failures such as timeout, temporary provider failure and suitable 5xx errors.

Do not retry invalid input, insufficient credits, policy rejection, invalid credentials or unsupported resolution.

Use exponential backoff.

---

## 29. Download

Every successful result must be downloadable.

Provide formats actually supported by the output.

Show:

```text
Format
Dimensions
File size
Quality
```

Do not lower resolution just to simplify downloading.

For batch jobs provide ZIP download.

---

## 30. Storage and Privacy

Production architecture:

```text
Private upload
 ↓
Processing
 ↓
Private result
 ↓
Short-lived signed download URL
```

Requirements:

- Private by default
- User ownership checks
- Organization isolation
- Signed URLs
- Expiration
- Cleanup jobs
- Delete input/output
- Account deletion support

Do not retain user images indefinitely without a clear product reason.

---

## 31. Metadata

Provide an option:

```text
Remove metadata before export
```

Make metadata stripping easy for privacy-sensitive workflows.

---

## 32. Error Handling

Example:

```text
Selected model is temporarily unavailable.

Your credits were not consumed.
Please try again or use Auto.
```

or:

```text
This image exceeds the selected model's maximum resolution.

Try:
• Resize image
• Choose another model
• Use Auto
```

Never expose raw provider stack traces.

---

## 33. Subscription Enforcement

Every AI image endpoint must validate server-side:

```text
authenticated
+
feature enabled
+
plan permitted
+
model permitted
+
credits available
+
rate limit available
+
provider available
+
budget available
```

Frontend restrictions are never authorization.

---

## 34. Model Cards

Show:

- Model name
- Provider
- Capability
- Quality
- Speed
- Resolution
- Tier
- Credits per operation
- Availability

Example:

```text
AI Edit Pro

Provider: Example
Capability: Image Editing
Quality: High
Speed: Fast
Resolution: Up to 4K
Cost: 2 credits
Plan: Pro
```

Do not expose sensitive internal provider pricing unnecessarily.

---

## 35. Safety and Provider Policy

Implement:

- Provider/model safety controls
- Abuse monitoring
- Rate limiting
- Safety-related failure logging
- Provider terms compliance

Do not promise capabilities that a provider does not permit.

---

## 36. Observability

Track:

- Requests
- Success rate
- Failure rate
- Average latency
- Provider latency
- Model latency
- Cost
- Credits
- Queue duration
- Download rate
- Error categories
- Retry rate

Admin dashboard should expose:

```text
Image Jobs Today
Success Rate
Provider Cost
Credits Consumed
Top Models
Top Operations
Failed Jobs
Average Processing Time
```

---

## 37. Security

Implement:

- Authentication
- Authorization
- Object ownership checks
- Organization isolation
- Rate limiting
- CSRF protection where applicable
- Secure upload handling
- File scanning where appropriate
- Signed URLs
- Secret management
- API key encryption
- Audit logging
- Abuse prevention

Provider API keys must never reach the browser.

---

## 38. API Design

Use the existing project's API conventions. Conceptually:

```text
POST   /api/image/jobs/
GET    /api/image/jobs/:id/
POST   /api/image/jobs/:id/cancel/
POST   /api/image/jobs/:id/retry/
GET    /api/image/jobs/
POST   /api/image/preview/
POST   /api/image/export/
GET    /api/image/models/
GET    /api/image/capabilities/
GET    /api/image/credits/
```

Use schema/serializer validation and consistent errors.

---

## 39. Database

Reuse existing project-wide User, Subscription, Plan, Credit, Organization and Project entities.

Where needed, add:

```text
ImageModel
ImageProvider
ImageJob
ImageAsset
ImageMask
ImageVariant
ImageUsage
ImageCreditTransaction
```

Do not create duplicate billing, subscription or credit systems.

---

## 40. Credit Ledger

Every transaction must be auditable.

Example:

```text
+100 subscription credits
-2 image edit
+2 failed-job refund
-4 upscale
```

Never change a balance without a corresponding ledger event.

Use idempotency keys.

---

## 41. Idempotency

Image job creation must accept an idempotency key.

Same request + same idempotency key:

```text
return existing job
do not create another provider request
do not double-charge
```

---

## 42. Provider Failover

Auto mode may use eligible fallback providers/models.

Fallback must respect:

- Capability
- Quality
- Entitlement
- Credits
- Budget
- Provider health

Do not silently downgrade explicit model selection.

---

## 43. Tests

### Unit
- Credit reservation
- Credit refund
- Cost calculation
- Model routing
- Entitlement
- File validation
- Resolution validation
- Mask validation
- Provider adapters

### Integration
- Upload → job → provider → result
- Provider failure → refund
- Insufficient credits → blocked
- Free user → premium blocked
- Pro user → premium allowed
- Batch processing
- Signed download

### E2E
Test real browser flows:

1. Upload
2. Background removal
3. Prompt editing
4. Mask selection
5. Generate
6. Before/after
7. Download
8. Verify resolution
9. Verify credit deduction

---

## 44. Resolution and Download Tests

For every operation verify:

```text
input dimensions
→ output dimensions
```

Check:

- No unexpected downscale
- Correct transparency
- Correct output format
- File integrity
- Downloaded file matches metadata

---

## 45. Failure Tests

Test:

- Provider timeout
- Provider 500
- Invalid API key
- Rate limit
- Out of credits
- Unauthorized model
- Invalid image
- Huge image
- Corrupt image
- Unsupported format
- Queue failure
- Storage failure
- Expired download

Every failure must leave the credit ledger consistent.

---

## 46. UI Quality Checklist

Before release:

- No broken layout
- No overflow
- No clipped controls
- No inconsistent backgrounds
- No random colors
- No oversized navigation
- Mobile responsive
- Keyboard accessible
- Loading states
- Empty states
- Error states
- Success states
- Accessible labels
- Tooltips where useful
- Preview works
- Before/after works
- Model selector works
- Credit display is correct
- Download works

---

## 47. Brand Rules

The Image Platform is part of ToolHub AI.

Always preserve:

- ToolHub brand identity
- shadcn/ui
- approved Lucide/existing icon system
- existing typography
- existing spacing
- existing `/tools` visual language
- existing Mega Menu visual language

Use:

> **Vercel-inspired principles, not Vercel copied design.**

Do not create a separate design system for Image Tools.

---

## 48. No Fake Features

Never show a feature as production-ready when it is not real.

Do not show:

- AI generation if backend is mock
- AI upscale if it is only a normal resize
- Object removal if there is no real mask/inpainting
- Prompt editing if the prompt is ignored
- 4K if actual output is not 4K
- Unlimited if provider quota is limited
- Premium access if entitlement is not enforced

Incomplete functionality must be hidden or explicitly marked `Coming Soon`.

---

## 49. Admin Controls

Admin should be able to:

- Enable/disable provider
- Enable/disable model
- Enable/disable capability
- Set model tier
- Set credit cost
- Set resolution limits
- Set batch limits
- Set provider budget
- Set rate limits
- View jobs
- Retry jobs
- Cancel jobs
- View failures
- View costs

Routine model configuration should not require code deployment.

---

## 50. Secret Management

Provider credentials must remain server-side.

Example environment variables:

```env
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
HUGGINGFACE_API_KEY=
```

Only configure providers actually used.

Requirements:

- Never expose keys to frontend
- Never log keys
- Mask keys in admin UI
- Secure secret storage
- Provider credential validation
- Provider health check

---

## 51. Production Rollout

Implement incrementally:

### Stage 1
Real provider architecture and one real image operation.

### Stage 2
Background removal, AI upscale and enhancement.

### Stage 3
Prompt editing, object removal and inpainting.

### Stage 4
Outpainting and background replacement.

### Stage 5
Batch processing.

### Stage 6
Business workspace and team controls.

### Stage 7
Additional providers/models.

Do not expose unfinished stages as production capabilities.

---

## 52. Definition of Done

The platform is complete only when applicable requirements are verified:

- [ ] No mock model exposed in production
- [ ] Real provider integration works
- [ ] Model registry works
- [ ] Provider routing works
- [ ] Free/Pro/Business entitlement works
- [ ] Credit reservation works
- [ ] Credit refund works
- [ ] Provider budget protection works
- [ ] Secure upload validation works
- [ ] Background removal works
- [ ] Background replacement works
- [ ] Object removal works
- [ ] Masking works
- [ ] Prompt editing works
- [ ] Inpainting works
- [ ] Outpainting works
- [ ] AI upscaling works
- [ ] Enhancement works
- [ ] Batch processing works
- [ ] Queue works
- [ ] Retry works
- [ ] Download works
- [ ] Resolution is preserved/reported
- [ ] Private storage works
- [ ] Signed URLs work
- [ ] Metadata handling works
- [ ] Rate limiting works
- [ ] Security checks work
- [ ] Admin controls work
- [ ] Usage analytics work
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Mobile UI works
- [ ] No fake capability remains

---

## 53. Final AI Coding Agent Instruction

Before changing code, inspect:

1. Existing frontend image editor
2. Existing backend image APIs
3. Model registry
4. Provider adapters
5. Subscription/entitlement system
6. Credit system
7. Celery/background jobs
8. Storage
9. Existing design system
10. Existing tests

Then create an implementation plan.

Implement incrementally.

Do not blindly rewrite the existing Image Editor.

Do not remove working functionality unless the replacement is equal or better.

Do not change unrelated modules.

Do not create duplicate billing, subscription, credit or authentication systems.

After implementation run:

```text
migrations
backend tests
frontend tests
lint
type checking
production build
E2E tests
provider integration smoke tests
image dimension verification
download verification
credit ledger verification
free/pro/business access verification
failed-job refund verification
provider budget verification
mobile UI verification
```

Finally produce an implementation report containing:

- Files changed
- Features implemented
- Providers configured
- Models configured
- Required environment variables
- Database migrations
- API endpoints
- Tests executed
- Tests passed
- Known limitations
- Production deployment requirements

**Never claim 100% completion unless the Definition of Done has actually been verified.**
