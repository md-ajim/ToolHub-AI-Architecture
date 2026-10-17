📄 docs/08-api-design.md
API Design
Version

v1.0

API Goals
REST API First
Versioned APIs
Secure by Default
Scalable
Consistent Response Format
Public API Ready
Base URL
/api/v1/

ভবিষ্যতে:

/api/v2/
API Categories
Authentication

Users

Profile

Image Tools

PDF Tools

SEO Tools

Developer Tools

AI Tools

AI Workspace

Workspace

Files

History

Subscription

Payments

Notifications

Analytics

API Keys

Admin
Authentication APIs
Register
POST /api/v1/auth/register
Login
POST /api/v1/auth/login
Refresh Token
POST /api/v1/auth/refresh
Logout
POST /api/v1/auth/logout
Google Login
POST /api/v1/auth/google
Forgot Password
POST /api/v1/auth/forgot-password
Reset Password
POST /api/v1/auth/reset-password
User APIs
GET /users/me

PATCH /users/me

DELETE /users/me
Subscription APIs
GET /plans

GET /subscription

POST /subscription/upgrade

POST /subscription/cancel

POST /subscription/resume
Billing APIs
GET /payments

GET /invoices

POST /checkout

POST /webhooks/stripe
Workspace APIs
GET /workspace

GET /history

GET /favorites

POST /favorites

DELETE /favorites
File APIs

Upload

POST /files/upload

Download

GET /files/{id}

Delete

DELETE /files/{id}
Image Tool APIs

Resize

POST /image/resize

Compress

POST /image/compress

Convert

POST /image/convert

Crop

POST /image/crop

Rotate

POST /image/rotate

Watermark

POST /image/watermark

WebP

POST /image/webp

AVIF

POST /image/avif

Favicon

POST /image/favicon
AI Image APIs
POST /ai/background-remove

POST /ai/upscale

POST /ai/enhance

POST /ai/object-remove

POST /ai/background-replace

POST /ai/passport-photo

POST /ai/product-background

GET /ai/jobs/{id}

AI Workspace APIs
GET /ai-workspace/models

GET /ai-workspace/conversations

POST /ai-workspace/conversations

POST /ai-workspace/conversations/{id}/messages

POST /ai-workspace/conversations/{id}/compare

GET /ai-workspace/usage
PDF APIs
POST /pdf/merge

POST /pdf/compress

POST /pdf/split

POST /pdf/rotate

POST /pdf/protect

POST /pdf/unlock

POST /pdf/to-image

POST /pdf/from-image
SEO APIs
POST /seo/meta

POST /seo/open-graph

POST /seo/sitemap

POST /seo/robots
Developer APIs
POST /developer/json-format

POST /developer/json-validate

POST /developer/base64-encode

POST /developer/base64-decode

POST /developer/url-encode

POST /developer/url-decode

POST /developer/hash
QR APIs
POST /qr/generate

GET /qr/{id}

GET /qr/{id}/analytics
Link Shortener APIs
POST /links

GET /links

PATCH /links/{id}

DELETE /links/{id}

GET /links/{id}/analytics
Resume APIs
POST /resume

GET /resume

PATCH /resume

DELETE /resume

POST /resume/export
Notification APIs
GET /notifications

PATCH /notifications/read

DELETE /notifications
Analytics APIs
GET /analytics/dashboard

GET /analytics/tool-usage

GET /analytics/storage

GET /analytics/subscription
API Keys
GET /api-keys

POST /api-keys

PATCH /api-keys

DELETE /api-keys
Admin APIs
GET /admin/users

GET /admin/payments

GET /admin/tools

GET /admin/jobs

GET /admin/system
Response Format

Success

{
  "success": true,
  "message": "Image resized successfully.",
  "data": {}
}

Validation Error

{
  "success": false,
  "message": "Validation failed.",
  "errors": {
    "file": [
      "Unsupported file format."
    ]
  }
}

Server Error

{
  "success": false,
  "message": "Internal server error."
}
HTTP Status Codes
Code	Meaning
200	Success
201	Created
204	Deleted
400	Bad Request
401	Unauthorized
403	Forbidden
404	Not Found
409	Conflict
422	Validation Error
429	Too Many Requests
500	Internal Server Error
Pagination
GET /history?page=1&page_size=20

Response

{
  "count": 152,
  "next": "...",
  "previous": "...",
  "results": []
}
Filtering

Example

GET /history?tool=image-resize
Sorting
GET /history?ordering=-created_at
Search
GET /history?search=passport
Rate Limiting

Free

60 requests/minute

Pro

300 requests/minute

API

Plan অনুযায়ী
File Upload Rules

Maximum

Free

25 MB

Pro

250 MB

Enterprise

Custom
Authentication

সব Protected API

Authorization: Bearer JWT_TOKEN
Webhooks

Payment Success

POST /webhooks/stripe

Future

Paddle
PayPal
API Versioning Rules
/api/v1/ স্থায়ী থাকবে।
Breaking Change হলে /api/v2/ তৈরি হবে।
Deprecated API নির্দিষ্ট সময় পর্যন্ত চালু থাকবে।
Security
JWT Authentication
Refresh Token Rotation
Rate Limiting
File Type Validation
File Size Validation
Virus Scanning (Future)
Signed Download URLs
Audit Logging
API Documentation

আপনার Public API-এর জন্য:

OpenAPI 3.1 Specification
Swagger UI
ReDoc
Postman Collection

যাতে অন্য ডেভেলপাররা সহজেই আপনার API ব্যবহার করতে পারে।

API Flow Example
Client
   │
   ▼
API Gateway (Future)
   │
   ▼
Authentication
   │
   ▼
Rate Limiter
   │
   ▼
Permission Check
   │
   ▼
Validation
   │
   ▼
Business Service
   │
   ▼
Background Queue (if needed)
   │
   ▼
Database / Storage
   │
   ▼
Response
📌 Architecture Decision Record (ADR)

এই প্রজেক্টের জন্য আমি নিচের API নীতিগুলো স্থির রাখব:

REST API হবে প্রধান ইন্টারফেস; GraphQL শুরুতে ব্যবহার করব না।
সব API Versioned হবে (/api/v1/)।
Response Format পুরো প্ল্যাটফর্মে একই থাকবে।
ভারী কাজ (AI, PDF, Batch Processing) Asynchronous Job API ব্যবহার করবে।
Public API শুরু থেকেই মাথায় রেখে Endpoint Design করা হবে।
OpenAPI Specification স্বয়ংক্রিয়ভাবে জেনারেট করা হবে, যাতে Documentation সবসময় API-এর সাথে আপডেট থাকে।
