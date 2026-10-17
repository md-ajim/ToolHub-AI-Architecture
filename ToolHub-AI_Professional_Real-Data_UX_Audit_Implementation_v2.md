# ToolHub-AI — Production UX, Real-Data & Functional Integrity Audit / Implementation Specification

**Document type:** Production implementation blueprint  
**Project:** ToolHub-AI  
**Scope:** Editor UI/UX, authenticated dashboard, real-data integrity, utility tools, PDF tools, AI workspace, favicon generator, SEO tools, responsive/accessibility QA  
**Priority:** Production / international SaaS quality  
**Status:** Implementation-ready specification — v2  
**Prepared:** 2026-10-02  
**P0 additions:** File visualization, AI structured output rendering, artifact persistence and download integrity

---

## 0. Executive Summary

ToolHub-AI should be treated as a real international SaaS product, not as a collection of visually polished pages.

The central requirement of this audit is:

> **Every visible UI state must be backed by real application state, real API behavior, real persistence, or an explicitly documented derived state. No fake counters, placeholder records, optimistic subscription states, hardcoded user information, dead buttons, simulated folders, or decorative data may remain in production UI.**

The current work should therefore be split into two equally important tracks:

1. **Functional integrity**
   - real user data
   - real authentication/session state
   - real files/folders
   - real projects
   - real history
   - real settings
   - real AI model availability
   - real exports/downloads
   - real persistence
   - real loading/error/empty states

2. **Premium product experience**
   - coherent design system
   - professional editor sidebar/Inspector
   - polished utility tools
   - strong typography and spacing
   - consistent icons
   - accessible interactions
   - responsive layouts
   - smooth but restrained motion
   - high-quality empty/loading/error states
   - predictable navigation
   - no visual inconsistency between tools

A public check of the production Object Remover URL currently exposes a simple upload-first experience: “Start creating”, an image upload/drop area, supported image formats, and an indication that AI tools become available after upload. This confirms that the public route is reachable, but it does **not** prove authenticated dashboard persistence, real upload storage, project creation, history, or account state. Those must be verified against the actual local application, backend, database, API calls, and browser network traffic. 

---

# 1. Research Findings

## 1.1 SaaS dashboard research

Current SaaS UX research consistently emphasizes:

- persistent, understandable navigation
- clear primary actions
- explicit empty/loading/error states
- reusable design systems
- consistent spacing and typography
- real data rather than decorative dashboard content
- information hierarchy before visual decoration

A modern dashboard should help the user understand what exists, what changed, and what they can do next without making them decode the interface.

Sources:

- SaaS dashboard layout patterns: https://threshline.com/blog/saas-dashboard-design-patterns/
- SaaS dashboard UX and information hierarchy: https://www.eleken.co/blog-posts/saas-dashboard-design
- SaaS design patterns by screen type: https://www.saasui.design/saas-design
- Scalable dashboard patterns: https://www.nextcraft.agency/resources/insights/saas-dashboard-patterns

---

## 1.2 File upload research

Modern SaaS upload UX is not just a file picker.

A trustworthy upload flow should communicate:

- what files are accepted
- size limits before selection
- upload progress
- per-file status
- successful completion
- failure reason
- retry
- cancel
- remove
- preview where appropriate
- final storage location

For batch uploads, each file should have an independent state instead of one ambiguous global spinner.

Source:

- SaaS file upload UX research, 2026: https://www.saasui.design/blog/saas-file-upload-ux-patterns

This is directly relevant to ToolHub-AI `/dashboard/files` and every editor upload flow.

---

## 1.3 File/folder hierarchy research

A real file manager should behave like a real content hierarchy:

- folders have IDs
- files have IDs
- parent-child relationships are persisted
- breadcrumbs represent actual hierarchy
- folder creation persists
- rename persists
- move persists
- delete/restore persists
- search uses real records
- sorting uses real metadata
- grid/list views use the same source of truth

Tree/file-browser research emphasizes visible hierarchy, disclosure controls, clear current-location state, safe drag/move behavior, search for large collections, and persistence of expanded state.

Source:

- SaaS file/tree UX patterns, 2026: https://www.saasui.design/blog/saas-tree-view-file-explorer-ux-patterns

---

## 1.4 Accessibility research

ToolHub-AI should target WCAG 2.2 AA-level interaction quality.

Important requirements include:

- visible keyboard focus
- focus not obscured by sticky UI
- usable keyboard navigation
- sufficient non-text contrast
- predictable controls
- accessible dialogs and menus
- accessible form labels

WCAG 2.2 documents specific focus visibility and focus appearance requirements.

Sources:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Focus Visible: https://www.w3.org/WAI/WCAG22/Understanding/focus-visible
- Focus Appearance: https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance

---

## 1.5 SEO research

Google Search documentation currently emphasizes:

- unique, descriptive page titles
- useful visible headings
- crawlable links
- canonical URLs
- sitemaps
- correct robots directives
- structured data where applicable
- server/HTML metadata that is not dependent on unreliable client-only rendering

Sources:

- SEO for developers: https://developers.google.com/search/docs/fundamentals/get-started-developers
- Title links: https://developers.google.com/search/docs/appearance/title-link
- Canonical URLs: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Sitemaps: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Robots metadata: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
- JavaScript SEO: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Structured data/search appearance: https://developers.google.com/search/docs/appearance

---

## 1.6 Favicon research

A professional favicon generator should not produce only one arbitrary square PNG.

Google currently states that a favicon should be square and at least 8×8 pixels, while recommending a larger size such as 48×48 or above for better display. Browsers can select among multiple `rel="icon"` resources based on size/type, and web app manifests can define multiple icon sizes and purposes.

ToolHub-AI's favicon generator should therefore generate a complete browser/web-app icon package, not merely a single file.

Sources:

- Google favicon requirements: https://developers.google.com/search/docs/appearance/favicon-in-search
- HTML `rel`/icon behavior: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel
- Web app manifest icons: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest/Reference/icons

---

# 2. Core Product Principle

## 2.1 The Real-Data Rule

For every page, identify:

```text
UI
 ↓
State
 ↓
API / Server Action
 ↓
Database / Storage / External Provider
 ↓
Persisted result
 ↓
UI refresh/revalidation
```

The implementation must not be:

```text
UI
 ↓
local fake array
 ↓
looks real
```

unless the data is explicitly a client-only preference or ephemeral editor state.

---

## 2.2 No Fake Production Data

Search the frontend and backend for:

- mock user names
- fake avatar URLs
- hardcoded plan names
- hardcoded credit counts
- fake history entries
- fake file counts
- fake project records
- fake storage usage
- fake timestamps
- placeholder folders
- fake payment states
- fake AI model availability
- “demo” records accidentally shipped to production
- `Math.random()`
- static arrays used as production dashboard data
- `setTimeout()` pretending to represent a backend operation
- success states without a server response
- buttons with no real handler
- disabled controls presented as available functionality

Test accounts may exist, but they must be clearly isolated from production behavior.

---

# 3. Cross-Application Data Architecture

## 3.1 Source of truth

Use the backend/database as the source of truth for:

- authenticated user
- profile
- subscription
- plan
- credits
- entitlement
- files
- folders
- projects
- project metadata
- history
- settings that are intended to persist
- payment state
- AI job state
- export records

Frontend state should represent:

- fetched server state
- temporary interaction state
- editor state
- loading state
- form state
- local UI preferences

Do not let local React state become a second database.

---

## 3.2 Mutation pattern

Every meaningful mutation should follow:

```text
User action
→ disable/reduce duplicate action
→ request backend mutation
→ backend validates authorization
→ backend validates business rules
→ database transaction
→ return authoritative result
→ invalidate/revalidate relevant queries
→ update UI
→ show success/error
```

Do not show permanent success before the backend confirms the mutation.

---

## 3.3 Refresh consistency

After:

- upload
- folder creation
- rename
- move
- delete
- project creation
- project update
- AI operation
- export
- settings update

the affected UI should reflect the new server state.

Test:

1. Perform action.
2. Refresh browser.
3. Navigate away and back.
4. Open in another tab if applicable.
5. Verify the state still exists.

---

# 4. GLOBAL PROFILE / ACCOUNT DROPDOWN

## Target area

Authenticated top-right account dropdown.

Current symptom:

> User cannot see sufficient user details from the dropdown.

## Required implementation

The account menu should show real authenticated data:

```text
┌──────────────────────────────┐
│  [Avatar]                    │
│  MD Ajim                     │
│  user@example.com            │
│                              │
│  Pro                         │
│  420 credits                 │
│                              │
│  ──────────────────────────  │
│  Account                     │
│  Settings                    │
│  Billing                     │
│  Usage                       │
│                              │
│  ──────────────────────────  │
│  Theme                       │
│  Help & Support              │
│                              │
│  Sign out                    │
└──────────────────────────────┘
```

Do not invent any of these values.

### Backend requirements

The account/session endpoint should return the fields actually required by the UI.

At minimum, where supported by the current data model:

- display name
- email
- avatar
- subscription/plan
- credit balance
- account status
- optional usage summary

### Security

Do not expose:

- password
- payment secrets
- provider tokens
- internal IDs unnecessarily
- admin-only fields

### UX

- keyboard accessible
- focus trap where appropriate
- click-outside close
- Escape close
- mobile friendly
- clear sign-out action
- no duplicated account menus

---

# 5. `/dashboard/files` — REAL FILE MANAGER

## Current reported problems

- Upload button does not appear to connect correctly to real data.
- New Folder does not create a real folder.
- UI appears disconnected from backend state.

This area needs a complete data-flow audit.

---

## 5.1 Required file model

Inspect the existing model first.

Do not create a parallel file model if one already exists.

A real file record should conceptually include:

```text
id
owner/user
folder_id
name
original_name
mime_type
extension
size
storage_key/path
thumbnail/preview reference
created_at
updated_at
deleted_at (if soft delete)
status
```

Only include fields that match the existing architecture.

---

## 5.2 Required folder model

Conceptually:

```text
id
owner/user
parent_id
name
created_at
updated_at
```

If the project already has this model, reuse it.

---

## 5.3 Upload flow

Required:

```text
Click Upload
→ native picker / drag & drop
→ validate type
→ validate size
→ upload
→ storage confirmation
→ DB record
→ thumbnail/metadata if required
→ UI refresh
```

A successful browser file selection alone must NOT be considered an upload.

---

## 5.4 Upload state machine

Use real states:

```text
idle
selecting
validating
uploading
processing
completed
failed
cancelled
```

For multiple files:

```text
file A → completed
file B → uploading 62%
file C → failed → Retry
```

Never collapse partial batch failures into a generic “Upload failed”.

---

## 5.5 New Folder

Required:

```text
New Folder
→ dialog
→ name validation
→ POST/Server Action
→ DB transaction
→ return folder
→ refresh current directory
→ select/focus newly created folder
```

Test:

- empty name
- duplicate name
- long name
- special characters
- same name in different parent folders
- unauthorized folder creation
- refresh persistence

---

## 5.6 File manager UX

Provide:

- breadcrumbs
- grid/list toggle
- search
- sort
- filter
- upload
- new folder
- file preview
- rename
- move
- delete
- restore if supported
- download
- context menu
- multi-select where appropriate
- keyboard navigation
- empty state
- loading state
- error state

For a mature file manager, folder hierarchy should remain understandable and breadcrumbs should reflect real parent relationships.

---

# 6. `/dashboard/projects`

## Required behavior

Projects must be real database records.

The project list must not be a frontend-generated array.

Each project card/row should show real:

- project name
- thumbnail/preview
- updated time
- created time where useful
- file/image count where supported
- status
- owner/workspace if applicable

---

## 6.1 Project creation

```text
Create Project
→ form
→ backend validation
→ DB transaction
→ project ID
→ navigate to project
```

Do not route to a UUID that exists only in frontend state.

---

## 6.2 Project detail

Example:

`/dashboard/projects/{project_id}`

Must:

- validate user ownership/permission
- load actual project
- load project assets
- load project metadata
- handle missing project
- handle unauthorized project
- persist edits
- persist title/name changes
- persist relevant editor state
- provide real delete/archive behavior if implemented

---

## 6.3 Deep-link test

Copy the project URL.

Open it in:

- new tab
- private window after authentication
- refreshed browser

The same project must load from server state.

---

# 7. `/dashboard/history`

History should represent actual operations/events.

It must not be a static activity feed.

Potential record types:

```text
upload
AI operation
export
download
project created
project updated
file deleted
file restored
settings changed
subscription event
```

Only include events actually supported by the backend.

---

## 7.1 History record requirements

Conceptually:

```text
id
user
event_type
resource_type
resource_id
metadata
created_at
status
```

Avoid storing unnecessary sensitive payloads.

---

## 7.2 History UX

Provide:

- date/time
- operation/tool
- asset/project
- status
- thumbnail where appropriate
- details
- retry/open resource where supported
- filters
- pagination/infinite loading
- empty state
- loading state
- error state

Do not display an event until the server has actually recorded it.

---

# 8. `/dashboard/settings`

Settings should be divided into clear sections.

Recommended structure:

```text
Account
Profile
Security
Preferences
Appearance
Notifications
Privacy
Connected Services
Billing
Usage
```

Only show sections supported by the existing architecture.

---

## 8.1 Real settings behavior

For every setting:

```text
UI value
↕
server value
```

Test:

1. Change setting.
2. Save.
3. Refresh.
4. Log out/in.
5. Verify persistence.

If a setting is local-only, label/architect it as local-only instead of pretending it is account-level.

---

## 8.2 Security

Never place security-sensitive changes behind a generic optimistic toggle.

Password/email/2FA changes should use the existing secure authentication flow.

---

# 9. `/tools/favicon-generator`

This tool should be upgraded from a simple image generator into a complete favicon/web-app icon package generator.

## Required input

- source image upload
- drag & drop
- optional text/logo mode if supported
- background
- foreground
- padding
- shape
- preview

---

## 9.1 Generate multiple outputs

Where technically appropriate, generate:

```text
favicon.ico

favicon-16x16.png
favicon-32x32.png
favicon-48x48.png

apple-touch-icon.png
180x180

icon-192.png
icon-512.png

maskable-192.png
maskable-512.png

android/chrome compatible assets
```

Do not blindly generate every possible size if it creates redundant files. Use a documented output matrix.

---

## 9.2 ZIP download

The user should have:

```text
[ Download ZIP ]
```

The ZIP should contain:

```text
favicon/
├── favicon.ico
├── favicon-16x16.png
├── favicon-32x32.png
├── favicon-48x48.png
├── apple-touch-icon.png
├── icon-192.png
├── icon-512.png
├── maskable-192.png
├── maskable-512.png
├── site.webmanifest
├── favicon-install.html
└── README.txt
```

Only include files actually generated.

---

## 9.3 Installation code

Generate copy-ready snippets:

```html
<link rel="icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
```

The exact generated snippet must match the actual generated files.

---

## 9.4 Browser preview

Provide a live preview section:

```text
Browser Tab
┌────────────────────────────────┐
│ [icon] ToolHub AI              │
└────────────────────────────────┘

Bookmarks
┌────────────────────────────────┐
│ [icon] ToolHub AI              │
└────────────────────────────────┘

Mobile / Web App
┌─────────────────────┐
│      [ICON]         │
│    ToolHub AI       │
└─────────────────────┘
```

The preview should use the actual generated icon, not a placeholder.

---

## 9.5 Technical verification

Test generated package by:

- opening the HTML preview
- inspecting `<head>`
- testing browser tab
- testing bookmark appearance where possible
- validating manifest JSON
- validating icon dimensions
- validating transparent backgrounds
- testing malformed/unsupported input
- testing large files

---

# 10. `/ai` — AI WORKSPACE

## Current requirement

Default models should be genuinely free where the product's current provider/capability registry confirms zero-cost availability.

Do NOT default to ChatGPT/OpenAI merely because it is recognizable.

More importantly:

> “Free” must mean the actual configured provider/model path has no billable provider cost under the application's current production configuration.

Do not label a model “Free” based only on a marketing assumption.

---

## 10.1 Model architecture

Reuse the existing ToolHub-AI capability/eligibility system.

The frontend should receive:

```text
eligible models
provider
capabilities
availability
recommended/default
pricing/credit metadata where applicable
```

The frontend should not invent the model list.

---

## 10.2 Default selection

If the backend returns eligible free models:

```text
Free eligible model
↓
default selection
```

If no free production model is actually available:

```text
No free model currently available
```

Do not silently substitute a paid model.

---

## 10.3 Chat box redesign

The AI workspace should feel like a professional AI workspace rather than a small chat widget.

Recommended layout:

```text
┌──────────────────────────────────────────────┐
│ AI Workspace                     New Chat    │
├──────────────────────────────────────────────┤
│                                              │
│                                              │
│                Conversation                  │
│                                              │
│                                              │
├──────────────────────────────────────────────┤
│ Attach   Model ▾   Tools                     │
│                                              │
│ Ask ToolHub AI anything...             Send  │
└──────────────────────────────────────────────┘
```

Required:

- larger composer
- multi-line input
- auto-resize
- keyboard shortcut
- attachment support where supported
- model selector
- tool/context selector where supported
- generation state
- stop/cancel
- retry
- copy
- error state
- empty state
- conversation persistence if supported
- real streaming state if backend supports streaming

---

# 11. `/tools/password-generator`

This is a utility tool, so its quality should come from correctness + clarity rather than visual decoration.

## Required controls

- length
- uppercase
- lowercase
- numbers
- symbols
- exclude ambiguous characters
- pronounceable mode only if genuinely implemented
- generate
- copy
- regenerate

---

## UX

Use a large output area:

```text
┌──────────────────────────────────────┐
│  9v#Lq8!mP2@x...              Copy   │
└──────────────────────────────────────┘
```

Include:

- strength indicator
- entropy/quality explanation if implemented correctly
- clear generated-state feedback
- copy success
- keyboard access
- mobile-friendly controls

Never log generated passwords.

Avoid analytics events containing the password.

---

# 12. `/tools/qr-generator`

Upgrade to a polished QR creation workflow.

## Input modes

Where supported:

- URL
- text
- email
- phone
- Wi-Fi
- vCard/contact
- SMS

Do not expose a mode unless its encoder is actually implemented.

---

## Design controls

- foreground
- background
- margin
- error correction
- size
- logo
- corner style only if supported
- export format

---

## Live preview

The QR preview must update from actual input/state.

Provide:

- PNG download
- SVG download if supported
- copy image where supported
- reset

Validate that generated QR codes are scannable after styling changes.

---

# 13. `/tools/resume-builder`

The resume builder needs two simultaneous improvements:

1. Professional visual design.
2. Reliable PDF generation/download.

---

## 13.1 Resume data model

Use structured resume data:

```text
personal information
summary
experience
education
skills
projects
certifications
languages
links
custom sections
```

Persist to backend if the existing application supports saved resumes.

---

## 13.2 Templates

Provide a small number of high-quality templates rather than many weak templates.

Each template must support:

- A4
- clean typography
- ATS-conscious structure
- consistent spacing
- print-safe margins
- page breaks
- long-content handling

---

## 13.3 PDF export

Required primary CTA:

```text
Download PDF
```

Flow:

```text
Edit
→ preview
→ generate PDF
→ verify PDF generated
→ download
```

Do not create a fake download that only downloads HTML.

---

## 13.4 PDF quality checks

Test:

- one-page resume
- two-page resume
- long experience
- long project names
- long URLs
- missing sections
- Unicode
- page breaks
- header/footer
- print margins
- font rendering

---

# 14. PDF TOOL FAMILY

Example routes:

- `/tools/pdf/merge`
- `/tools/pdf/compress`

But the same quality standard must apply to the entire PDF tool family.

---

# 15. `/tools/pdf/merge`

## UX

Use a professional file workflow:

```text
Merge PDF

[ Drop PDFs here ]
or
[ Upload PDFs ]

Files
────────────────────────────
☷  document-1.pdf     2.4 MB
☷  document-2.pdf     1.8 MB
☷  document-3.pdf     5.1 MB

Drag to reorder

[ Merge PDFs ]
```

Required:

- multiple upload
- real file validation
- drag reorder
- remove
- file size
- page count if available
- preview where useful
- merge
- processing state
- error state
- final download

---

## Download

After successful server processing:

```text
[ Download merged PDF ]
```

The download must point to the actual generated file.

---

# 16. `/tools/pdf/compress`

## UX

Show:

```text
Compress PDF

Upload PDF

Original
12.4 MB

Compression
○ Basic
● Balanced
○ Maximum

Estimated output
...

[ Compress PDF ]
```

After processing:

```text
Original: 12.4 MB
Compressed: 4.7 MB
Saved: 62%

[ Download PDF ]
```

Do not display an estimated result as if it were the actual result.

After processing, replace the estimate with the real output size.

---

# 17. PDF FAMILY DESIGN SYSTEM

All PDF tools should share:

```text
PdfToolShell
UploadDropzone
FileQueue
ProcessingCard
ProgressState
ResultCard
DownloadButton
ErrorState
```

Do not independently redesign every PDF page.

Use a shared design language.

---

# 18. SEO TOOLS — MODERNIZATION

The SEO tool family should feel like a professional SEO workspace, not a collection of simple input forms.

---

## 18.1 SEO analyzer architecture

Potential modules:

```text
SEO Overview

Meta
├── Title
├── Description
├── Canonical

Content
├── H1
├── headings
├── word count
├── keyword/topic coverage

Technical
├── robots.txt
├── sitemap
├── indexability
├── canonical
├── status codes

Social
├── Open Graph
├── Twitter/X cards

Structured Data
├── JSON-LD
├── Schema type

Preview
├── Google result
├── social preview
```

Only expose checks that can actually be implemented and verified.

---

## 18.2 Google preview

Show:

```text
ToolHub AI — AI Image Tools
toolhubai.pro/tools/...

Create and edit images with professional AI-powered tools...
```

But clearly label it as a **preview**, not a guarantee of Google's exact rendering.

Google can rewrite title links/snippets.

---

## 18.3 Technical SEO

The site-level SEO system should support:

- unique titles
- unique descriptions
- canonical URLs
- sitemap
- robots directives
- crawlable links
- structured data
- Open Graph
- correct HTTP status behavior
- index/noindex control
- language metadata where applicable
- image alt text
- stable URLs

Google specifically documents titles, canonicalization, sitemaps, robots controls, and JavaScript SEO as important technical areas.

---

# 19. EDITOR SIDEBAR + INSPECTOR — PROFESSIONAL DESIGN SYSTEM

This is a high-priority visual modernization.

The editor should not resemble a generic settings form.

---

## 19.1 Left sidebar

Recommended hierarchy:

```text
TOOLS

Search tools...

RECENT

EDIT
  Select
  Pan
  Resize
  Crop
  Rotate
  Flip

AI TOOLS
  Background Remover
  Object Remover
  Enhance
  Upscale
  Retouch
  Generative Fill
  Relight

DESIGN
  Social
  Product
  Mockup
  Watermark

EXPORT
  Compress
  Export
```

Use the existing tool registry as the source of truth.

Do not duplicate tool definitions.

---

## 19.2 Inspector

Use:

```text
Inspector
──────────────

Context Header

CONTENT
Typography
Appearance
Effects
Spacing
Advanced
```

Controls should have a clear hierarchy.

Avoid showing every setting with equal visual prominence.

---

## 19.3 Shared control system

Create/reuse:

- InspectorShell
- InspectorSection
- InspectorField
- Select
- NumberInput
- Slider
- ColorControl
- Toggle
- SegmentedControl
- ModelSelector
- ButtonGroup

Normalize:

- height
- radius
- border
- typography
- spacing
- focus
- hover
- disabled
- selected

---

## 19.4 Color controls

Instead of a generic color field:

```text
Color
[ ● ] #111827
```

Use a professional swatch control with picker interaction.

Raw HEX should be secondary information.

---

## 19.5 Sliders

Use:

```text
Opacity                          100%
───────────────●────────────────
```

with precise keyboard/value editing.

Do not make every slider bright orange.

---

# 20. DESIGN SYSTEM

Create a shared ToolHub-AI design language.

## Tokens

At minimum:

```text
color.background
color.surface
color.surfaceElevated
color.border
color.text
color.textMuted
color.primary
color.primarySoft
color.ai
color.success
color.warning
color.error

spacing.xs
spacing.sm
spacing.md
spacing.lg
spacing.xl

radius.sm
radius.md
radius.lg

shadow.sm
shadow.md

font.size.xs
font.size.sm
font.size.md
font.size.lg
font.size.xl
```

Use semantic tokens rather than random Tailwind values scattered throughout the application.

---

# 21. MOTION / SMOOTHNESS

“Smooth” should not mean excessive animation.

Use motion for:

- dropdown opening
- sidebar transitions
- modal entry
- toast
- tab switching
- upload progress
- AI processing
- preview changes

Use:

- short durations
- transform/opacity where possible
- no layout-jumping animation
- reduced-motion support

Never animate every component merely for visual effect.

---

# 22. LOADING / EMPTY / ERROR STATES

Every real-data page must explicitly support:

```text
Loading
Empty
Populated
Refreshing
Error
Partial failure
Permission denied
Not found
```

Example:

### Empty Files

```text
        [folder icon]

        No files yet

Upload your first image or document
to start building your workspace.

[ Upload file ]
```

### Error

```text
Something went wrong

We couldn't load your files.

[ Retry ]
```

No blank white screens.

---

# 23. REAL-DATA VERIFICATION MATRIX

Every major route should be tested with:

| Test | Expected |
|---|---|
| Fresh login | real user data |
| Refresh | same persisted state |
| Logout/login | state remains |
| New tab | server state remains |
| Create | record persists |
| Update | record persists |
| Delete | correct state |
| Network failure | honest error |
| Unauthorized resource | 403/404 behavior |
| Empty account | correct empty state |
| Large data set | pagination/virtualization |
| Slow network | useful loading state |

---

# 24. SECURITY / TRUST

For user-owned resources:

```text
authenticated user
→ authorization check
→ resource ownership/permission
→ mutation
```

Never rely on:

```text
frontend hidden button
```

for security.

The backend must enforce ownership for:

- files
- folders
- projects
- history
- settings
- generated assets
- exports

---

# 25. PERFORMANCE

The application should remain responsive with real data.

Audit:

- unnecessary API calls
- duplicate requests
- waterfall requests
- large JSON payloads
- unoptimized thumbnails
- unnecessary re-renders
- oversized images
- blocking JavaScript
- slow PDF processing
- large file uploads

For large files/projects:

- pagination
- virtualization
- thumbnails
- lazy loading
- caching
- query invalidation
- background processing

should be used where appropriate.

---

# 26. RESPONSIVE REQUIREMENTS

Test at minimum:

```text
375 × 812
390 × 844
768 × 1024
1024 × 768
1280 × 800
1366 × 768
1440 × 900
1536 × 864
1920 × 1080
```

Test:

- dashboard
- editor
- file manager
- projects
- history
- settings
- AI
- favicon generator
- password generator
- QR generator
- resume builder
- PDF tools
- SEO tools

No:

- horizontal overflow
- clipped dropdowns
- inaccessible modals
- hidden primary buttons
- overlapping sidebars
- broken sticky headers

---

# 27. ACCESSIBILITY REQUIREMENTS

At minimum:

- keyboard navigation
- visible focus
- semantic buttons/links
- labels for inputs
- accessible dialogs
- accessible menus
- accessible comboboxes
- accessible sliders
- accessible tooltips
- sufficient contrast
- screen-reader-friendly state changes
- reduced-motion support

Do not use a `<div>` as a button when a real `<button>` is appropriate.

---

# 28. ICONOGRAPHY

ToolHub-AI needs one coherent icon system.

Audit all icons.

Normalize:

- size
- stroke
- weight
- optical alignment
- active state
- disabled state

Avoid:

- mixed icon families
- random emoji
- inconsistent filled/outlined styles
- icons with different visual scale

Icons are part of the product's brand language.

---

# 29. ROUTE-BY-ROUTE AUDIT PLAN

The implementation agent must inspect these routes individually:

### Authentication/account

- profile dropdown
- account information
- plan/credits
- settings

### Files

`/dashboard/files`

### Projects

`/dashboard/projects`

`/dashboard/projects/{project_id}`

### History

`/dashboard/history`

### Settings

`/dashboard/settings`

### AI

`/ai`

### Favicon

`/tools/favicon-generator`

### Utility

`/tools/password-generator`

`/tools/qr-generator`

### Resume

`/tools/resume-builder`

### PDF

`/tools/pdf/merge`

`/tools/pdf/compress`

and then every other PDF tool.

### SEO

All SEO tool routes/components.

### AI editors

At minimum:

`/tools/object-remover/editor`

and then every editor that uses the same editor shell.

---

# 30. IMPORTANT: LOCAL URL AUDIT

The following local URLs cannot be considered externally verified merely by opening the public website:

```text
http://localhost:32768/dashboard/files
http://localhost:32768/dashboard/projects
http://localhost:32768/dashboard/projects/2586b973-349f-4a0d-90e9-5c23cc2a2915
http://localhost:32768/dashboard/history
http://localhost:32768/dashboard/settings
```

The implementation agent must audit them from inside the running application.

Required investigation:

1. Open browser.
2. Login using a test account.
3. Open DevTools Network.
4. Perform every relevant action.
5. Identify API requests.
6. Inspect response payloads.
7. Inspect database records.
8. Refresh.
9. Confirm persistence.
10. Inspect console errors.
11. Inspect failed requests.
12. Inspect authorization behavior.
13. Inspect loading/empty/error states.

Do not conclude “real data works” simply because the page renders.

---

# 31. BROWSER NETWORK AUDIT

For every page, document:

```text
GET /...
POST /...
PATCH /...
DELETE /...
```

For every request record:

```text
purpose
request payload
response
status
auth requirement
database mutation
cache invalidation
UI update
```

Find:

- 404
- 401
- 403
- 409
- 422
- 429
- 500
- CORS problems
- stale responses
- duplicate requests
- silent failures

---

# 32. DATABASE AUDIT

For every reported broken workflow:

### Files

Verify:

```text
file selected
→ storage object
→ database record
```

### Folder

Verify:

```text
new folder
→ database row
→ parent relation
```

### Project

Verify:

```text
project creation
→ database row
→ owner relation
→ assets relation
```

### History

Verify:

```text
action
→ history/event record
```

### Settings

Verify:

```text
setting mutation
→ database/user preference
```

Do not add a second source of truth to compensate for a broken existing one.

---

# 33. FRONTEND STATE AUDIT

Search for:

```text
useState(...)
mockData
sampleData
demoData
fakeData
placeholder
TODO
FIXME
setTimeout
Math.random
localStorage
sessionStorage
hardcoded user
hardcoded credits
hardcoded projects
hardcoded history
```

Each occurrence must be classified:

```text
VALID CLIENT STATE
or
PRODUCTION DATA BUG
```

Do not remove legitimate editor-local state just because it is not server state.

---

# 34. API CONTRACT AUDIT

For each endpoint verify:

- request schema
- response schema
- error schema
- authentication
- authorization
- idempotency where needed
- database transaction
- frontend consumer
- cache invalidation

Avoid silently accepting inconsistent response formats.

---

# 35. ERROR HANDLING STANDARD

Use structured errors.

Example:

```json
{
  "code": "FILE_UPLOAD_TOO_LARGE",
  "message": "The selected file exceeds the 10 MB limit.",
  "field": "file",
  "retryable": false
}
```

The exact schema should follow the project's existing API conventions.

Frontend should translate known error codes into useful user messages.

Do not show:

```text
Something went wrong
```

when a specific reason is available.

---

# 36. DOWNLOAD STANDARD

Every generated downloadable asset must use a real server/client-generated artifact.

Required:

```text
generate
→ verify
→ provide actual URL/blob/file
→ download
```

Do not create fake download buttons.

Do not download a placeholder file.

For ZIP/PDF/favicon output, verify:

- MIME type
- filename
- file integrity
- content
- size
- browser download behavior

---

# 37. SEO TOOL QUALITY STANDARD

Every SEO tool should clearly distinguish:

```text
Detected
Recommended
Warning
Error
Information
Preview
```

Never represent a heuristic as an absolute Google ranking guarantee.

For example:

```text
Title length: 58 characters
Status: Within recommended range

```

is preferable to:

```text
SEO Score: 98/100
```

unless the scoring methodology is transparent and actually meaningful.

---

# 38. DESIGN QUALITY GATE

A page is not “finished” merely because it works.

Each page must pass:

### Visual

- typography
- spacing
- alignment
- iconography
- borders
- shadows
- color hierarchy
- responsive layout

### Interaction

- hover
- focus
- pressed
- disabled
- loading
- success
- error
- empty

### Functional

- API
- persistence
- authorization
- refresh
- deep link
- retry

### Accessibility

- keyboard
- screen reader semantics
- focus
- contrast

### Performance

- initial render
- interaction latency
- large data
- large files

---

# 39. IMPLEMENTATION ORDER

## Phase 1 — Full audit

Do not change UI immediately.

Audit:

- routes
- components
- API calls
- models
- database
- storage
- auth
- state management
- design system
- tool registry
- editor
- utilities
- PDF processing
- SEO system

Deliver:

```text
REAL_DATA_AUDIT.md
UI_COMPONENT_AUDIT.md
API_CONTRACT_AUDIT.md
```

---

## Phase 2 — Fix real-data architecture

Prioritize:

1. Files
2. Folders
3. Projects
4. Project details
5. History
6. Settings
7. Account dropdown

Reason:

A beautiful interface with fake persistence is still a broken product.

---

## Phase 3 — Shared design system

Build/reuse:

- spacing
- typography
- surfaces
- buttons
- inputs
- dropdowns
- dialogs
- tooltips
- tabs
- cards
- tables
- empty states
- loading states
- error states
- icons

---

## Phase 4 — Editor redesign

Refine:

- left sidebar
- tool categories
- Inspector
- sliders
- color controls
- model selector
- AI states
- responsive behavior

Do not change AI routing/capability architecture.

---

## Phase 5 — Utility tools

Improve:

- password generator
- QR generator
- favicon generator

---

## Phase 6 — Resume/PDF

Implement:

- professional templates
- real PDF output
- download
- PDF tool design system
- processing states
- error handling

---

## Phase 7 — AI workspace

Implement:

- backend-driven model availability
- genuinely free default model where available
- professional large composer
- real generation state
- streaming/cancel/retry where supported

---

## Phase 8 — SEO tools

Implement:

- modern analyzer UI
- technical checks
- metadata
- previews
- structured data
- crawlability
- canonical
- sitemap
- robots
- social previews

---

## Phase 9 — Full QA

Test all routes and workflows.

---

# 40. AUTOMATED TEST REQUIREMENTS

Add/update:

### Unit tests

- folder validation
- file validation
- QR generation
- password generation
- favicon size generation
- SEO analyzers
- PDF processing helpers

### Integration tests

- upload
- folder creation
- project creation
- project update
- history creation
- settings update
- PDF generation
- ZIP generation

### E2E

At minimum:

```text
Login
→ upload
→ create folder
→ create project
→ edit
→ export
→ download
→ history
```

And:

```text
Favicon
→ upload
→ configure
→ generate
→ preview
→ ZIP
```

And:

```text
PDF
→ upload
→ process
→ result
→ download
```

---

# 41. NO-REGRESSION REQUIREMENT

Before finalizing:

Run existing:

- frontend tests
- backend tests
- type checks
- lint
- build
- relevant integration tests

Then manually verify actual browser behavior.

A successful build is not proof of a successful product.

---

# 42. FINAL ACCEPTANCE CHECKLIST

## Real data

- [ ] Account dropdown uses real user
- [ ] Plan is real
- [ ] Credits are real
- [ ] Files are real
- [ ] Upload persists
- [ ] Folder creation persists
- [ ] Folder hierarchy persists
- [ ] Projects are real
- [ ] Project details are real
- [ ] History is real
- [ ] Settings persist
- [ ] No fake production records

## Editor

- [ ] Sidebar hierarchy improved
- [ ] Inspector redesigned
- [ ] Icons consistent
- [ ] Controls consistent
- [ ] Sliders professional
- [ ] Color picker professional
- [ ] AI model selector backend-driven
- [ ] No production mock model leakage
- [ ] Responsive
- [ ] Keyboard accessible

## AI

- [ ] Free default only when genuinely available
- [ ] No automatic paid-model substitution
- [ ] Model availability backend-authoritative
- [ ] Large professional composer
- [ ] Real generation states
- [ ] Error/retry/cancel handled

## Favicon

- [ ] Multiple relevant icon sizes
- [ ] ICO where supported by implementation
- [ ] PNG outputs
- [ ] Apple icon
- [ ] Manifest icons
- [ ] Maskable variants where appropriate
- [ ] ZIP download
- [ ] Install snippet
- [ ] Browser preview
- [ ] Generated assets actually match preview

## Resume

- [ ] Professional templates
- [ ] Structured data
- [ ] Real PDF generation
- [ ] PDF download
- [ ] Multi-page tested
- [ ] Unicode tested

## PDF

- [ ] Merge polished
- [ ] Compress polished
- [ ] All PDF tools follow shared design system
- [ ] Real processing
- [ ] Real output
- [ ] Real download
- [ ] Processing/error states

## Utilities

- [ ] Password generator polished
- [ ] QR generator polished
- [ ] Real generation
- [ ] Copy/download works
- [ ] No sensitive generated data logging

## SEO

- [ ] Modern analyzer
- [ ] Metadata checks
- [ ] Canonical
- [ ] Robots
- [ ] Sitemap
- [ ] Structured data
- [ ] Social preview
- [ ] Crawlability
- [ ] Clear distinction between recommendations and guarantees

## Quality

- [ ] Desktop tested
- [ ] Tablet tested
- [ ] Mobile tested
- [ ] Keyboard tested
- [ ] Focus states tested
- [ ] Loading tested
- [ ] Empty tested
- [ ] Error tested
- [ ] Slow network tested
- [ ] Refresh tested
- [ ] Deep links tested
- [ ] Unauthorized access tested
- [ ] Build passes
- [ ] Tests pass
- [ ] No console errors
- [ ] No critical network errors

---

# 43. Definition of Done

ToolHub-AI should not be considered complete until the implementation agent can demonstrate:

```text
REAL DATA
+
REAL BACKEND
+
REAL STORAGE
+
REAL PERSISTENCE
+
REAL AUTHORIZATION
+
REAL DOWNLOADS
+
REAL ERROR HANDLING
+
COHERENT DESIGN SYSTEM
+
PROFESSIONAL UX
+
RESPONSIVE UI
+
ACCESSIBILITY
+
SEO
+
PERFORMANCE
+
REGRESSION SAFETY
```

The final product should feel like one unified platform.

The editor, dashboard, utilities, AI workspace, PDF tools, favicon generator, SEO tools, settings and account system should not look like separate projects assembled together.

---

# 44. Final Product Principle

The most important rule for the implementation agent:

> **Do not optimize for “looks finished.” Optimize for “is genuinely finished.”**

A professional ToolHub-AI experience means:

- the button works
- the API works
- the database changes
- the storage changes
- the UI reflects the server
- refresh does not erase state
- errors are honest
- downloads contain the expected content
- permissions are enforced
- empty states are intentional
- loading states are truthful
- AI model availability is real
- the visual system is consistent
- every interaction feels deliberate

Only after those foundations are correct should visual polish be considered complete.

---

## External research references

1. SaaS upload UX patterns — https://www.saasui.design/blog/saas-file-upload-ux-patterns
2. SaaS file/tree UX patterns — https://www.saasui.design/blog/saas-tree-view-file-explorer-ux-patterns
3. SaaS design patterns — https://www.saasui.design/saas-design
4. SaaS dashboard patterns — https://threshline.com/blog/saas-dashboard-design-patterns/
5. SaaS dashboard design — https://www.eleken.co/blog-posts/saas-dashboard-design
6. WCAG 2.2 — https://www.w3.org/TR/WCAG22/
7. Google SEO developer guide — https://developers.google.com/search/docs/fundamentals/get-started-developers
8. Google title links — https://developers.google.com/search/docs/appearance/title-link
9. Google canonicalization — https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
10. Google sitemaps — https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
11. Google robots metadata — https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
12. Google JavaScript SEO — https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
13. Google favicon guidance — https://developers.google.com/search/docs/appearance/favicon-in-search
14. MDN favicon/link behavior — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel
15. MDN web-app manifest icons — https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest/Reference/icons


---

# 45. P0 — FILE VISUALIZATION, AI OUTPUT FORMATS & DOWNLOAD INTEGRITY

These are mandatory production requirements. A file is not considered successfully produced merely because a database row or job record exists.

The complete lifecycle must be:

`Generate/Upload → Persist → Verify → Preview → Inspect → Download → Reuse`

## 45.1 `/ai/library`

Every uploaded/generated file must be represented by a real, high-quality, type-aware preview.

### Images
- Show the complete image without accidental cropping.
- Preserve the original aspect ratio.
- Provide fit-to-screen, 100%/actual-size, zoom, pan and fullscreen.
- Use a real preview/original asset, not a low-resolution thumbnail as the main viewer.
- Show real filename, MIME type, dimensions and size.
- Provide a real **Download** action.

### PDFs
- Render actual pages.
- Page navigation, zoom, fit-width/fit-page, fullscreen.
- Show page count.
- Download the original PDF.
- Handle loading, corrupt/password-protected/failed states honestly.

### DOC/DOCX/PPT/PPTX and other documents
- Provide a reliable preview/conversion only when actually implemented.
- Never show a fake preview.
- Always keep the original file downloadable.

### File preview architecture

Create/reuse a type-aware:

```text
FilePreviewRouter
├── ImageViewer
├── PdfViewer
├── TextCodeViewer
├── StructuredDataViewer
├── DocumentPreview
└── UnsupportedFileViewer
```

The file manager should distinguish:

```text
thumbnail
preview
original/download
```

Do not use a small thumbnail URL as the full-resolution viewer.

---

# 46. SECURE FILE DELIVERY

For private files:

```text
Authenticated request
→ ownership/permission check
→ storage existence check
→ authorized/signed access
→ correct Content-Type
→ correct filename
→ download/preview
```

Audit all direct asset URLs and storage delivery for:

- 401/403/404
- expired signed URLs
- incorrect MIME type
- zero-byte responses
- wrong Content-Disposition
- broken range requests
- missing storage objects
- thumbnail/original confusion
- unauthorized access

Never construct private download URLs from filenames on the frontend.

---

# 47. PROJECT DETAIL — COMPLETE ASSET VISIBILITY

For `/dashboard/projects/{project_id}`:

- show the complete image at useful resolution;
- show PDFs/documents with actual content previews where supported;
- expose metadata from the real asset;
- provide **Open / Preview / Download** where appropriate;
- distinguish source, working, generated and exported assets;
- verify that the displayed asset and downloaded asset are the same artifact.

Deep-link + refresh must continue to work.

---

# 48. HISTORY — REAL OUTPUT ARTIFACTS

`/dashboard/history` must expose actual operation results, not only activity text.

Example:

```text
Object Removed
Completed

[actual output thumbnail]

[ Open ] [ Download ]
```

For PDF tools:

```text
PDF Merge
Completed

merged-document.pdf
[ Preview ] [ Download ]
```

The relationship should be:

```text
HistoryEvent
→ Job/Operation
→ OutputArtifact
→ StorageObject
→ AuthorizedDownload
```

A completed job without a retrievable artifact is a failed product workflow.

---

# 49. GLOBAL DOWNLOAD CONTRACT

Every output-producing tool must use one consistent download architecture.

Required lifecycle:

```text
processing
→ completed
→ persist artifact metadata
→ verify storage object
→ generate authorized access
→ preview where possible
→ download
```

Support all applicable output types:

- PNG/JPEG/WebP
- PDF
- ZIP
- CSV
- JSON
- TXT/MD
- DOCX
- XLSX
- SVG
- HTML
- other generated artifacts

Verify:

- filename
- MIME type
- byte size
- file integrity
- actual content
- browser download behavior

Do not show a Download button for an artifact that is still processing or no longer available.

---

# 50. `/ai` — CHATGPT-LEVEL STRUCTURED OUTPUT RENDERING

ToolHub-AI's AI workspace must not flatten every response into plain text.

The supplied Full Stack AI article identifies 15 useful response formats: Plain Text, Lists, Tables, Code, Markdown, LaTeX, HTML, JSON, URLs, ASCII Art, Emojis, CSV, YAML, XML and Quotes, and also describes combining formats. This is a useful benchmark for the response-rendering layer. citeturn1view0

The requirement is **format capability**, not that every answer must contain every format.

Implement a structured renderer supporting, when returned/requested:

```text
Paragraph
Heading
OrderedList
UnorderedList
TaskList
Table
CodeBlock
InlineCode
Markdown
Math/LaTeX
HTML
JSON
URLs
ASCII Art
Emoji
CSV
YAML
XML
Blockquote/Quote
ImageArtifact
FileArtifact
```

A single answer must be able to combine several:

```text
Heading
→ explanation
→ table
→ code
→ JSON
→ quote
→ downloadable file
```

---

# 51. FORMAT-SPECIFIC UX

### Tables
Real HTML table, responsive scrolling, copy table, CSV download where appropriate.

### Code
Syntax highlighting, language label, copy, horizontal scrolling and download where useful.

### Markdown
Professional headings, lists, tables, links, code and quotes.

### LaTeX
Inline/display math with a trusted renderer. Preserve raw equation if rendering fails.

### HTML
Sanitized preview + source/raw view + copy/download. Never inject arbitrary AI HTML into the main application DOM.

### JSON
Collapsible structured viewer, formatting, copy, download `.json`, raw fallback if invalid.

### URLs
Safe clickable links, copy, open in new tab.

### ASCII art
Preserve whitespace using a monospace `<pre>`-style renderer.

### CSV
Structured table view + copy CSV + download CSV. Use a proper CSV parser.

### YAML/XML
Syntax highlighting, copy, download, validation where appropriate.

### Quotes
Visually distinct blockquote with attribution/source kept adjacent when supplied.

---

# 52. AI RESPONSE ACTIONS

Show actions appropriate to the content:

```text
Copy
Regenerate
Continue/Edit
Download
```

Examples:

```text
Code       → Copy code / Download
JSON       → Copy JSON / Download
CSV        → Copy CSV / Download
Generated file → Preview / Download
```

Do not show irrelevant controls.

---

# 53. AI LIBRARY ↔ CHAT

Where supported by the existing architecture:

```text
AI chat
→ upload/generate file
→ persist Library asset
→ preview
→ download
→ reuse in future chat
```

Provide an **Add from Library** flow where appropriate. Current ChatGPT Library similarly supports browsing/searching/filtering saved files and downloading selected files, which is a useful product benchmark. citeturn0search2turn0search6

---

# 54. FILE / ARTIFACT QUALITY GATE

For every file-producing feature:

### Images
- complete image visible
- no unintended crop
- correct aspect ratio
- high-quality preview
- original downloadable

### PDF
- real page preview
- correct page count
- valid generated file
- download works
- downloaded file opens

### Documents
- accurate metadata
- real preview/conversion where supported
- original downloadable

### ZIP
- actual archive
- correct files
- correct names
- extractable

---

# 55. P0 TEST MATRIX

## AI Library
- [ ] image thumbnail is sharp
- [ ] full image opens
- [ ] zoom/pan/fullscreen works
- [ ] original downloads
- [ ] PDF pages render
- [ ] PDF downloads
- [ ] document metadata is real
- [ ] unsupported types fail gracefully

## AI
- [ ] plain text
- [ ] ordered/nested lists
- [ ] tables
- [ ] code
- [ ] Markdown
- [ ] LaTeX
- [ ] HTML
- [ ] JSON
- [ ] URLs
- [ ] ASCII art
- [ ] emojis
- [ ] CSV
- [ ] YAML
- [ ] XML
- [ ] quotes
- [ ] mixed-format response
- [ ] copy actions
- [ ] generated-file preview
- [ ] generated-file download

## Projects
- [ ] full-resolution image
- [ ] full document/PDF access
- [ ] real metadata
- [ ] source/result distinction
- [ ] download works
- [ ] refresh/deep-link persistence

## History
- [ ] completed operation has real artifact
- [ ] preview works
- [ ] download works
- [ ] missing artifact is reported honestly
- [ ] expired artifact is handled

## All file-producing tools
- [ ] processing state
- [ ] completed state
- [ ] artifact persisted
- [ ] preview where applicable
- [ ] authorized download
- [ ] correct filename/MIME
- [ ] file integrity verified

---

# 56. FINAL TOOLHUB-AI QUALITY STANDARD

ToolHub-AI has three equal product gates:

```text
PREMIUM DESIGN
+
MAXIMUM POSSIBLE OUTPUT QUALITY
+
FLAWLESS ARTIFACT EXPERIENCE
```

Therefore:

```text
Beautiful UI + broken download       = NOT DONE
Great AI result + poor presentation  = NOT DONE
Working backend + fake data           = NOT DONE
```

The intended experience is:

> **Premium interface + exceptional AI output + accurate previews + reliable persistence + reliable downloads.**

These P0 requirements must be included in the final regression and acceptance audit for the entire platform, not only the example routes listed by the user.
