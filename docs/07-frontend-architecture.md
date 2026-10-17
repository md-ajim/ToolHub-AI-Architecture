📄 docs/07-frontend-architecture.md
Frontend Architecture
Version

v1.0

Goal
SEO First
Performance First
Mobile First
Accessibility First
Reusable Components
Modular Design
AI Ready
Technology Stack
Technology	Choice
Framework	Next.js (App Router)
Language	TypeScript
UI	React
Styling	Tailwind CSS
Components	shadcn/ui
Icons	Lucide React
Forms	React Hook Form + Zod
Data Fetching	TanStack Query
Charts	Recharts
Theme	next-themes
Animation	Framer Motion
Root Folder Structure
frontend/

├── app/
├── components/
├── features/
├── hooks/
├── lib/
├── services/
├── store/
├── types/
├── utils/
├── constants/
├── public/
├── styles/
└── middleware.ts
app/
app/

(page)

(layout)

loading.tsx

error.tsx

not-found.tsx

globals.css
Public Routes
/

pricing

blog

docs

about

contact

privacy

terms

login

register
Tool Routes
/tools

/tools/image

/tools/pdf

/tools/seo

/tools/developer

/tools/video

/tools/audio

/tools/ai
Example Tool URLs
/tools/image/resize

/tools/image/compress

/tools/image/convert

/tools/image/upscale

/tools/image/background-remover

/tools/pdf/merge

/tools/pdf/compress

/tools/seo/meta-generator

/tools/developer/json-formatter
Dashboard
/dashboard

/history

/workspace

/subscription

/billing

/profile

/settings

/api

/notifications

/workspace/ai

/workspace/ai/[conversationId]
Admin
/admin

/users

/payments

/tools

/blog

/analytics

/settings
components/

Shared UI Components

components/

ui/

layout/

navigation/

forms/

cards/

dialogs/

charts/

tables/

tool/

seo/
features/

Feature-Based Components

features/

image/

pdf/

ai/

subscription/

workspace/

analytics/

authentication/
ai-workspace/
lib/
lib/

auth.ts

api.ts

query-client.ts

metadata.ts

storage.ts

logger.ts
services/

API Calls

services/

auth.service.ts

image.service.ts

pdf.service.ts

subscription.service.ts

payment.service.ts
ai-workspace.service.ts

AI Workspace is a persistent authenticated application surface. It must use centralized API services and server state, never provider SDKs or provider keys in browser code. See `32-ai-workspace-architecture.md`.
store/

Global State

store/

auth.ts

theme.ts

workspace.ts

notifications.ts
hooks/
hooks/

useUser.ts

useSubscription.ts

useUpload.ts

useDownload.ts

useTheme.ts
types/
types/

user.ts

tool.ts

payment.ts

api.ts

subscription.ts
utils/
utils/

format.ts

date.ts

files.ts

download.ts

validation.ts
constants/
constants/

plans.ts

routes.ts

limits.ts

tools.ts
Component Structure
Button

↓

Card

↓

Tool Card

↓

Tool Page

↓

Dashboard

ছোট Component থেকে বড় Page তৈরি হবে।

Page Layout

প্রতিটি Tool Page-এ থাকবে:

Hero Section
Upload Area
Tool Settings
Preview
Download
FAQ
Related Tools
SEO Content
Upload Flow
User

↓

Select File

↓

Validate

↓

Preview

↓

Upload

↓

API

↓

Processing

↓

Download
SEO Structure

প্রতিটি Tool Page-এ:

Unique Title
Meta Description
Canonical URL
Open Graph
Twitter Card
JSON-LD
Breadcrumb
Performance Rules
Server Components ডিফল্ট
Client Components শুধুমাত্র প্রয়োজন হলে
Dynamic Import
Lazy Loading
Image Optimization
Font Optimization
Route-based Code Splitting
Responsive Breakpoints
Mobile
Tablet
Laptop
Desktop
Wide Screen
Design System

Colors

Primary
Secondary
Success
Warning
Error
Neutral

Spacing

4px Grid System

Border Radius

Small
Medium
Large

Typography

Heading
Body
Caption
Authentication Flow
Login

↓

JWT

↓

Refresh Token

↓

Protected Route

↓

Dashboard
Premium Flow
User

↓

Check Plan

↓

Allowed?

↓

Process

↓

Upgrade Page (if needed)
Error Handling

সব Page-এ:

Loading State
Empty State
Error State
Retry Button
Analytics

Track করা হবে:

Page View
Tool Usage
Upload
Download
Conversion
Upgrade Click
Subscription
Accessibility
Keyboard Navigation
Screen Reader Labels
Color Contrast
Focus Indicators
ARIA Attributes
Reusable Layouts
Public Layout
Tool Layout
Dashboard Layout
Admin Layout
Auth Layout
Future Ready

এই Frontend Architecture ভবিষ্যতে সমর্থন করবে:

Multi-language
Dark Mode
Chrome Extension
PWA
Android Web App
iOS Web App
Team Dashboard
AI Chat Assistant
Coding Rules
Feature-Based Folder Structure
Strict TypeScript
Reusable Components
No Business Logic Inside UI Components
Centralized API Services
Consistent Naming Convention
Shared Validation Schemas
