📄 docs/05-domain-model.md
Domain Model
Version

v1.0

Goal

Business Logic-কে ছোট ছোট Domain-এ ভাগ করা, যাতে প্রতিটি Module স্বাধীনভাবে কাজ করতে পারে এবং ভবিষ্যতে ৫০০+ টুল হলেও কোডবেস সহজে পরিচালনা করা যায়।

Domain List
01. Accounts
02. Authentication
03. Subscription
04. Billing
05. Workspace
06. Storage
07. Processing
08. Image Tools
09. PDF Tools
10. AI Engine
11. SEO Tools
12. Developer Tools
13. Analytics
14. Notification
15. Blog
16. API
17. Admin
18. System
19. AI Workspace
01. Accounts Domain
Entity: User
Fields
Field	Type	Notes
id	UUID	Primary Key
email	Email	Unique
password	String	Hashed
full_name	String	
avatar	URL	Nullable
country	String	ISO Code
language	String	Default Language
timezone	String	
status	Enum	Active / Suspended
email_verified	Boolean	
created_at	DateTime	
updated_at	DateTime	
Entity: Profile
Field	Type
user	OneToOne(User)
bio	Text
company	String
website	URL
social_links	JSON
preferences	JSON
02. Subscription Domain
Entity: Plan
Field	Type
id	UUID
name	String
slug	String
monthly_price	Decimal
yearly_price	Decimal
storage_limit	Integer
api_limit	Integer
batch_limit	Integer
ai_credit	Integer
is_active	Boolean
Entity: Subscription
Field	Type
id	UUID
user	FK(User)
plan	FK(Plan)
status	Enum
AI Workspace Domain
Entity: Conversation
Field	Type
id	UUID
owner	FK(User)
project	Nullable FK
title	String
Entity: Message
Field	Type
id	UUID
conversation	FK(Conversation)
role	Enum(User/Assistant/System)
model	Nullable FK(AIModel)
status	Enum
Entity: Model Access Policy
Field	Type
model	FK(AIModel)
plan	FK(Plan)
enabled	Boolean
usage_rule	JSONB
start_date	Date
end_date	Date
auto_renew	Boolean
03. Billing Domain
Payment
Field	Type
id	UUID
user	FK
amount	Decimal
currency	String
gateway	Stripe/Paddle
transaction_id	String
status	Enum
created_at	DateTime
Invoice
Field	Type
id	UUID
payment	FK
invoice_number	String
pdf_url	URL
04. Storage Domain
File
Field	Type
id	UUID
owner	FK(User)
filename	String
mime_type	String
extension	String
size	BigInt
bucket	String
path	String
checksum	String
status	Enum
expires_at	DateTime
Folder
Field	Type
id	UUID
owner	FK
parent	Self FK
name	String
05. Processing Domain
Job
Field	Type
id	UUID
owner	FK
tool	FK(Tool)
status	Pending/Running/Completed/Failed
priority	Integer
progress	Integer
input_file	FK(File)
output_file	FK(File)
error_message	Text
started_at	DateTime
finished_at	DateTime
BatchJob
Field	Type
id	UUID
owner	FK
total_jobs	Integer
completed_jobs	Integer
failed_jobs	Integer
06. Tool Domain
Tool
Field	Type
id	UUID
category	Enum
slug	String
name	String
description	Text
icon	URL
free_limit	Integer
premium	Boolean
active	Boolean
Tool Usage
Field	Type
id	UUID
user	FK
tool	FK
ip	String
execution_time	Float
file_size	BigInt
created_at	DateTime
07. AI Domain
AI Model
Field	Type
id	UUID
provider	Enum
model_name	String
version	String
endpoint	URL
status	Boolean
AI Job
Field	Type
id	UUID
model	FK
owner	FK
input_file	FK
output_file	FK
credit_used	Integer
latency	Float
status	Enum
08. Workspace Domain
Workspace Item
Field	Type
id	UUID
owner	FK
file	FK
favorite	Boolean
tags	JSON
archived	Boolean
History
Field	Type
id	UUID
owner	FK
tool	FK
job	FK
created_at	DateTime
09. Analytics Domain
Event
Field	Type
id	UUID
user	Nullable FK
event_name	String
metadata	JSONB
country	String
device	String
created_at	DateTime
10. Notification Domain
Notification
Field	Type
id	UUID
owner	FK
title	String
body	Text
type	Enum
is_read	Boolean
11. API Domain
API Key
Field	Type
id	UUID
owner	FK
key	String
secret	String
status	Boolean
API Usage
Field	Type
id	UUID
api_key	FK
endpoint	String
request_count	Integer
total_processing_time	Float
12. Blog Domain
Article
Field	Type
id	UUID
title	String
slug	String
content	Text
author	FK
published	Boolean
13. Admin Domain
Audit Log
Field	Type
id	UUID
admin	FK
action	String
target	String
ip	String
created_at	DateTime
Domain Relationships
User
 ├── Profile
 ├── Subscription
 ├── Payment
 ├── Files
 ├── Jobs
 ├── Workspace
 ├── Notifications
 ├── API Keys
 └── Analytics

Tool
 ├── Jobs
 ├── Usage
 └── History

File
 ├── Job
 ├── AI Job
 └── Workspace

Subscription
 └── Plan
Design Rules
সব Primary Key হবে UUID।
Public API-তে কখনও Auto Increment ID দেখানো হবে না।
Soft Delete (deleted_at) ব্যবহার করা হবে।
created_at এবং updated_at প্রায় সব Entity-তে থাকবে।
Status-এর জন্য Enum ব্যবহার করা হবে (যেমন Pending, Running, Completed, Failed)।
বড় আকারের Metadata-এর জন্য PostgreSQL-এর JSONB ব্যবহার করা হবে।
