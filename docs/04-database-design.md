📄 docs/04-database-design.md
Database Design
Version

v1.0

Database Goal
Scalable
Modular
Fast
Secure
Easy to Extend
Support Millions of Records
Database Choice

Primary: PostgreSQL

Reason:

Excellent indexing
JSONB support
Full-text search
Strong concurrency
Mature ecosystem
Database Modules

পুরো ডাটাবেসকে ১৪টি Module-এ ভাগ করা হবে।

Accounts

Authentication

Tools

Files

Processing

Workspace

Subscription

Payments

Analytics

Notifications

API

Blog

Admin

System
Module 1 — Accounts
users
id
uuid
email
password
full_name
avatar
country
language
timezone
is_active
is_verified
last_login
created_at
updated_at
profiles
id
user_id
bio
website
company
occupation
social_links
preferences
Module 2 — Authentication
sessions
id
user_id
device
ip
user_agent
expires_at
oauth_accounts
id
user_id
provider
provider_user_id
email
Module 3 — Subscription
plans
id
name
price
billing_cycle
storage_limit
daily_limit
batch_limit
api_limit
subscriptions
id
user_id
plan_id
status
starts_at
expires_at
usage
id
user_id
tool
usage_count
date
Module 4 — Billing
payments
id
user_id
amount
currency
gateway
status
transaction_id
paid_at
invoices
id
payment_id
invoice_number
pdf_url
Module 5 — Files
files
id
user_id
filename
mime_type
size
storage_path
status
uploaded_at
processed_files
id
file_id
tool
result_path
processing_time
download_count
Module 6 — Processing
jobs
id
user_id
tool
status
priority
started_at
finished_at
error
batch_jobs
id
user_id
job_count
status
Module 7 — Workspace
folders
id
user_id
name
favorites
id
user_id
tool
history
id
user_id
tool
file
created_at
Module 8 — API
api_keys
id
user_id
key
status
created_at
api_usage
id
api_key
endpoint
request_count
Module 9 — Notifications
notifications
id
user_id
title
message
type
read
Module 10 — Analytics
events
id
user_id
event_name
tool
metadata
created_at
page_views
id
page
visitor
country
device
Module 11 — Blog
posts
id
title
slug
content
author
published
categories
id
name
slug
Module 12 — Admin
audit_logs
id
admin
action
target
ip
Module 13 — AI
ai_models
id
name
version
provider
status
ai_jobs
id
user
model
status
credits
processing_time
AI Workspace
ai_model_registry
id
provider
provider_model_id
tier
capabilities
status
ai_conversations
id
user_id
project_id
title
ai_messages
id
conversation_id
role
model_id
status
ai_message_runs
id
message_id
model_id
usage
cost
status
Module 14 — System
settings
key
value
feature_flags
feature
enabled
Relationships (High Level)
User

├── Profile

├── Subscription

├── Files

├── Payments

├── Jobs

├── Workspace

├── API Keys

├── Notifications

└── Analytics
Index Strategy

সবচেয়ে বেশি Index থাকবে

email
slug
created_at
status
user_id
tool
payment_id
api_key
Soft Delete

সব বড় টেবিলে থাকবে

deleted_at

যাতে ডেটা হারিয়ে না যায়।

UUID Strategy

সব Public Resource

uuid

ব্যবহার করবে।

ID কখনও Public API-তে দেখানো হবে না।

Storage Strategy

Database-এ File থাকবে না।

Database-এ থাকবে শুধু

URL

Metadata

Status

মূল File থাকবে S3-তে।

Future Ready

এই Database Design ভবিষ্যতে সমর্থন করবে:

Team Workspace
Organization
Multi-language
Public API
AI Credits
Chrome Extension
Android
iOS
Marketplace
