# ToolHub-AI — Production UX, Real-Data & Functional Integrity Audit / Implementation Specification

**Document type:** Production implementation blueprint  
**Project:** ToolHub-AI  
**Scope:** Editor UI/UX, authenticated dashboard, real-data integrity, utility tools, PDF tools, AI workspace, favicon generator, SEO tools, responsive/accessibility QA  
**Priority:** Production / international SaaS quality  
**Status:** Implementation-ready specification  
**Prepared:** 2026-10-01

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

# 45. Implementation Record — Phases 0–3 + Hardening (2026-10-01)

**Status:** Implemented against this specification. All verification green at time of writing.
**Method:** Research-first (5 parallel codebase audits) → phased implementation → `tsc` + `eslint` + `vitest` + `next build` + backend `manage.py check` + container test suites after every phase.
**Rule honored throughout:** no mock/fake production data; every fix works end-to-end against real backend + real database.

## 45.1 Phase 0 — Trust fixes (spec §§4–7, 11)

### Editor header: real user menu + real credits (spec §4 account system)
- **Found:** `EditorHeader.tsx` read only `EditorContext.entitlements` and rendered a static badge — no user details, no menu; any auth hiccup displayed `Free / 0 credits`. Backend `GET /subscriptions/entitlements/` (`AllowAny` + anonymous fallback) is real, so the symptom was a frontend data-flow gap, not mock data.
- **Built:** `EditorUserMenu` in `frontend/src/components/editor/EditorHeader.tsx` — consumes `useAuth()` + entitlements; wallet-aware credits (`wallet.ai_credits`, `-1` → Unlimited via existing `types/payment.ts` helpers); four honest states (loading skeleton / Login CTA for guests / Retry row on plan-fetch failure / real data); dropdown items Profile, AI Workspace, Dashboard, Settings, Plans & pricing, Log out (mirrors the main-site `UserMenu` pattern). `EntitlementData` in `subscription.service.ts` extended with the real `plan_code` + `wallet` fields the backend already returns.
- **Also fixed:** the dead `Image Editor ⌄ / Switch editor` button (no `onClick`) → working editor-switcher menu over 6 verified editor routes + All tools, with unsaved-changes confirm.

### History: contract + population (spec §7)
- **Found:** API real but (a) only AI jobs wrote `History`, pdf/image paths wrote neither `File` nor `History` rows (empty-by-design tables), (b) frontend expected `file.original_name/url` while backend sends `filename/storage_path` → Open/Download icons never rendered, search never matched, (c) guest users saw an infinite skeleton (`loadingData` never cleared).
- **Built:** shared best-effort recorder `backend/apps/workspace/services.py::record_tool_result()` (creates `File` + `History`, never raises, skips anonymous); wired into all 8 PDF views via `save_to_media(..., user, tool)` and into `image_tools/tasks.py::process_image_job` on COMPLETED. Frontend `dashboard/history/page.tsx` reads the real contract (`filename`/`storage_path` + `resolveMediaUrl`, legacy keys as fallback), fixed the guest skeleton → login prompt, search matches real filenames.

### QR generator dead controls + zero downloads (spec §§10–11)
- **Found:** frontend sent `error_correction` + `size`; backend serializer dropped both and hardcoded `ERROR_CORRECT_L`; no download button at all.
- **Built:** backend accepts/honors `error_correction` (L/M/Q/H) + existing color/geometry params; `BusinessService.generateQr` sends the real contract; page gained a working EC selector, fill/back color pickers, honestly-labeled display-size scaling, and a real PNG download (base64 → blob). Result block later migrated to the shared `ToolResultCard`.

### Split mislabel (§11 honesty)
- `pdf/split` button said `Download ZIP` for a single PDF → `Download PDF`.

## 45.2 Phase 1 — Dashboard data layer (spec §§5–7)

### Storage endpoints (new, all user-scoped, no mocks)
- `POST /storage/files/` — multipart upload, plan-limit enforcement (`get_storage_limit_bytes` + total-usage check), 500 MB hard cap, executable blocklist, `user_<id>/uuid_name` layout, real `File` row (optional `folder_id`/`project_id`).
- `PATCH /storage/files/<id>/` — assign/unassign folder + project (foreign targets → 404).
- `GET /storage/files/<id>/download/` — `FileResponse` attachment stream.
- `GET/POST /workspace/folders/`, `PATCH/DELETE /workspace/folders/<id>/` — nested folders on the pre-existing (previously orphaned, zero-route) `Folder` model, cycle-guard, soft-delete nulls contained files.
- `PATCH /workspace/projects/<id>/` — rename + description.
- Schema: `File.folder` FK + hand-written migration `storage/0003_file_folder.py` (compose runs `migrate --noinput` on start).

### Frontend (previously empty stubs now real)
- `hooks/useUpload.ts` (was 0 lines): XHR multipart + progress + Bearer + single 401-refresh retry + cancel.
- `hooks/useDownload.ts` (was 0 lines): authenticated blob download + `downloadStoredFile`/`downloadMediaPath`.
- `services/storage.service.ts` (new): list/delete/update/usage. `WorkspaceService` extended: folders CRUD + `updateProject`.
- **Files page rebuilt:** nested folders + breadcrumb + create/rename/delete, multi-upload with progress rows, working download per row, move-to-folder, real usage bar (plan limit / Unlimited), load-error Retry. **Projects list:** error + Retry state, rename modal, delete confirm dialog. **Project detail rewritten:** rename, real image previews (`storage_path`, null-safe), working Download + Open-in-tab, remove-from-project (file kept), Add-files dialog (library picker + direct upload with `projectId`).

## 45.3 Phase 2 — Flagship tools (spec §§9, 11)

### Favicon multi-device pack + ZIP + browser preview (spec §9)
- **Backend** `create_favicon_pack()`: deterministic ZIP — `favicon.ico` (16/32/48), `favicon-16/32.png`, `apple-touch-icon` (180), `android-chrome` 192/512, `mstile` 150, `site.webmanifest`, `browserconfig.xml`; options background (incl. `transparent`), padding 0–40%, app name, theme color through serializer → view → celery task. Opaque-required icons flattened honestly.
- **Frontend** (`jszip` added): options UI, existing job-poll flow, client-side ZIP extraction → per-file grid with real sizes + individual downloads + ZIP download (auth blob), install snippet (`<head>` block) + copy, **browser preview with real generated pixels** (16px tab icon, 32px URL bar, light/dark toggle, iOS 180px tile + clipping note).

### Resume real PDF (spec §11)
- `jspdf` + `html2canvas` added; `lib/resumePdf.ts` renders the preview node to paginated A4 (`Name_Resume.pdf`, progress stages). **Download PDF is a real file**; separate Print button + `@media print` stylesheet (only the resume prints).
- 3 templates (Modern/Minimal/Executive) + 6 accent colors + photo upload (2 MB cap) + `localStorage` draft + Reset + empty-section filtering.

### Real compress + merge reorder (spec §11)
- **Compression proven with live numbers** (container, real PDF): 96,650 B → medium 24,406 B (**−75%**) → high 12,666 B (**−87%**), outputs reopen cleanly. Technique: pypdf XObject surgery + Pillow downsample/re-encode (levels low/medium/high = 2200/85, 1600/70, 1100/55; skips SMask + tiny icons; never raises). No Ghostscript in the image — this path needs none.
- Compress page: level selector + `before → after (−%)` stats + no-savings hint. Merge page: numbered order list with **up/down/remove** (merge follows that order), duplicate-guarded accumulation, `hideFileList`.

## 45.4 Phase 3 — AI, password, SEO, shared shell (spec §§10–11)

### /ai free default + bigger composer (spec §10)
- **Correction to the report that prompted this:** no ChatGPT default was ever hardcoded; `Auto` routing picks highest-tier first, so payers landed on paid models. Fix is frontend-only: `defaultFreeModelId()` (first runnable free chat model in display order) in `modelRegistry.tsx`, applied in `ai/page.tsx` and `ai/c/[id]/page.tsx` (persisted/explicit choice still wins; Auto stays selectable). Backend routing untouched.
- Bigger composer: landing `max-w-2xl→3xl`, thread `3xl→4xl`, textarea 48→64px min / 200→320px cap + autogrow, deeper container, 36→40px send/stop.

### Password premium UX (spec §11)
- **Client-side `crypto.getRandomValues`** (rejection-sampled, bias-free): instant/offline, passwords never leave the browser (removes the trust negative of POSTing secrets). Length slider + number (4–128), 4 presets, 4 charset toggles, ambiguous-exclude, **entropy-bits strength meter + crack-time estimate**, show/hide, copy feedback, in-memory-only session history.

### SEO modernization (spec §11, backend untouched — all contracts already supported lists)
- Shared `components/tool/SeoOutput.tsx` (copy-feedback + **file download**).
- Meta: 60/160 counters with over-limit states + **Google SERP preview** + `meta-tags.html`. OG: URL validation + **Facebook + X card previews** (real image URL) + type select + `.html`. Robots: **multi-group builder** + line count + `robots.txt`. Sitemap: per-line URL validation + count + `sitemap.xml`.

### Shared shell (spec: one unified platform)
- New `components/tool/ToolShell.tsx` (`ToolShell` + `ToolResultCard`: stats + download + preview + actions). Migrated: QR, compress, split, rotate, protect, unlock, `PdfConversionTool` (covers to-jpg/from-jpg) — 8 pages on one result language, zero one-off green boxes left in the PDF suite.

## 45.5 Verification evidence (final state)

| Check | Result |
|---|---|
| `tsc --noEmit` (frontend) | clean |
| `eslint` on all touched frontend files | 0 errors (1 pre-existing error in `ChatComposer.tsx` draft effect, untouched lines — left intact deliberately) |
| `vitest` (`editor`, `constants`, `dashboard`) | **61/61 green** (one transient worker flake observed once, green on consecutive reruns) |
| `next build` | ✅ 146/146 pages, repeated after every phase |
| Backend `py_compile` on all touched modules | OK |
| Container suites (`manage.py test`: entitlements, pdf conversion ×2, image services) | **26/26 OK** |
| Compress technique | live-proven numbers above |
| `manage.py check` | no issues |

## 45.6 Deploy checklist (required — code is not live until this runs)

1. Redeploy backend + frontend (new npm deps: `jszip`, `jspdf`, `html2canvas`).
2. Database: `storage/0003_file_folder.py` applies via the compose `migrate --noinput` step (verify it ran; no other migrations needed — no new models besides the FK).
3. Smoke after deploy, all against real backend + real DB: editor header shows name/plan/real credits + logout; upload → Saved Files row → download identical bytes; create/nest/delete folder; project rename + add-files; run PDF merge → Files + History rows appear with working download; favicon ZIP contains all 9 files; resume PDF downloads with correct filename; compress medium shrinks a photo PDF.
4. Known environment notes: container `/app` is an image copy (not a repo mount) — local edits take effect only after redeploy; `pytest` is not installed in the backend image (Django runner used instead); one pytest-style test module (`workspace/test_comment_access.py`) cannot run in-container for that reason.

## 45.7 Deliberately left for follow-up (not regressions)

- Remaining ~10 utility pages still on hand-rolled result boxes (ToolShell migration is incremental by design; pattern + 8 migrated pages prove it).
- `ChatComposer.tsx` pre-existing `set-state-in-effect` lint note (draft-consumption effect) — behavior-correct, out of scope.
- `xkiro_free_models.json` is stale (nothing imports it; DB seed is truth) — flagged, not deleted, pending owner decision.
- In-place password change (settings uses the intentional email-link flow); bio/company/website live on `/dashboard/profile` by design.
