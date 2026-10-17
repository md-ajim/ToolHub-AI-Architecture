# 28 --- Tool Development Workflow

**Updated Version:** 1.1\
**Supersedes:** 1.0\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v1.1 Addendum --- Workspace-First Delivery Workflow

Updated lifecycle:

``` text
Specification
↓
Reuse Audit
↓
Architecture Review
↓
Workspace Integration Review
↓
UX/UI Plan
↓
Implementation
↓
Visual QA
↓
Production
```

Workspace review must verify Tool Registry placement, search/category
metadata, Tool Rail integration, Inspector capability, AI Gateway
integration where applicable, no duplicate navigation, no duplicate
components, and no removal of existing tools.

AI coding agents must read the relevant architecture and UX documents
before changing the workspace shell.

------------------------------------------------------------------------

**Project:** Multi-Tool Utility / Micro-SaaS Platform\
**Document:** Standard Tool Development & Delivery Workflow\
**Version:** 1.0\
**Status:** Core Engineering Process\
**Priority:** Critical\
**Depends On:** `27-tool-specification-system.md`

------------------------------------------------------------------------

## 1. Purpose

This document defines the standard workflow for developing, testing,
launching, and maintaining every tool on the platform.

The platform is designed to grow progressively:

``` text
10 tools
↓
25 tools
↓
50 tools
↓
100 tools
↓
250 tools
↓
500+ tools
```

The process must remain:

``` text
Predictable
Repeatable
Scalable
Testable
AI-agent-friendly
```

Every new tool should follow the same lifecycle.

------------------------------------------------------------------------

## 2. Core Principle

A tool must not be developed as an isolated mini-project.

The standard workflow is:

``` text
Tool Specification
↓
Reuse Audit
↓
Architecture Review
↓
UX/UI Plan
↓
Backend
↓
Processing
↓
Storage
↓
Entitlement / Usage
↓
Frontend
↓
Editor / Workspace Integration
↓
Analytics
↓
SEO
↓
Testing
↓
Security QA
↓
Visual QA
↓
Launch
↓
Monitoring
↓
Optimization
```

------------------------------------------------------------------------

## 3. Phase 0 --- Tool Selection

Before development begins, confirm:

``` text
Why are we building this tool?
Who needs it?
What problem does it solve?
Is there real user/search demand?
Does it duplicate an existing tool?
Can existing components/services be reused?
Can an existing editor capability support it?
Is it free, freemium, or premium?
```

Do not build a tool merely because it sounds interesting.

------------------------------------------------------------------------

## 4. Phase 1 --- Tool Specification

Create:

``` text
docs/tools/[tool-slug].md
```

Examples:

``` text
docs/tools/image-resizer.md
docs/tools/background-remover.md
docs/tools/pdf-compressor.md
```

The specification must follow:

``` text
27-tool-specification-system.md
```

Do not start implementation until the required product and technical
decisions are documented.

------------------------------------------------------------------------

## 5. Phase 2 --- Similarity & Reuse Audit

Inspect the repository for:

``` text
Existing Components
Existing APIs
Existing Services
Existing Editors
Existing Uploaders
Existing Result Panels
Existing Storage Services
Existing AI Services
Existing Entitlement Services
Existing Analytics
Existing SEO Components
Existing Tool Registry
```

Ask:

``` text
Can an existing tool be extended?
Can an existing component be reused?
Can an existing editor capability support it?
Can an existing backend service process it?
```

Avoid duplicate architecture.

------------------------------------------------------------------------

## 6. Phase 3 --- Tool Classification

Assign one level:

``` text
Level 1 — Simple Utility
Level 2 — Interactive Tool / Editor
Level 3 — Advanced Editor / Workspace
```

Examples:

``` text
JSON Formatter
→ Level 1

Image Resizer
→ Level 2

Product Image Editor
→ Level 3
```

Complexity must match actual user needs.

------------------------------------------------------------------------

## 7. Phase 4 --- Architecture Review

Verify:

``` text
Frontend Route
Backend Endpoint
Domain Model
Database Changes
Storage
Processing
AI
Queue
Authentication
Authorization
Entitlement
Credits / Usage
Analytics
SEO
```

The tool must fit the existing platform architecture.

------------------------------------------------------------------------

## 8. Phase 5 --- UX Flow

Define the main user journey.

Simple tool:

``` text
Open
↓
Input
↓
Configure
↓
Process
↓
Result
↓
Export
```

Editor tool:

``` text
Open
↓
Upload
↓
Canvas
↓
Select Tool
↓
Edit
↓
Preview
↓
Export
```

Keep the critical path as short as practical.

------------------------------------------------------------------------

## 9. Phase 6 --- UI Design

Use:

``` text
18-ui-ux-design-system.md
19-page-design-specification.md
20-component-design-system.md
21-responsive-design-guidelines.md
22-ui-design-ai-guide.md
```

For editor tools additionally use:

``` text
23-editor-design-system.md
24-editor-page-specification.md
25-editor-component-system.md
```

For multi-model chat, research or file-context features additionally
use:

``` text
32-ai-workspace-architecture.md
```

The UI must reuse:

``` text
Shared Design Tokens
Shared Components
Shared Navigation
Shared Tool Patterns
```

------------------------------------------------------------------------

## 10. Phase 7 --- Route Setup

Create the public route:

``` text
/tools/[tool]
```

For complex editing:

``` text
/tools/[tool]/editor
```

Remember:

``` text
Public Tool Page
→ SEO / Discovery

Editor Workspace
→ Focused Application Experience
```

Do not mix their responsibilities.

------------------------------------------------------------------------

## 11. Phase 8 --- Backend Foundation

Typical server-backed flow:

``` text
Request
↓
Validation
↓
Authentication
↓
Authorization
↓
Entitlement
↓
Usage / Credit Check
↓
Domain Service
↓
Processing
↓
Storage
↓
Response
```

Keep business logic out of views/controllers whenever possible.

------------------------------------------------------------------------

## 12. Phase 9 --- Domain Logic

Create or reuse services such as:

``` text
ImageProcessingService
CompressionService
ConversionService
AIProcessingService
ExportService
```

The tool should orchestrate reusable services rather than duplicate
their internal logic.

------------------------------------------------------------------------

## 13. Phase 10 --- Processing Strategy

Choose deliberately:

``` text
Browser
Server
Celery Worker
AI Service
Hybrid
```

Guideline:

``` text
Lightweight client-side task
→ Browser

Heavy CPU/GPU task
→ Worker

AI task
→ Async AI Job + Worker

Bulk processing
→ Async job system
```

Do not perform heavy work synchronously inside ordinary API requests.

------------------------------------------------------------------------

## 14. Phase 11 --- Storage Integration

For file-based tools:

``` text
Upload
↓
Object Storage
↓
Processing
↓
Output
↓
Object Storage
↓
Download / Workspace
```

Follow:

``` text
13-storage-file-management-architecture.md
```

Do not use the production application filesystem as permanent user
storage.

------------------------------------------------------------------------

## 15. Phase 12 --- Authentication & Authorization

Determine:

``` text
Anonymous
Authenticated
Premium
Business
Enterprise
```

Enforce permissions server-side.

Never trust frontend-supplied:

``` text
Plan
Credits
Permissions
File ownership
```

------------------------------------------------------------------------

## 16. Phase 13 --- Entitlement Integration

Every premium-aware tool uses the centralized entitlement architecture.

Concept:

``` text
Tool Request
↓
EntitlementService
↓
Allowed / Denied
```

Do not scatter plan-specific logic throughout the application.

Avoid patterns such as:

``` python
if user.plan == "pro":
    ...
```

when a centralized entitlement service can answer the question.

------------------------------------------------------------------------

## 17. Phase 14 --- Usage & Credits

If a tool consumes usage or credits:

``` text
Check
↓
Reserve
↓
Process
↓
Finalize
```

On failure:

``` text
Processing Fails
↓
Release / Refund Reservation
```

Credit operations must be atomic and safe under concurrent requests.

------------------------------------------------------------------------

## 18. Phase 15 --- API

For server-backed tools define:

``` text
Method
Endpoint
Authentication
Request
Response
Errors
Rate Limits
```

Follow:

``` text
08-api-design.md
```

Responses should be predictable and versionable.

------------------------------------------------------------------------

## 19. Phase 16 --- Frontend Integration

Implement:

``` text
Input
Validation
Tool UI
Loading
Processing
Result
Export
Error
```

Reuse existing components such as:

``` text
FileUploader
ToolWorkspace
ResultPanel
ProcessingState
DownloadButton
```

where applicable.

------------------------------------------------------------------------

## 20. Phase 17 --- Editor Integration

For Level 2/3 image tools:

``` text
EditorShell
↓
Capability Configuration
↓
Tool-specific Logic
```

Do not create a new editor shell for every image feature.

Example:

``` text
Social Resizer
→ ResizeControls
→ CropControls
→ PresetSelector
→ ExportPanel
```

------------------------------------------------------------------------

## 21. Phase 18 --- Workspace Integration

Ask:

``` text
Can the result be saved to a project?
Can the file be reopened later?
Can it be opened in another tool?
Can the current project context be preserved?
```

Example:

``` text
Background Removal
↓
Resize
↓
Watermark
↓
Compress
↓
Export
```

Use:

``` text
26-application-workspace-architecture.md
```

for persistent workflows.

------------------------------------------------------------------------

## 22. Phase 19 --- Cross-Tool Integration

Where meaningful, provide logical next actions.

Example:

``` text
Background Removed
↓
[Resize]
[Compress]
[Watermark]
[Convert]
```

The product should behave like one application rather than unrelated
utilities.

------------------------------------------------------------------------

## 23. Phase 20 --- State Implementation

Implement all relevant states:

``` text
Initial
Uploading
Validating
Processing
Success
Error
Empty
Limit Reached
Premium Required
Insufficient Credits
Unsupported Input
```

Do not implement only the happy path.

------------------------------------------------------------------------

## 24. Phase 21 --- Responsive Implementation

Test:

``` text
Mobile
Tablet
Desktop
Large Desktop
Landscape
Touch
```

For editor tools:

``` text
Desktop Editor
Tablet Editor
Mobile Editor
```

Follow:

``` text
21-responsive-design-guidelines.md
```

------------------------------------------------------------------------

## 25. Phase 22 --- Theme Implementation

Verify:

``` text
Light
Dark
System
```

Tool-specific styling must not break semantic theme tokens.

------------------------------------------------------------------------

## 26. Phase 23 --- SEO Implementation

Public tool pages should include where applicable:

``` text
Title
Description
Canonical
Open Graph
Structured Data
Internal Links
FAQ
Useful SEO Content
```

SEO content must not overwhelm the actual tool.

------------------------------------------------------------------------

## 27. Phase 24 --- Analytics

Add meaningful events:

``` text
tool_viewed
tool_started
file_uploaded
processing_started
processing_completed
processing_failed
export_started
export_completed
upgrade_required
upgrade_clicked
tool_abandoned
```

Editor tools may additionally track:

``` text
editor_opened
editor_tool_selected
edit_started
edit_completed
```

Do not collect unnecessary sensitive content.

------------------------------------------------------------------------

## 28. Phase 25 --- Testing

Minimum tests:

``` text
Valid Input
Invalid Input
Empty Input
Unsupported Input
Large Input
Authentication
Authorization
Entitlement
Usage Limit
Credits
Processing Failure
Success
Export
```

Editor tools additionally:

``` text
Canvas
Resize
Crop
Zoom
Undo
Redo
Mobile
Desktop
```

------------------------------------------------------------------------

## 29. Phase 26 --- Security QA

Check:

``` text
Authentication bypass
Authorization bypass
File ownership
Premium bypass
Credit bypass
Rate-limit bypass
Malicious uploads
Path traversal
Signed URL security
Webhook interactions where relevant
```

Frontend restrictions are not security boundaries.

------------------------------------------------------------------------

## 30. Phase 27 --- Performance QA

Check:

``` text
Initial Page Load
JavaScript Size
Memory Usage
Upload Performance
Processing Time
API Latency
Export Time
Mobile Performance
```

Use profiling tools where necessary.

------------------------------------------------------------------------

## 31. Phase 28 --- Visual QA

The actual rendered page must be inspected.

Workflow:

``` text
Implement
↓
Run Application
↓
Render / Screenshot
↓
Inspect
↓
Fix
↓
Render Again
```

Inspect:

``` text
Spacing
Alignment
Typography
CTA hierarchy
Canvas size
Inspector width
Dark mode
Light mode
Mobile
Tablet
Desktop
```

Do not declare UI complete from code inspection alone.

------------------------------------------------------------------------

## 32. Phase 29 --- Content QA

Verify:

``` text
Tool Name
Description
Labels
Error Messages
Help Text
SEO Content
FAQ
Supported Formats
File Limits
Premium Messaging
```

Never fabricate product claims.

------------------------------------------------------------------------

## 33. Phase 30 --- Admin Integration

Where applicable, add admin controls for:

``` text
Tool Status
Tool Limits
SEO Metadata
Usage Monitoring
Job Monitoring
Feature Flags
```

Follow:

``` text
15-Admin-Panel-Architecture.md
```

------------------------------------------------------------------------

## 34. Phase 31 --- Feature Flag / Beta

New tools may move through:

``` text
Draft
Internal
Beta
Active
Deprecated
```

Use gradual rollout only where justified.

------------------------------------------------------------------------

## 35. Phase 32 --- Documentation

Update relevant documentation when architecture changes:

``` text
Tool Specification
API Documentation
Architecture Documentation
Tool Registry
Navigation
SEO configuration
AI Developer Guide when necessary
```

Documentation must remain synchronized with implementation.

------------------------------------------------------------------------

## 36. Phase 33 --- Launch Preparation

Verify:

``` text
Production Build
Database Migrations
Environment Variables
Object Storage
Queues
Workers
Monitoring
Analytics
SEO
Sitemap
Robots
Error Tracking
```

Perform a production-like test before launch.

------------------------------------------------------------------------

## 37. Phase 34 --- Launch

Recommended:

``` text
Internal Test
↓
Beta
↓
Production
↓
Monitor
↓
Fix
↓
Optimize
```

Do not launch high-cost AI features without monitoring compute and
provider costs.

------------------------------------------------------------------------

## 38. Phase 35 --- Post-Launch Monitoring

Monitor:

``` text
Usage
Errors
Processing Failures
Latency
Storage
AI Cost
Conversion
Abandonment
User Feedback
```

Useful metrics:

``` text
Tool Completion Rate
Export Rate
Return Usage
Upgrade Rate
Failure Rate
```

------------------------------------------------------------------------

## 39. Phase 36 --- Optimization

Improve based on evidence:

``` text
UX
Speed
SEO
Conversion
Reliability
Processing Cost
Retention
```

Do not add complexity simply to increase feature count.

------------------------------------------------------------------------

## 40. End-to-End Workflow

``` text
Tool Idea
   ↓
Tool Specification
   ↓
Reuse Audit
   ↓
Architecture Review
   ↓
UX Design
   ↓
Route
   ↓
Backend
   ↓
Domain Services
   ↓
Storage / Processing
   ↓
Entitlement / Credits
   ↓
Frontend
   ↓
Editor / Workspace Integration
   ↓
Responsive
   ↓
SEO
   ↓
Analytics
   ↓
Tests
   ↓
Security QA
   ↓
Visual QA
   ↓
Beta
   ↓
Production
   ↓
Monitoring
   ↓
Optimization
```

------------------------------------------------------------------------

## 41. AI Coding Agent Workflow

When an AI agent receives a new tool request, it must:

``` text
1. Read 27-tool-specification-system.md.
2. Read the tool's individual specification.
3. Read relevant global architecture.
4. Search existing components and services.
5. Search for similar tools.
6. Create an implementation plan.
7. Get approval before major architectural changes.
8. Implement incrementally.
9. Run tests.
10. Perform visual QA.
11. Report changed files and results.
12. Stop at the requested phase.
```

The AI agent must not silently redesign the architecture.

------------------------------------------------------------------------

## 42. Small Tool Rule

For simple tools, use the lightest architecture that meets the
requirement.

Example:

``` text
JSON Formatter
```

should not require:

``` text
Celery
AI
S3
Complex Project System
```

unless there is a real requirement.

------------------------------------------------------------------------

## 43. Heavy Tool Rule

For resource-intensive tools:

``` text
AI
Large PDF
Large Images
Bulk Processing
```

use:

``` text
Async Processing
Queue
Worker
Object Storage
Monitoring
Usage Controls
```

------------------------------------------------------------------------

## 44. Editor Rule

For image tools:

``` text
Simple operation
→ Level 1

Interactive operation
→ Level 2

Advanced creative workflow
→ Level 3
```

Do not force a full professional editor onto a simple utility.

------------------------------------------------------------------------

## 45. Free Tool Rule

Whenever practical:

``` text
Core Utility
→ Free
```

Premium should primarily monetize:

``` text
Scale
Quality
Speed
Automation
Storage
Advanced AI
Bulk Processing
Professional Workflow
```

Do not intentionally make a free tool unusable.

------------------------------------------------------------------------

## 46. Launch Quality Gate

A tool cannot be marked:

``` text
READY
```

until:

``` text
Product
UX
Frontend
Backend
Processing
Storage
Security
Entitlement
Analytics
SEO
Testing
Visual QA
```

have all been reviewed.

------------------------------------------------------------------------

## 47. Final Principle

Every new tool should become part of the existing platform.

The preferred implementation is:

``` text
New Tool
+
Existing Design System
+
Existing Components
+
Existing Services
+
Existing Editor
+
Existing Workspace
+
Existing Entitlement
+
Existing Analytics
```

not:

``` text
New Tool
+
New Architecture
+
New UI System
+
New Upload System
+
New Billing Logic
+
New Analytics
```

The long-term objective is:

> **Launch tools quickly without sacrificing the quality, consistency,
> scalability, and software-like experience of the platform.**
