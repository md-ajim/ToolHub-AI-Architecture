# 26 --- Application Workspace Architecture

**Updated Version:** 2.0\
**Supersedes:** Updated for AI Multi-Model Workspace\
**Status:** Updated Product / UX / Architecture Specification

> Additive update: existing tools and compatible architecture remain
> unless explicitly deprecated.

------------------------------------------------------------------------

## v2.0 Addendum --- Minimal Unified Application Shell

Replace the stacked shell:

``` text
Public Header
↓
Primary Navigation
↓
Workspace Navigation
↓
Main Workspace
```

with:

``` text
Minimal Application Header
↓
Workspace Sidebar / Tool Rail
↓
Main Workspace
↓
Contextual Panels
```

### AI Workspace navigation

``` text
+ New Chat
Models
Projects

RECENT
  Conversations...

Settings
Help
Account
```

Global Search remains in the compact application header.

-   Sidebar owns workspace destinations.
-   Header owns global utilities.
-   Contextual surfaces own temporary capabilities.
-   `Compare` is contextual, not permanent global navigation.
-   `Usage` belongs to Account/Profile or contextual account surfaces.
-   Projects must not be duplicated across navigation layers.

Existing authentication, projects, files, history, usage, subscription
and editor architecture remain valid.

------------------------------------------------------------------------

**Project:** Multi-Tool Utility / Micro-SaaS Platform\
**Document:** Application Workspace & Persistent Product Architecture\
**Version:** 1.0\
**Status:** Core Product Architecture\
**Priority:** Critical

------------------------------------------------------------------------

## 1. Purpose

This document defines how the platform evolves from a collection of web
tools into a cohesive browser-based software platform.

The public website remains the primary discovery and SEO layer.

The authenticated application becomes a persistent workspace where users
can:

-   Create
-   Edit
-   Process
-   Save
-   Organize
-   Reuse
-   Export

their work across multiple tools.

The long-term goal is:

``` text
One Platform
+
One Account
+
One Workspace
+
Many Tools
```

------------------------------------------------------------------------

## 2. Product Experience Model

The intended experience is:

``` text
Google / Direct Visit
        ↓
Public Tool Page
        ↓
Use Tool
        ↓
Application Workspace
        ↓
Project / File Context
        ↓
Multiple Tools
        ↓
Save / History
        ↓
Export
```

The user should be able to move between relevant tools without losing
useful context.

------------------------------------------------------------------------

## 3. Public Website vs Application

### Public Website

Optimized for:

``` text
SEO
Discovery
Free usage
Marketing
Education
Tool browsing
Conversion
```

Examples:

``` text
/
/tools
/tools/[tool]
/category/[category]
/pricing
/blog
```

### Application

Optimized for:

``` text
Productivity
Persistence
Editing
Projects
Files
History
Subscription
Personalization
```

Examples:

``` text
/dashboard
/workspace
/workspace/[projectId]
/dashboard/history
/dashboard/files
/dashboard/settings

/workspace/ai

/workspace/ai/[conversationId]

/workspace/ai

/workspace/ai/[conversationId]
```

------------------------------------------------------------------------

## 4. Application Workspace Principle

The authenticated application should feel like software.

Example:

``` text
My Workspace
├── Recent Work
├── Projects
├── Files
├── AI Results
├── Favorites
├── Saved Presets
└── History
```

The AI Workspace is a first-class persistent application surface for
multi-model conversations, compare runs and permitted file context. It
shares the workspace's projects, private-file ownership and subscription
rules, while its model routing and provider integration remain in the AI
Gateway. See `32-ai-workspace-architecture.md`.

The platform should remember useful user context without persisting
unnecessary transient UI state.

------------------------------------------------------------------------

## 5. Workspace Entry Points

Users may enter the workspace from:

``` text
Dashboard
Tool Page
Editor
History
Project
Recent Work
Saved File
```

Example:

``` text
Public Tool
↓
Upload
↓
Editor
↓
Save as Project
↓
Workspace
```

------------------------------------------------------------------------

## 6. Dashboard

Primary authenticated entry:

``` text
/dashboard
```

The dashboard should prioritize work, not meaningless statistics.

Recommended:

``` text
Welcome / Context
↓
Quick Actions
↓
Continue Working
↓
Recent Files
↓
Recent Projects
↓
Usage / Credits
↓
Recommended Tools
```

------------------------------------------------------------------------

## 7. Continue Working

The dashboard should surface unfinished or recently used work.

Example:

``` text
Continue Working

Product Photo Project
Updated 10 minutes ago

[Open]
```

This creates a persistent software-like experience.

------------------------------------------------------------------------

## 8. Recent Work

Recent work may include:

``` text
Recently opened projects
Recently edited files
Recent AI jobs
Recent exports
```

Every item should provide a direct reopen action where possible.

------------------------------------------------------------------------

## 9. Workspace

Base route:

``` text
/workspace
```

Purpose:

``` text
File organization
Project organization
Persistent editing
Cross-tool workflows
Saved results
```

Potential navigation:

``` text
All
Projects
Files
AI Results
Exports
Favorites
Trash
```

Only expose sections that are implemented.

------------------------------------------------------------------------

## 10. Project Architecture

A project is a persistent user workspace.

Example:

``` text
Project
├── Source Files
├── Edited Versions
├── AI Results
├── Tool History
├── Exports
└── Project Settings
```

A single project may contain outputs from multiple tools.

------------------------------------------------------------------------

## 11. Cross-Tool Project Workflow

Example:

``` text
Product Image Project
        ↓
Original Upload
        ↓
Background Removal
        ↓
Image Enhancement
        ↓
Resize for Instagram
        ↓
Watermark
        ↓
Compress
        ↓
Export
```

The user should not need to create a new project for every operation.

------------------------------------------------------------------------

## 12. Persistent File Context

A file may move through multiple tools:

``` text
Original
 ↓
Resized Version
 ↓
Enhanced Version
 ↓
Background Removed Version
 ↓
Watermarked Version
 ↓
Final Export
```

The system should preserve these relationships where useful.

------------------------------------------------------------------------

## 13. File Relationships

Conceptual fields:

``` text
parent_file_id
project_id
source_job_id
version_number
origin_tool
```

These support:

``` text
History
Versioning
Project organization
Cross-tool workflows
```

The exact database implementation must remain aligned with the existing
domain model.

------------------------------------------------------------------------

## 14. Editor + Workspace

The editor is one part of the application workspace.

Flow:

``` text
Workspace
   ↓
Project
   ↓
Editor
   ↓
Tool
   ↓
Result
   ↓
Save
```

The editor should be able to open files from the workspace.

------------------------------------------------------------------------

## 15. Editor Session vs Project

These are different concepts.

### Editor Session

Temporary editing context:

``` text
Canvas state
Zoom
Selected tool
Temporary edits
```

### Project

Persistent user workspace:

``` text
Files
Edit versions
History
AI results
Saved state
```

Do not persist every transient UI state as permanent project data.

------------------------------------------------------------------------

## 16. Autosave

For persistent projects:

``` text
Edit
↓
Debounced Save
↓
Project State
```

Potential status:

``` text
Saving...
Saved
Save failed
```

Autosave should be debounced and should not generate unnecessary
requests.

------------------------------------------------------------------------

## 17. Manual Save

Where appropriate, support:

``` text
Save
Save As
Duplicate
```

Manual save should remain available even when autosave exists.

------------------------------------------------------------------------

## 18. Version History

Persistent projects may maintain:

``` text
Original
Version 1
Version 2
Version 3
Final
```

Potential actions:

``` text
Preview
Restore
Duplicate
Delete
```

Version retention may depend on subscription.

------------------------------------------------------------------------

## 19. Saved Presets

Users may save reusable configurations:

``` text
Image Resize Preset
Compression Preset
Social Media Preset
Export Preset
Watermark Preset
```

Conceptual:

``` text
Preset
├── owner
├── tool
├── name
├── configuration
└── created_at
```

------------------------------------------------------------------------

## 20. Favorites

Users may favorite:

``` text
Tools
Projects
Files
Presets
```

Favorites are a retention feature and should remain lightweight.

------------------------------------------------------------------------

## 21. Recent Tools

The workspace can remember recently used tools:

``` text
Image Resizer
Background Remover
PDF Compressor
```

Do not expose private activity publicly.

------------------------------------------------------------------------

## 22. Workspace Search

Authenticated users may search:

``` text
Files
Projects
Tools
Presets
History
```

Example:

``` text
Search "product photo"
```

Results can include:

``` text
Project
File
Tool
AI Result
Export
```

------------------------------------------------------------------------

## 23. Global Search vs Workspace Search

These are different systems.

### Global Search

Finds:

``` text
Public Tools
Categories
Public Content
```

### Workspace Search

Finds:

``` text
Private Files
Projects
History
Presets
Results
```

Private workspace data must never leak into public search results.

------------------------------------------------------------------------

## 24. File Organization

Support organization through:

``` text
Projects
Folders where justified
Tags where justified
Favorites
```

Do not force users to manually organize every file.

------------------------------------------------------------------------

## 25. Workspace Navigation

Recommended:

``` text
Overview
Projects
Files
AI Results
History
Favorites
Presets
Trash
```

The final navigation should remain consistent with the application route
architecture.

------------------------------------------------------------------------

## 26. Trash

Persistent files may support:

``` text
Delete
↓
Trash
↓
Restore
↓
Permanent Delete
```

Temporary processing files should follow automatic retention policies
instead of requiring manual trash management.

------------------------------------------------------------------------

## 27. File Sharing

Future sharing may support:

``` text
Share
↓
Permission
↓
Secure Link
↓
Expiration
```

Potential permissions:

``` text
View
Download
Edit
```

Do not implement collaboration complexity before the product needs it.

------------------------------------------------------------------------

## 28. Cross-Tool Actions

After a successful operation, offer logical next tools.

Example:

``` text
Background Removed
        ↓
[Resize]
[Compress]
[Add Watermark]
[Convert]
```

This creates a cohesive tool ecosystem.

------------------------------------------------------------------------

## 29. File Handoff

Future user-facing action:

``` text
Open With
```

Example:

``` text
Image
→ Open with Resizer
→ Open with Cropper
→ Open with Watermark
→ Open with Enhancer
```

The source file remains available.

------------------------------------------------------------------------

## 30. Tool Chains

Advanced workflows may become:

``` text
Tool A
↓
Tool B
↓
Tool C
↓
Tool D
```

Example:

``` text
Remove Background
↓
Enhance
↓
Resize
↓
Compress
```

The current file/version context should be preserved where technically
appropriate.

------------------------------------------------------------------------

## 31. Workflow Persistence

Future capability:

``` text
Workflow
├── Step 1: Background Removal
├── Step 2: Resize
├── Step 3: Watermark
└── Step 4: Export
```

This is a future feature. Do not overbuild it during the initial product
phase.

------------------------------------------------------------------------

## 32. State Architecture

Separate:

``` text
UI State
Server State
Project State
File State
Subscription State
Processing State
```

Do not put all application state in a single global client store.

------------------------------------------------------------------------

## 33. Client State vs Server State

### Client State

Examples:

``` text
Sidebar open
Current tab
Canvas zoom
Selected tool
Temporary inspector state
```

### Server State

Examples:

``` text
Projects
Files
Subscriptions
Credits
History
AI Jobs
Presets
```

------------------------------------------------------------------------

## 34. Connection State

Workspace may support:

``` text
Online
Offline
Reconnecting
Save Pending
Save Failed
```

Do not claim full offline editing unless it is actually implemented.

------------------------------------------------------------------------

## 35. Recovery

If saving fails:

``` text
Retry
Keep unsaved state where possible
Inform the user
Recover the session where possible
```

Never silently discard user work.

------------------------------------------------------------------------

## 36. Notifications

Useful application notifications:

``` text
AI job completed
Export ready
Subscription updated
Storage limit reached
Processing failed
Save completed
```

Notifications must be meaningful and not spam the user.

------------------------------------------------------------------------

## 37. AI Job Center

Long-running jobs may be exposed through:

``` text
/dashboard/history
```

or, if justified:

``` text
/dashboard/ai-jobs
```

Potential states:

``` text
Queued
Processing
Completed
Failed
Canceled
```

Do not add a separate page unless the usage volume justifies it.

------------------------------------------------------------------------

## 38. Workspace + AI Integration

Example:

``` text
Project
 ↓
Open Image
 ↓
AI Background Removal
 ↓
AI Job
 ↓
Result
 ↓
Save Version
 ↓
Continue Editing
```

AI outputs should become normal project/file assets where appropriate.

------------------------------------------------------------------------

## 39. Workspace + Subscription

Subscription may affect:

``` text
Storage
AI Credits
History Retention
Project Limits
Advanced Editor Capabilities
Large Files
Premium Exports
```

The backend remains authoritative.

------------------------------------------------------------------------

## 40. Workspace + Credits

Before expensive operations, users should be able to see:

``` text
Current Balance
Estimated Cost
Remaining Balance
```

Credits must be enforced server-side.

------------------------------------------------------------------------

## 41. Usage

The workspace may show:

``` text
Storage
AI Credits
Tool Usage
Processing Count
Projects
```

Users should understand their current usage and limits.

------------------------------------------------------------------------

## 42. Security

Private workspace data must require:

``` text
Authentication
Authorization
Object Ownership
Signed File Access
Server-side Entitlements
Rate Limits
```

A private project URL must never grant access by itself.

------------------------------------------------------------------------

## 43. Performance

Do not load all workspace data at once.

Use:

``` text
Pagination
Infinite Loading where useful
Search
Filtering
Lazy Loading
Virtualization for very large collections
```

------------------------------------------------------------------------

## 44. Workspace Route Architecture

Conceptual:

``` text
/workspace
├── Overview
├── Projects
├── Files
├── AI Results
├── History
├── Favorites
├── Presets
└── Trash
```

The exact route structure must remain synchronized with
`17-page-and-route-architecture.md`.

------------------------------------------------------------------------

## 45. Project Page

Route:

``` text
/workspace/[projectId]
```

Recommended:

``` text
Project Header
↓
Project Files
↓
Recent Results
↓
Continue Editing
↓
Project History
↓
Exports
```

------------------------------------------------------------------------

## 46. Project Header

Potential:

``` text
Back
Project Name
Rename
Share
More
```

Keep project actions unobtrusive.

------------------------------------------------------------------------

## 47. Workspace Empty State

For a new account:

``` text
Welcome to your workspace

Start with a tool or create a project.

[Explore Tools]
[Create Project]
```

The empty state should guide the user toward their first useful action.

------------------------------------------------------------------------

## 48. Recent Work Card

Display:

``` text
Thumbnail
Name
Last Updated
Current Tool
Status
```

Primary action:

``` text
Continue
```

------------------------------------------------------------------------

## 49. Quick Actions

Potential actions:

``` text
New Project
Upload File
Open Recent
Explore Tools
```

Prioritize frequent tasks.

------------------------------------------------------------------------

## 50. Application Onboarding

Do not force long onboarding.

A lightweight first-use flow may communicate:

``` text
Upload
Edit
Save
Export
```

The interface should teach users through use.

------------------------------------------------------------------------

## 51. Tool Discovery Inside Workspace

Users should be able to access:

``` text
Tools
Categories
Search
Recent
Favorites
```

without leaving the application unnecessarily.

------------------------------------------------------------------------

## 52. Persistent Context

Where useful, preserve:

``` text
Current Project
Selected File
Last Used Tool
Relevant Presets
```

Do not carry context that can confuse users.

------------------------------------------------------------------------

## 53. Session Recovery

If a user closes the browser during a persistent edit:

``` text
Return
↓
Open Project
↓
Continue
```

This is a key part of the software-like experience.

------------------------------------------------------------------------

## 54. Export Management

Exports may be discoverable through:

``` text
Project
History
Files
```

Avoid unnecessary file duplication.

------------------------------------------------------------------------

## 55. Data Lifecycle

Project files may follow:

``` text
Created
↓
Edited
↓
Saved
↓
Used
↓
Archived / Deleted
↓
Trash
↓
Permanent Delete
```

Temporary processing files remain under short-retention policies.

------------------------------------------------------------------------

## 56. Workspace Analytics

Meaningful aggregate events may include:

``` text
workspace_opened
project_created
project_opened
file_opened
tool_switched
preset_saved
export_completed
workspace_abandoned
```

Do not collect unnecessary private content.

------------------------------------------------------------------------

## 57. Retention Model

Natural retention features include:

``` text
Projects
Recent Work
Saved Presets
History
Favorites
Cloud Files
Cross-tool Workflows
```

Every retention feature must provide actual utility.

------------------------------------------------------------------------

## 58. Workspace Monetization

Premium workspace value may include:

``` text
More Projects
More Storage
Longer History
More AI Credits
Advanced Editor
Large Files
Premium Presets
Priority Processing
Advanced Exports
```

Never make the free workspace meaningless.

------------------------------------------------------------------------

## 59. Free Workspace

A free account should still provide genuine value:

``` text
Basic Projects
Basic History
Basic Storage
Basic Tools
Limited AI
```

Exact limits are controlled by the entitlement architecture.

------------------------------------------------------------------------

## 60. Brand Principle

The workspace must not become a clone of another design product.

It should be:

``` text
Our Brand
+
Our Tools
+
Our Editor
+
Our Workspace
```

Professional software principles are reusable; competitor branding is
not.

------------------------------------------------------------------------

## 61. AI Coding Agent Rules

Before implementing workspace functionality, the AI must read:

``` text
17-page-and-route-architecture.md
18-ui-ux-design-system.md
19-page-design-specification.md
20-component-design-system.md
21-responsive-design-guidelines.md
22-ui-design-ai-guide.md
23-editor-design-system.md
24-editor-page-specification.md
25-editor-component-system.md
```

The AI must:

``` text
Reuse existing components
Reuse editor architecture
Keep public and application UX separate
Support dark/light themes
Support responsive layouts
Preserve project context
Avoid duplicated state systems
Keep authorization server-side
Keep billing enforcement server-side
Implement recovery for unsaved work
```

------------------------------------------------------------------------

## 62. Definition of Done

The application workspace foundation is complete when:

``` text
[ ] Dashboard exists
[ ] Workspace exists
[ ] Projects exist
[ ] Files can be associated with projects
[ ] Editor can open workspace files
[ ] Results can return to projects
[ ] Recent work exists
[ ] History exists
[ ] Favorites exist
[ ] Basic presets exist where required
[ ] Save/autosave behavior is defined
[ ] Recovery behavior exists where needed
[ ] Cross-tool handoff works where implemented
[ ] Authentication is enforced
[ ] File ownership is enforced
[ ] Subscription limits are enforced
[ ] AI credits are enforced
[ ] Responsive workspace exists
[ ] Dark/light mode works
[ ] Analytics events are defined
[ ] No unnecessary duplicate architecture exists
```

------------------------------------------------------------------------

## 63. Final Product Vision

The long-term experience should be:

``` text
Search
↓
Tool
↓
Editor
↓
Workspace
↓
Project
↓
Multiple Tools
↓
Saved Work
↓
Return Later
```

The user should not feel that they are visiting hundreds of unrelated
utilities.

They should feel that they are using:

> **One powerful online software platform containing many specialized
> tools.**

This architecture is the foundation for that experience.
