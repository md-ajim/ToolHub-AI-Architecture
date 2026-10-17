📄 docs/03-system-architecture.md
System Architecture
Version

v1.0

Architecture Goal
Modular Monolith (শুরুতে)
API First
AI Ready
Cloud Ready
SEO First
Scale Without Rewriting
High Level Architecture
                        Users
                          │
                          ▼
                 Next.js Frontend
                          │
                          ▼
                  Django REST API
                          │
 ┌──────────────┬──────────┼───────────┬─────────────┐
 ▼              ▼          ▼           ▼             ▼
Auth         Tool Engine  Billing   Workspace   Analytics
 │              │           │           │             │
 └──────────────┴───────────┴───────────┴─────────────┘
                          │
                    Celery Queue
                          │
AI / Background Workers
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
      PostgreSQL/MySQL                Amazon S3
                          │
                          ▼
                       Redis
Frontend
Technology
Next.js
React
TypeScript
Tailwind CSS
shadcn/ui
Responsibilities
UI
Routing
Authentication
Dashboard
Tool Pages
Pricing
Blog
Documentation
Backend
Technology
Django
Django REST Framework
Responsibilities
Authentication
Tool Processing
Billing
Subscription
History
File Management
Notifications
Admin API
Background Jobs
Technology
Celery
Redis

AI Workspace

Multi-model chat is a separate application domain. Requests flow through an internal AI Gateway, model registry and provider adapters; the frontend never calls a model provider directly. The gateway applies authentication, authorization, entitlement, usage reservation, rate limiting, streaming policy, normalized provider errors and cost tracking. See `32-ai-workspace-architecture.md`.
Use Cases
AI Processing
PDF Merge
Bulk Resize
Bulk Compress
Email Sending
Cleanup Jobs
Analytics Aggregation
Database

প্রস্তাব: PostgreSQL (দীর্ঘমেয়াদে বেশি নমনীয়), তবে MySQL-ও ব্যবহার করা সম্ভব।

Core Tables:

users
subscriptions
payments
tool_usage
files
processing_jobs
notifications
api_keys
analytics_events
Storage

Amazon S3

Folder Structure

uploads/
processed/
exports/
avatars/
temporary/
logs/
Redis

ব্যবহার হবে

Queue
Cache
Rate Limit
Sessions (যদি প্রয়োজন হয়)
AI Worker

আলাদা Worker

Responsibilities

Background Removal
AI Enhance
Upscale
OCR
Image Generation (ভবিষ্যতে)

এটি API থেকে আলাদা থাকবে যাতে ভারী AI কাজ সাধারণ API-কে ধীর না করে।

Tool Engine

প্রতিটি Tool Module আলাদা থাকবে।

Image Tools
PDF Tools
Video Tools
Audio Tools
SEO Tools
Developer Tools
Business Tools
AI Tools
Subscription Engine

Plans

Free
Pro
Team

Checks

Daily Limit
Monthly Limit
Storage Limit
Batch Limit
Billing

Payment Gateway

Stripe

Future

Paddle
PayPal
Authentication
Email
Google OAuth
JWT Access Token
Refresh Token
Notifications

Channels

Email
In-App

Future

Push Notification
Logging

সব গুরুত্বপূর্ণ ঘটনা লগ হবে:

Login
Payment
Tool Run
Error
AI Job
API Request
Monitoring
Server Health
Queue Length
Processing Time
Error Rate
Storage Usage
Security
HTTPS Only
CSRF Protection
XSS Protection
SQL Injection Protection
File Validation
Virus Scan (ভবিষ্যতের জন্য)
Rate Limiting
API Strategy

সবকিছু REST API দিয়ে শুরু হবে।

উদাহরণ:

/api/v1/image/resize
/api/v1/pdf/merge
/api/v1/ai/background-remove
/api/v1/subscription
/api/v1/workspace

ভবিষ্যতে v2 যোগ করা যাবে, পুরোনো ক্লায়েন্ট ভাঙবে না।

File Processing Flow
Upload
    │
    ▼
Validate
    │
    ▼
Store Temporary File
    │
    ▼
Queue Processing
    │
    ▼
Process
    │
    ▼
Save Result
    │
    ▼
Return Download URL
Scaling Strategy
Stage 1

একটি Server

Next.js
Django
Redis
PostgreSQL
Celery
Stage 2

Server আলাদা

Frontend
Backend
Worker
Stage 3

AI Worker আলাদা GPU Server

Stage 4

Multiple Worker + CDN

Folder Structure
apps/
    accounts/
    image_tools/
    pdf_tools/
    ai_tools/
    seo_tools/
    developer_tools/
    business_tools/
    workspace/
    subscriptions/
    billing/
    analytics/
    notifications/

core/
config/
shared/
Design Principles
Modular Monolith
Single Responsibility
Reusable Components
Feature-Based Modules
Background Processing
API Versioning
Scalable Storage
Testable Code
Future Ready

এই আর্কিটেকচার এমনভাবে ডিজাইন করা হয়েছে যাতে ভবিষ্যতে নিচের ফিচারগুলো মূল কোডবেস না ভেঙেই যোগ করা যায়:

Chrome Extension
Android App
iOS App
Public API
Team Workspace
White-label API
AI Marketplace
Multi-language Support
