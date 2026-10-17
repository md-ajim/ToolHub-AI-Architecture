# 12 --- AI Processing Architecture

**Updated Version:** 2.0\
**Supersedes:** 1.0\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v2.0 Addendum --- Unified AI Processing Contract

This update preserves the existing asynchronous
image/creative-processing architecture and adds a clean boundary for the
multi-model AI Workspace.

### Mandatory principles

-   Interactive chat/vision/short AI requests use the AI Gateway and
    normalized provider adapters.
-   Heavy creative jobs continue through the async job system.
-   The frontend never depends directly on a provider SDK or
    model-specific response shape.
-   Model selection, entitlement, credits, fallback, usage and provider
    health remain server-enforced.
-   Image AI and conversational AI may share infrastructure, but are not
    forced into one processing pipeline.
-   New providers/models must be addable without rewriting existing
    tools.

``` text
Interactive AI
→ Auth → Entitlement → Credit Reservation → Model Router
→ Provider Adapter → Stream/Response → Usage → Settlement

Async Creative AI
→ Auth → Entitlement → Credit Reservation → Job
→ Queue → Worker → Model Adapter → Storage
→ Result → Usage → Settlement
```

Existing AI tools, queues, workers, storage and credit enforcement
remain supported.

------------------------------------------------------------------------

**Project:** Multi-Tool Utility / Micro-SaaS Platform\
**Document:** AI Processing Architecture\
**Status:** Architecture Specification\
**Version:** 1.0\
**Last Updated:** 2026-08-09

------------------------------------------------------------------------

## 1. Purpose

This document defines the architecture for all AI-powered processing
features in the platform.

The architecture must support:

-   AI image enhancement
-   Image upscaling
-   Image restoration
-   Background removal
-   Auto clipping path
-   Object removal
-   Product background generation
-   AI image editing
-   AI document processing
-   AI-assisted content generation where applicable
-   Batch processing
-   Free and paid processing limits
-   Asynchronous jobs
-   Queue-based execution
-   GPU/CPU worker separation
-   Processing history
-   Secure file handling
-   Usage metering
-   Subscription-based quotas
-   API access
-   Future addition of new AI models without redesigning the entire
    system

The system must be designed so that new AI tools can be added
incrementally without breaking existing tools.

------------------------------------------------------------------------

# 2. Core Architectural Principle

The frontend must **never directly depend on a specific AI model**.

The architecture should follow:

``` text
User
  ↓
Next.js Frontend
  ↓
Django REST API
  ↓
AI Processing Service / Job Manager
  ↓
Queue
  ↓
AI Worker
  ↓
Model Adapter
  ↓
AI Model
  ↓
Output Storage
  ↓
Job Result
  ↓
Frontend
```

This separation allows models to be replaced or upgraded independently.

Conversational multi-model workloads are specified separately in
`32-ai-workspace-architecture.md`. They reuse provider abstraction, cost
controls, usage tracking and secure file handling, but do not force all
chat requests through the long-running image-job pipeline.

------------------------------------------------------------------------

# 3. AI Processing Layers

The AI architecture is divided into the following layers:

``` text
┌───────────────────────────────┐
│          Frontend             │
│      Next.js / React          │
└───────────────┬───────────────┘
                │
┌───────────────▼───────────────┐
│          API Layer             │
│       Django REST API          │
└───────────────┬───────────────┘
                │
┌───────────────▼───────────────┐
│       Processing Manager       │
│ Job creation / validation      │
│ quota / permissions / routing  │
└───────────────┬───────────────┘
                │
┌───────────────▼───────────────┐
│          Job Queue             │
│        Redis / Broker          │
└───────────────┬───────────────┘
                │
        ┌───────┴────────┐
        │                │
┌───────▼───────┐ ┌──────▼────────┐
│ CPU Workers    │ │ GPU Workers   │
│ Pillow/OpenCV  │ │ AI Models     │
└───────┬───────┘ └──────┬────────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼─────────┐
        │ Output Storage   │
        │ S3/Object Store  │
        └──────────────────┘
```

------------------------------------------------------------------------

# 4. AI Tool Categories

## 4.1 Image AI

Initial AI image tools:

1.  Background Remover
2.  Auto Clipping Path
3.  Photo Enhancer
4.  Image Upscaler
5.  Image Deblurring
6.  Image Restoration
7.  Object Remover
8.  Product Background Generator
9.  AI Image Cleanup
10. AI Image Relighting

Future tools may include:

-   Face enhancement
-   Old photo restoration
-   Noise removal
-   Shadow generation
-   Background replacement
-   AI image expansion
-   Smart crop
-   Portrait enhancement

------------------------------------------------------------------------

# 5. Model Abstraction

Each AI capability must use a model adapter.

Example:

``` python
class AIModelAdapter:
    def process(self, input_file, options):
        raise NotImplementedError
```

Example implementation:

``` python
class BackgroundRemovalAdapter(AIModelAdapter):
    def process(self, input_file, options):
        ...
```

The application should not directly call model-specific code from views.

Bad:

``` python
def remove_background(request):
    rembg.remove(...)
```

Preferred:

``` python
job = ai_service.create_job(
    tool="background-remover",
    user=request.user,
    input_file=file
)
```

The service decides which model should process the job.

------------------------------------------------------------------------

# 6. Model Registry

Maintain a central model registry.

Example conceptual structure:

``` text
Model Registry

background-removal
 ├── rembg
 ├── model-v2
 └── premium-model

upscaling
 ├── realesrgan
 └── premium-upscaler

enhancement
 ├── basic-enhancer
 └── premium-enhancer
```

Each model should define:

-   model name
-   version
-   supported formats
-   maximum resolution
-   CPU/GPU requirement
-   estimated processing cost
-   timeout
-   supported plans
-   status
-   quality tier

------------------------------------------------------------------------

# 7. AI Job System

Every AI operation must be represented as a processing job.

Example lifecycle:

``` text
CREATED
   ↓
QUEUED
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure path:

``` text
PROCESSING
   ↓
FAILED
```

Cancellation path:

``` text
QUEUED / PROCESSING
   ↓
CANCELLED
```

Recommended statuses:

``` text
pending
queued
processing
completed
failed
cancelled
expired
```

------------------------------------------------------------------------

# 8. Job Model

Conceptual fields:

``` text
AIProcessingJob

id
user_id
tool_id
model_id
input_file_id
output_file_id
status
priority
options
error_code
error_message
processing_started_at
processing_completed_at
processing_duration
created_at
updated_at
```

Additional fields may include:

``` text
credits_consumed
estimated_cost
actual_cost
worker_id
retry_count
```

------------------------------------------------------------------------

# 9. Queue Architecture

AI processing must be asynchronous.

The HTTP request should create a job and return immediately.

Example:

``` text
POST /api/v1/ai/jobs

Response:

{
  "job_id": "...",
  "status": "queued"
}
```

The worker processes the job separately.

This prevents:

-   request timeout
-   web server blocking
-   poor user experience
-   server instability
-   inability to scale workers independently

------------------------------------------------------------------------

# 10. Recommended Queue Stack

Initial architecture:

``` text
Django
   ↓
Celery
   ↓
Redis
   ↓
AI Workers
```

Possible future architecture:

``` text
Django
   ↓
Message Broker
   ↓
Dedicated Worker Pools
   ├── CPU Workers
   ├── GPU Workers
   ├── High Priority Workers
   └── Batch Workers
```

------------------------------------------------------------------------

# 11. Worker Types

## CPU Worker

For:

-   resize
-   format conversion
-   compression
-   metadata processing
-   simple image operations
-   PDF operations

Technologies:

-   Pillow
-   OpenCV
-   ImageMagick where appropriate

## GPU Worker

For:

-   background removal
-   upscaling
-   enhancement
-   restoration
-   object removal
-   generative image processing

GPU workers should be independently scalable.

------------------------------------------------------------------------

# 12. Processing Priority

Jobs should have priorities.

Example:

``` text
Priority 1 — Paid / Premium
Priority 2 — Standard authenticated users
Priority 3 — Free users
Priority 4 — Anonymous bulk/background jobs
```

However, free users must still receive predictable service.

Priority must not be implemented in a way that permanently starves free
jobs.

------------------------------------------------------------------------

# 13. Free vs Premium AI Processing

## Free

Possible restrictions:

-   daily processing limit
-   lower resolution
-   slower queue
-   limited batch size
-   watermark where appropriate
-   limited history
-   limited storage

## Premium

Possible benefits:

-   higher resolution
-   larger batch size
-   faster queue
-   more AI credits
-   no watermark
-   longer history
-   cloud workspace
-   premium models
-   commercial-use options where licensing permits

------------------------------------------------------------------------

# 14. Credit-Based AI Usage

AI processing should support a credit system.

Example:

``` text
1 standard image = 1 credit
HD enhancement = 3 credits
4K upscale = 8 credits
Object removal = 5 credits
Generative background = 10 credits
```

Actual values should be configured rather than hard-coded.

A user plan can define:

``` text
monthly_credits
daily_limit
maximum_file_size
maximum_resolution
maximum_batch_size
```

------------------------------------------------------------------------

# 15. Usage Metering

Every AI operation must be measurable.

Record:

``` text
user
tool
model
job
credits
processing_time
input_size
output_size
timestamp
```

This data is required for:

-   billing
-   quota enforcement
-   analytics
-   abuse detection
-   cost calculation
-   profitability analysis

------------------------------------------------------------------------

# 16. AI Cost Tracking

The platform must track estimated AI processing cost.

Example:

``` text
AI Cost

model_cost
compute_cost
storage_cost
bandwidth_cost
total_estimated_cost
```

This is important because AI features can become expensive at scale.

The system should be able to answer:

``` text
How much did this user cost us?

How much revenue did this user generate?

Which AI tool has the highest infrastructure cost?

Which plan is profitable?

What is the average cost per processed image?
```

------------------------------------------------------------------------

# 17. File Processing Pipeline

Standard pipeline:

``` text
Upload
 ↓
File Validation
 ↓
Virus / Security Check
 ↓
Metadata Validation
 ↓
Temporary Storage
 ↓
Create AI Job
 ↓
Queue
 ↓
Worker
 ↓
AI Processing
 ↓
Output Validation
 ↓
Permanent Storage
 ↓
Job Completion
 ↓
Download URL
```

------------------------------------------------------------------------

# 18. Input Validation

Validate:

-   MIME type
-   extension
-   file size
-   dimensions
-   color mode
-   corrupted files
-   supported format
-   malicious payloads

Never trust the extension alone.

------------------------------------------------------------------------

# 19. Output Validation

Before exposing an AI-generated file:

-   verify file exists
-   verify MIME type
-   verify file integrity
-   verify expected dimensions
-   verify output size
-   scan where necessary
-   generate secure download URL

------------------------------------------------------------------------

# 20. Temporary Files

Temporary processing files must not remain indefinitely.

Example policy:

``` text
Temporary input:
1–6 hours

Failed job files:
short retention

Completed free output:
configurable short retention

Premium workspace:
long-term retention according to plan
```

Retention values must be configurable.

------------------------------------------------------------------------

# 21. Storage Architecture

Recommended:

``` text
AWS S3 / compatible object storage
```

Separate storage prefixes:

``` text
users/
temp/
ai-inputs/
ai-outputs/
avatars/
projects/
exports/
```

Never expose private object storage directly.

Use signed URLs.

------------------------------------------------------------------------

# 22. Security

AI processing introduces file-security risks.

Required controls:

-   authentication
-   authorization
-   MIME validation
-   file-size limits
-   filename sanitization
-   secure object storage
-   signed URLs
-   rate limiting
-   abuse detection
-   job ownership validation
-   worker isolation
-   timeout limits
-   resource limits
-   automatic cleanup

------------------------------------------------------------------------

# 23. API Design

Example endpoints:

``` text
POST   /api/v1/ai/jobs
GET    /api/v1/ai/jobs/{id}
POST   /api/v1/ai/jobs/{id}/cancel
GET    /api/v1/ai/jobs/{id}/result
GET    /api/v1/ai/tools
GET    /api/v1/ai/usage
GET    /api/v1/ai/history
```

For batch processing:

``` text
POST /api/v1/ai/batch-jobs
GET  /api/v1/ai/batch-jobs/{id}
```

------------------------------------------------------------------------

# 24. Job Progress

For long-running tasks, the frontend should receive progress updates.

Possible implementation:

``` text
Option A:
Polling

Option B:
Server-Sent Events

Option C:
WebSocket
```

Initial implementation can use polling.

Example:

``` text
GET /api/v1/ai/jobs/{id}

{
  "status": "processing",
  "progress": 65
}
```

WebSockets/SSE can be introduced later if required.

------------------------------------------------------------------------

# 25. Batch Processing

Batch jobs should be separate from single jobs.

Example:

``` text
Batch Job
 ├── Job 1
 ├── Job 2
 ├── Job 3
 ├── Job 4
 └── Job 5
```

The system should support:

-   batch size limits
-   parallel processing
-   partial failure
-   retry
-   ZIP export
-   progress tracking

Example:

``` text
100 files
95 completed
3 failed
2 cancelled
```

The user should still be able to download successful results.

------------------------------------------------------------------------

# 26. Retry Strategy

Transient failures should be retried.

Example:

``` text
Attempt 1
 ↓
Failure
 ↓
Retry
 ↓
Attempt 2
 ↓
Failure
 ↓
Retry
 ↓
Attempt 3
 ↓
Permanent Failure
```

Do not endlessly retry AI jobs.

------------------------------------------------------------------------

# 27. Timeout Strategy

Every model must define a maximum processing time.

Example:

``` text
Standard image:
60 seconds

Large image:
180 seconds

Generative job:
300 seconds
```

Values must be configurable.

------------------------------------------------------------------------

# 28. Model Fallback

Where multiple models are available:

``` text
Primary Model
     ↓
Failure
     ↓
Fallback Model
     ↓
Failure
     ↓
Job Failed
```

Fallback should only be enabled when output quality and cost are
acceptable.

------------------------------------------------------------------------

# 29. AI Provider Abstraction

The architecture should support both self-hosted models and external
APIs.

``` text
AI Provider Interface
       │
       ├── Local Model
       ├── Cloud AI Provider
       ├── Specialized API
       └── Future Provider
```

This prevents vendor lock-in.

------------------------------------------------------------------------

# 30. Self-Hosted vs External API

## Self-hosted

Advantages:

-   lower cost at high volume
-   full control
-   custom models
-   privacy control
-   predictable processing pipeline

Disadvantages:

-   GPU infrastructure
-   model maintenance
-   deployment complexity
-   scaling cost

## External API

Advantages:

-   fast initial launch
-   no GPU management
-   easy experimentation
-   automatic model upgrades

Disadvantages:

-   per-request cost
-   provider dependency
-   rate limits
-   API pricing changes

### Strategy

Start with APIs/self-hosted open-source models where practical.

Move high-volume profitable workloads to self-hosted models when
economics justify it.

------------------------------------------------------------------------

# 31. AI Tool Configuration

AI tools must be configurable from the backend.

Example:

``` text
AITool

id
slug
name
description
category
active
free_enabled
premium_enabled
model
max_file_size
max_resolution
credit_cost
daily_limit
batch_limit
```

This avoids hard-coding business rules into frontend components.

------------------------------------------------------------------------

# 32. AI Model Configuration

Example:

``` text
AIModel

id
name
provider
version
tool
type
cpu_or_gpu
active
priority
cost_per_operation
max_resolution
timeout_seconds
```

------------------------------------------------------------------------

# 33. AI Processing Service

Business logic should live in a dedicated service layer.

Example:

``` text
ai/
├── services/
│   ├── job_service.py
│   ├── processing_service.py
│   ├── quota_service.py
│   ├── credit_service.py
│   ├── model_service.py
│   └── cost_service.py
```

Django views should remain thin.

------------------------------------------------------------------------

# 34. Suggested Backend Structure

``` text
backend/
├── apps/
│   ├── ai/
│   │   ├── models/
│   │   ├── serializers/
│   │   ├── views/
│   │   ├── services/
│   │   ├── tasks/
│   │   ├── adapters/
│   │   ├── validators/
│   │   ├── permissions/
│   │   └── admin/
│   │
│   ├── files/
│   ├── subscriptions/
│   ├── usage/
│   └── users/
│
├── workers/
│   ├── cpu/
│   └── gpu/
│
└── config/
```

------------------------------------------------------------------------

# 35. Frontend Architecture

Each AI tool should have its own dedicated page.

Example:

``` text
/tools/background-remover
/tools/image-upscaler
/tools/photo-enhancer
/tools/object-remover
/tools/image-restorer
```

Reusable UI:

``` text
AIUploadArea
ProcessingOptions
ProcessingProgress
ResultPreview
BeforeAfterViewer
DownloadButton
BatchUploader
UsageIndicator
UpgradePrompt
```

------------------------------------------------------------------------

# 36. User Experience

Ideal flow:

``` text
Open Tool
 ↓
Upload Image
 ↓
Choose Options
 ↓
Click Process
 ↓
Show Progress
 ↓
Preview Result
 ↓
Download
 ↓
Offer next action
```

Do not force account creation before basic free usage unless necessary.

------------------------------------------------------------------------

# 37. Conversion Strategy

AI tools should naturally introduce premium upgrades.

Example:

``` text
Free Result
 ↓
"Download HD"
 ↓
Premium Upgrade
```

Or:

``` text
5 images processed
 ↓
"Continue with 100-image batch"
 ↓
Premium
```

Upgrade prompts must not make the free tool unusable.

------------------------------------------------------------------------

# 38. AI History

Authenticated users can view:

``` text
My AI Jobs
 ├── Completed
 ├── Processing
 ├── Failed
 └── Expired
```

Each history item can show:

-   tool
-   date
-   thumbnail
-   processing status
-   output
-   download
-   delete

Premium users can receive longer retention.

------------------------------------------------------------------------

# 39. Privacy

The platform should clearly communicate:

-   what files are stored
-   how long files are retained
-   whether AI providers receive files
-   whether files are used for model training
-   when files are automatically deleted

Do not claim privacy properties that the actual implementation does not
provide.

------------------------------------------------------------------------

# 40. Observability

AI workers must expose metrics such as:

``` text
jobs_total
jobs_completed
jobs_failed
jobs_processing
average_processing_time
queue_depth
model_error_rate
gpu_utilization
cpu_utilization
memory_usage
storage_usage
estimated_ai_cost
```

Use centralized logs and monitoring.

------------------------------------------------------------------------

# 41. Failure Handling

Possible failure types:

``` text
INVALID_FILE
UNSUPPORTED_FORMAT
FILE_TOO_LARGE
MODEL_TIMEOUT
MODEL_ERROR
INSUFFICIENT_CREDITS
QUOTA_EXCEEDED
STORAGE_ERROR
WORKER_UNAVAILABLE
PROVIDER_ERROR
```

Errors should be converted into user-friendly messages.

Never expose internal stack traces to users.

------------------------------------------------------------------------

# 42. Abuse Prevention

AI tools can be abused for:

-   excessive processing
-   automated requests
-   resource exhaustion
-   storage abuse
-   account sharing

Controls:

-   IP rate limiting
-   account rate limiting
-   daily quotas
-   concurrency limits
-   file limits
-   CAPTCHA where necessary
-   suspicious activity detection
-   API rate limits

------------------------------------------------------------------------

# 43. Anonymous Users

Free tools can support anonymous users where economically safe.

Use:

``` text
IP/device/session based limits
```

However, anonymous usage should have stricter limits than authenticated
users.

------------------------------------------------------------------------

# 44. API Access

Future premium API:

``` text
POST /api/v1/public/ai/background-removal
POST /api/v1/public/ai/upscale
POST /api/v1/public/ai/enhance
```

API users require:

-   API keys
-   rate limits
-   usage tracking
-   monthly quotas
-   billing
-   documentation
-   key revocation
-   security controls

------------------------------------------------------------------------

# 45. AI API Key Security

Never expose private provider API keys in:

-   frontend JavaScript
-   browser requests
-   public repositories
-   logs

Use environment variables / secret management.

------------------------------------------------------------------------

# 46. Development Strategy

Do not build every AI feature simultaneously.

Recommended phases:

## Phase 1 --- Foundation

Build:

-   AI tool registry
-   AI job model
-   queue
-   worker
-   storage
-   usage tracking
-   basic monitoring

## Phase 2 --- First High-Demand Tools

Start with:

1.  Background Remover
2.  Image Upscaler
3.  Photo Enhancer
4.  Image Compressor
5.  Image Converter
6.  Image Resizer

## Phase 3 --- Monetization

Add:

-   credits
-   subscription limits
-   premium resolution
-   batch processing
-   processing priority
-   history

## Phase 4 --- Advanced AI

Add:

-   object removal
-   product background generation
-   restoration
-   deblurring
-   AI image editing

## Phase 5 --- API

Add:

-   API keys
-   developer dashboard
-   API usage
-   API billing
-   documentation

------------------------------------------------------------------------

# 47. Recommended Initial AI Product Strategy

The first AI products should satisfy three conditions:

1.  High search demand
2.  Strong repeat usage
3.  Clear premium value

Priority:

``` text
1. Background Remover
2. Image Upscaler
3. Photo Enhancer
4. Object Remover
5. Product Background Generator
6. Image Restoration
```

These can later share the same underlying processing infrastructure.

------------------------------------------------------------------------

# 48. Architecture Must Support Future Growth

The system must be capable of evolving from:

``` text
1 AI tool
```

to:

``` text
10 AI tools
```

then:

``` text
50+ AI tools
```

without creating separate architectures for every tool.

The correct abstraction is:

``` text
Tool
 ↓
Job
 ↓
Queue
 ↓
Worker
 ↓
Model Adapter
 ↓
Model
 ↓
Storage
 ↓
Result
```

------------------------------------------------------------------------

# 49. Scalability Path

### Stage 1

``` text
Single application server
+
Redis
+
Celery
+
Single worker
+
Object storage
```

### Stage 2

``` text
Web servers
+
Redis
+
Multiple CPU workers
+
Multiple AI workers
+
Object storage
```

### Stage 3

``` text
Load Balancer
+
Auto-scaled API
+
Dedicated queues
+
CPU worker cluster
+
GPU worker cluster
+
Object storage
+
Monitoring
```

### Stage 4

``` text
Multi-region / distributed processing
+
Dedicated model infrastructure
+
Advanced autoscaling
+
Cost optimization
```

------------------------------------------------------------------------

# 50. Important Architectural Rules

AI coding agents must follow these rules:

1.  Never put AI processing directly inside Django request handlers.
2.  Never hard-code a single AI provider into the entire application.
3.  Never expose provider API keys to the frontend.
4.  Never trust uploaded file extensions.
5.  Always validate file type and size.
6.  Always enforce user quotas.
7.  Always record AI usage.
8.  Always track processing cost where possible.
9.  Always use asynchronous processing for heavy jobs.
10. Always make model selection configurable.
11. Always isolate CPU and GPU workloads when necessary.
12. Always clean temporary files.
13. Always use secure download URLs for private files.
14. Always make failed jobs observable.
15. Always design batch processing separately from single-file
    processing.
16. Never let a single user exhaust worker resources.
17. Never make frontend code responsible for subscription enforcement.
18. Never assume an external AI API will always be available.
19. Keep AI model adapters replaceable.
20. Keep business rules configurable from the backend.

------------------------------------------------------------------------

# 51. Definition of Done

The AI architecture is considered production-ready when:

-   [ ] AI jobs are asynchronous
-   [ ] Queue system is operational
-   [ ] CPU workers are operational
-   [ ] GPU strategy is defined
-   [ ] Model adapters exist
-   [ ] AI tool registry exists
-   [ ] File validation exists
-   [ ] Secure storage exists
-   [ ] Signed downloads exist
-   [ ] Quotas exist
-   [ ] Credit system exists
-   [ ] Usage tracking exists
-   [ ] Cost tracking exists
-   [ ] Retry mechanism exists
-   [ ] Timeout handling exists
-   [ ] Failure handling exists
-   [ ] Batch processing exists
-   [ ] Monitoring exists
-   [ ] Rate limiting exists
-   [ ] Subscription integration exists
-   [ ] AI history exists
-   [ ] Data retention policy exists
-   [ ] API architecture is extensible
-   [ ] New AI models can be added without rewriting the application

------------------------------------------------------------------------

# 52. Final Architecture

The final conceptual architecture is:

``` text
                         USER
                           │
                           ▼
                    NEXT.JS FRONTEND
                           │
                           ▼
                    DJANGO REST API
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       AUTH          SUBSCRIPTION        USAGE
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                  AI PROCESSING MANAGER
                           │
                           ▼
                      JOB QUEUE
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        CPU WORKERS                 GPU WORKERS
              │                         │
              └────────────┬────────────┘
                           ▼
                     MODEL ADAPTERS
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          LOCAL AI     EXTERNAL API   FUTURE MODEL
              │            │            │
              └────────────┼────────────┘
                           ▼
                     OUTPUT STORAGE
                           │
                           ▼
                    SECURE DOWNLOAD
                           │
                           ▼
                         USER
```

This architecture is intentionally designed for incremental development:
launch a small number of profitable AI tools first, validate traffic and
subscription demand, then add models and tools without replacing the
core system.
