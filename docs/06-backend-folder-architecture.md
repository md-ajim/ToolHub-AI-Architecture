📄 docs/06-backend-folder-architecture.md
Backend Folder Architecture
Version

v1.0

Goal
Modular
Scalable
Easy to Maintain
Feature-Based
API First
AI Ready
Tech Stack
Python
Django
Django REST Framework
PostgreSQL
Redis
Celery
Amazon S3
Root Structure
backend/

├── apps/
├── config/
├── core/
├── shared/
├── services/
├── integrations/
├── workers/
├── tests/
├── scripts/
├── media/
├── static/
├── logs/
├── requirements/
├── manage.py
└── README.md
apps/

এখানে প্রতিটি Business Module থাকবে।

apps/

accounts/
authentication/
subscriptions/
billing/
ai_workspace/
workspace/
storage/
processing/

image_tools/
pdf_tools/
seo_tools/
developer_tools/
business_tools/
video_tools/
audio_tools/
ai_tools/

analytics/
notifications/
api/
blog/
admin_panel/
system/
প্রতিটি App-এর Structure
image_tools/

models.py
views.py
serializers.py
urls.py
permissions.py
selectors.py
services.py
tasks.py
validators.py
signals.py
admin.py
apps.py
tests/

migrations/
প্রতিটি ফাইলের কাজ
models.py

Database Models

serializers.py

Request/Response Validation

views.py

API Endpoints

urls.py

Routes

services.py

Business Logic

যেমন

Resize Image
Compress Image
Convert Image

সব Business Logic এখানে থাকবে।

selectors.py

Database Read Query

যেমন

get_user_history()

get_recent_jobs()

get_subscription()

Database Read আলাদা থাকবে।

validators.py

সব Input Validation

যেমন

File Size
MIME Type
Premium Check
permissions.py

DRF Permission

যেমন

IsPremium

IsAdmin

IsOwner
tasks.py

Celery Background Jobs

যেমন

Compress

Resize

Merge PDF

AI Processing
signals.py

Django Signals

যেমন

User Created
Subscription Updated
Payment Success
config/
config/

settings/

base.py
development.py
production.py

urls.py
asgi.py
wsgi.py
celery.py
shared/

সব App-এর Common Code

shared/

constants.py

exceptions.py

responses.py

pagination.py

permissions.py

validators.py

utils.py

storage.py

enums.py
services/

External Services

services/

email/

storage/

payment/

ai/

pdf/

image/

notification/
integrations/

Third-party Integration

stripe/

google/

aws/

cloudflare/

resend/

openai/

stability/

replicate/
workers/

Background Processing

workers/

ai/

image/

pdf/

cleanup/

emails/
tests/
tests/

unit/

integration/

performance/
scripts/
scripts/

backup.py

seed.py

cleanup.py

import.py

export.py
Logging
logs/

api.log

worker.log

payment.log

error.log

security.log
Storage

লোকাল Media শুধুমাত্র Development-এর জন্য।

Production

Amazon S3
Environment
.env

.env.production

.env.development
Business Flow
Client

↓

API

↓

Serializer

↓

Permission

↓

Validator

↓

Service

↓

Selector / Model

↓

Database

↓

Response
Heavy Processing Flow
Upload

↓

Validation

↓

Save File

↓

Celery Queue

↓

Worker

↓

S3 Upload

↓

Database Update

↓

User Notification
Dependency Rules

App A

↓

shared

↓

services

↓

integrations

↓

Database

App কখনও অন্য App-এর Business Logic সরাসরি Call করবে না।

Service Layer ব্যবহার করবে।

AI Workspace provider integrations must remain behind a gateway/service and adapter boundary. Views must not call provider SDKs directly; model access, usage reservation and normalized provider errors are shared domain services. See `32-ai-workspace-architecture.md`.

Naming Convention

Apps

snake_case

Classes

PascalCase

Functions

snake_case

API

kebab-case
Response Format

সব API একই Format Follow করবে।

Success

{
  "success": true,
  "message": "Completed",
  "data": {}
}

Error

{
  "success": false,
  "message": "Validation failed",
  "errors": {}
}
Security Rules
JWT Authentication
Rate Limiting
File Validation
Virus Scan (Future)
Signed S3 URL
HTTPS Only
CSRF Protection (যেখানে প্রযোজ্য)
Audit Logging
Development Rules
Fat Models নয়
Thin Views
Business Logic শুধুমাত্র Service Layer-এ
Database Query Selector Layer-এ
Celery শুধুমাত্র Heavy Task-এর জন্য
Reusable Code shared/-এ
Third-party Code integrations/-এ
Versioning
/api/v1/

/api/v2/

পুরনো API কখনও ভাঙা হবে না।

Future Ready

এই Structure ভবিষ্যতে সমর্থন করবে:

৫০০+ Tool
Public API
Chrome Extension
Android App
iOS App
Team Workspace
AI Marketplace
Multi-Region Deployment
Multiple AI Provider
White-label API
