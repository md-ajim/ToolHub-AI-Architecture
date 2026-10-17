# 13 — Storage & File Management Architecture

**Project:** Multi-Tool Utility / Micro-SaaS Platform  
**Document:** Storage & File Management Architecture  
**Status:** Architecture Specification  
**Version:** 1.0  
**Last Updated:** 2026-08-09

---

## 1. Purpose

This document defines the complete architecture for handling files across the platform.

The system will process potentially large volumes of:

- Images
- AI-generated images
- PDFs
- Documents
- SVG files
- ZIP archives
- User uploads
- Temporary processing files
- Batch-processing outputs
- User workspace files
- Exported files

The architecture must provide:

- Secure uploads
- Secure downloads
- Object storage
- File validation
- Access control
- Temporary file management
- Permanent file management
- Automatic cleanup
- Storage quotas
- Subscription-aware storage
- AI processing integration
- CDN delivery where appropriate
- Cost optimization
- Scalability
- Backup and recovery strategy

The architecture must work for the initial MVP and scale to millions of files without requiring a complete redesign.

AI Workspace attachments and derived parsed content reuse this storage architecture. They remain private by default, must retain owner/project linkage, and require their own configurable retention/deletion policy; no separate chat-upload store may be introduced. See `32-ai-workspace-architecture.md`.

---

# 2. Core Principle

The application server must **not be used as the permanent file storage layer**.

Preferred architecture:

```text
User
  ↓
Next.js Frontend
  ↓
Django REST API
  ↓
Signed Upload URL
  ↓
Object Storage
  ↓
Django Database stores metadata
```

For processing:

```text
Object Storage
      ↓
Processing Worker
      ↓
Temporary Workspace
      ↓
Processing
      ↓
Object Storage
      ↓
Database Metadata
      ↓
Signed Download URL
      ↓
User
```

---

# 3. Storage Technology

Initial recommended storage:

```text
AWS S3
```

The application should use an abstraction layer so that storage can later be moved to:

- Cloudflare R2
- Google Cloud Storage
- Azure Blob Storage
- MinIO
- Any S3-compatible provider

The business logic must not depend directly on AWS-specific implementation details.

---

# 4. Storage Abstraction

Create a storage service.

Example:

```python
class StorageService:
    def upload(self, file, path, metadata=None):
        ...

    def download(self, path):
        ...

    def delete(self, path):
        ...

    def exists(self, path):
        ...

    def generate_upload_url(self, path, content_type):
        ...

    def generate_download_url(self, path):
        ...
```

The rest of the application should communicate with:

```text
StorageService
```

rather than directly calling S3 throughout the codebase.

---

# 5. Storage Layers

The platform should separate files into logical storage categories.

```text
Object Storage
│
├── Temporary
├── User Uploads
├── AI Inputs
├── AI Outputs
├── Projects
├── Exports
├── Batch Results
├── Avatars
└── System Assets
```

Each category must have separate lifecycle and security rules.

---

# 6. Recommended Bucket Strategy

Initially, one private bucket can be used with logical prefixes.

Example:

```text
platform-private/
├── users/
├── temporary/
├── ai/
├── projects/
├── exports/
└── batch/
```

For larger scale, separate buckets can be introduced:

```text
platform-private
platform-public
platform-processing
platform-backups
```

Do not create unnecessary buckets during MVP.

---

# 7. Storage Path Architecture

Never store all files in a single directory.

Recommended structure:

```text
users/{user_id}/uploads/{year}/{month}/{file_id}
```

AI:

```text
ai/{user_id}/inputs/{job_id}/{file_id}
ai/{user_id}/outputs/{job_id}/{file_id}
```

Projects:

```text
projects/{user_id}/{project_id}/{file_id}
```

Exports:

```text
exports/{user_id}/{export_id}/{file_id}
```

Temporary:

```text
temporary/{session_id}/{file_id}
```

---

# 8. File ID

The database-generated ID should be used instead of trusting the original filename.

Example:

```text
file_01JXXXXXXXXXXXX
```

The original filename is stored separately.

Never use a user-provided filename as the primary object-storage identifier.

---

# 9. File Metadata Model

Conceptual model:

```text
File

id
owner_id
project_id
original_name
storage_key
mime_type
extension
size
checksum
width
height
duration
status
storage_provider
storage_bucket
visibility
file_type
source
created_at
updated_at
expires_at
deleted_at
```

Optional:

```text
metadata_json
```

for tool-specific information.

---

# 10. File Status

Recommended statuses:

```text
pending
uploading
uploaded
processing
ready
failed
expired
deleted
quarantined
```

Lifecycle:

```text
pending
  ↓
uploading
  ↓
uploaded
  ↓
processing
  ↓
ready
```

Failure:

```text
uploaded
  ↓
processing
  ↓
failed
```

Security:

```text
uploaded
  ↓
quarantined
```

Expiration:

```text
ready
  ↓
expired
  ↓
deleted
```

---

# 11. File Categories

The system should distinguish:

```text
image
document
pdf
svg
video
audio
archive
ai_input
ai_output
export
avatar
other
```

Not every category must be supported initially.

---

# 12. Upload Architecture

Preferred flow:

```text
1. User selects file
2. Frontend requests upload permission
3. Backend validates user/quota
4. Backend generates signed upload URL
5. Browser uploads directly to object storage
6. Storage upload completes
7. Frontend confirms upload
8. Backend verifies file
9. File becomes available
```

This prevents large files from passing through Django.

---

# 13. Upload API

Example:

```text
POST /api/v1/files/upload-url
```

Request:

```json
{
  "filename": "photo.jpg",
  "content_type": "image/jpeg",
  "size": 2450000
}
```

Response:

```json
{
  "file_id": "file_xxx",
  "upload_url": "...",
  "storage_key": "users/.../file_xxx"
}
```

After upload:

```text
POST /api/v1/files/{file_id}/complete
```

---

# 14. Direct-to-Storage Upload

The preferred upload mechanism is:

```text
Browser
   │
   │ Signed PUT/POST
   ▼
S3
```

Not:

```text
Browser
   ↓
Django
   ↓
S3
```

The first approach is more scalable.

---

# 15. Upload Validation

Before issuing an upload URL, validate:

- authenticated user
- file size
- allowed MIME type
- extension
- plan restrictions
- quota
- tool restrictions
- batch limits

After upload, validate again.

Client-side validation alone is insufficient.

---

# 16. MIME Validation

Do not trust:

```text
filename extension
```

For example:

```text
image.jpg
```

does not guarantee the file is actually a JPEG.

The backend/worker should inspect the actual file content.

---

# 17. File Size Limits

Limits should be configurable by plan.

Example:

```text
Free:
10 MB

Basic:
25 MB

Pro:
100 MB

Business:
500 MB
```

These are examples and should be configurable.

---

# 18. Image Validation

For image files validate:

- actual MIME type
- dimensions
- color mode
- corruption
- maximum pixel count
- animation support
- metadata

Protect against decompression bombs and extremely large images.

---

# 19. PDF Validation

Validate:

- MIME type
- file size
- page count
- malformed PDF
- encrypted PDF handling
- dangerous embedded content where applicable

---

# 20. SVG Security

SVG files require special handling because they can contain active content.

Do not blindly serve uploaded SVG files as trusted HTML.

Possible controls:

- sanitize SVG
- remove scripts
- remove external references
- restrict dangerous elements
- convert SVG to raster formats when appropriate
- serve untrusted SVG with safe content headers

---

# 21. Filename Handling

Store:

```text
original_name
```

for display.

Storage should use:

```text
file_id
```

or a generated safe key.

Sanitize all filenames.

Never allow:

```text
../
```

path traversal.

---

# 22. File Ownership

Every user-owned file must have an owner.

Example:

```text
File.owner_id
```

Every download request must verify:

```text
request.user == file.owner
```

or an explicit permission grants access.

Never rely on obscurity of file IDs.

---

# 23. Visibility

Files should have explicit visibility:

```text
private
public
shared
temporary
```

Default:

```text
private
```

---

# 24. Private Storage

User files should remain private by default.

Recommended:

```text
S3 Block Public Access = enabled
```

Private files should be delivered using signed URLs.

---

# 25. Signed Download URLs

Example flow:

```text
User
 ↓
Django
 ↓
Permission Check
 ↓
Signed URL
 ↓
S3
 ↓
File
```

Signed URLs should:

- expire
- be scoped to the specific object
- not expose permanent public access

---

# 26. Signed URL Expiration

Example:

```text
Download:
5–15 minutes

Upload:
10–30 minutes
```

Values should be configurable.

Long-lived public URLs should not be used for private files.

---

# 27. CDN

For public or frequently accessed assets:

```text
User
 ↓
CDN
 ↓
Object Storage
```

Potential CDN:

```text
CloudFront
```

or another compatible CDN.

Do not put private user files behind a publicly cacheable CDN configuration without carefully controlling authorization.

---

# 28. AI Processing Integration

AI processing uses:

```text
Input File
 ↓
AI Job
 ↓
Worker
 ↓
Output File
```

Example:

```text
ai/{user_id}/inputs/{job_id}/input.jpg

ai/{user_id}/outputs/{job_id}/result.png
```

The AI architecture must use the storage service instead of directly embedding storage logic into every model adapter.

---

# 29. Temporary Processing Storage

Workers may require local temporary storage.

Example:

```text
/tmp/ai/{job_id}/
```

Rules:

- create isolated job directory
- never reuse another user's directory
- remove after processing
- remove on failure
- enforce local disk limits

---

# 30. Temporary File Lifecycle

Example:

```text
Upload
 ↓
Temporary
 ↓
Processing
 ↓
Output
 ↓
Cleanup
```

Temporary files must have automatic expiration.

---

# 31. Retention Policy

Different file types can have different retention periods.

Example:

| File Type | Free | Premium |
|---|---:|---:|
| Temporary files | 1–6 hours | 1–6 hours |
| AI outputs | 24 hours | 30+ days |
| Workspace files | Limited | Long-term |
| Failed jobs | Short retention | Short retention |
| Batch exports | 24 hours | Configurable |

These values must be configurable.

---

# 32. Automatic Cleanup

A scheduled cleanup worker should remove expired files.

Example:

```text
Celery Beat
   ↓
Cleanup Task
   ↓
Find expired files
   ↓
Delete object
   ↓
Update database
```

Never rely only on manual deletion.

---

# 33. Storage Lifecycle Rules

Object storage lifecycle policies should also be configured.

Example:

```text
temporary/*
  → delete after X hours

ai/temporary/*
  → delete after X hours

exports/*
  → delete after X days
```

Application-level cleanup and storage lifecycle rules should complement each other.

---

# 34. Soft Delete

For important user files, use soft deletion first.

Example:

```text
deleted_at = timestamp
```

Then permanently remove after a grace period.

Benefits:

- accidental deletion recovery
- safer operations
- auditability

---

# 35. Permanent Delete

Permanent deletion should remove:

```text
database metadata
+
object storage object
+
derived files
+
thumbnails
+
cached copies
```

Deletion should be idempotent.

---

# 36. Derived Files

A single source file may produce:

```text
Original
 ├── Thumbnail
 ├── Preview
 ├── Optimized version
 ├── AI output
 └── Export
```

These should be related through metadata.

Example:

```text
parent_file_id
```

---

# 37. Thumbnail Architecture

For image-based tools:

```text
Original
 ↓
Thumbnail Worker
 ↓
Small Preview
```

Store thumbnails separately:

```text
previews/{file_id}/small.webp
previews/{file_id}/medium.webp
```

Do not load full-resolution images just to display thumbnails.

---

# 38. Image Optimization

Where appropriate:

- WebP
- AVIF
- JPEG
- PNG

should be generated according to use case.

Original files should be preserved when required by the product.

---

# 39. File Hashing

Calculate a checksum such as:

```text
SHA-256
```

Use it for:

- integrity
- duplicate detection
- upload verification
- debugging

Do not rely on checksum alone for security authorization.

---

# 40. Duplicate Detection

The platform may detect duplicate uploads using:

```text
hash
+
size
+
optional perceptual hash
```

Possible future feature:

```text
"This file already exists in your workspace."
```

This can reduce storage costs.

---

# 41. Storage Quotas

Every account should have storage limits.

Example:

```text
Free:
100 MB

Basic:
2 GB

Pro:
20 GB

Business:
100 GB+
```

These values are examples.

The quota system must be configurable.

---

# 42. Quota Calculation

Track:

```text
storage_used_bytes
storage_limit_bytes
```

Do not calculate total storage from millions of objects on every request.

Maintain aggregate usage.

---

# 43. Storage Usage Model

Conceptual:

```text
StorageUsage

user_id
used_bytes
file_count
last_calculated_at
```

The system should reconcile usage periodically.

---

# 44. Subscription Integration

Storage permissions depend on subscription.

Example:

```text
Free
 ├── limited storage
 ├── short retention
 └── limited history

Premium
 ├── more storage
 ├── longer retention
 ├── workspace
 └── larger files
```

The storage layer should query subscription/entitlement services rather than hard-code plan names.

---

# 45. User Workspace

Premium users may receive:

```text
My Files
Projects
AI History
Exports
Shared Files
Trash
```

Example:

```text
Dashboard
 ├── Workspace
 │   ├── Files
 │   ├── Projects
 │   ├── AI Results
 │   └── Exports
 └── Trash
```

---

# 46. Project-Based Organization

Files may optionally belong to a project.

Example:

```text
Project
 ├── Product Images
 ├── Logos
 ├── AI Outputs
 └── Exports
```

Conceptual relationship:

```text
User
 ↓
Project
 ↓
File
```

---

# 47. File Sharing

Future premium feature:

```text
Generate Share Link
```

Example:

```text
User
 ↓
Share File
 ↓
Secure Token
 ↓
Recipient
```

Share links should support:

- expiration
- password protection
- download limit
- revoke
- access logging

---

# 48. Temporary File Sharing

For a temporary file-sharing tool:

```text
Upload
 ↓
Generate temporary URL
 ↓
Share
 ↓
Expiration
 ↓
Automatic deletion
```

Example expiration options:

```text
10 minutes
1 hour
24 hours
7 days
```

---

# 49. File Access Logs

For sensitive/private sharing:

```text
FileAccessLog

file_id
user_id
share_id
ip_hash
user_agent
action
timestamp
```

Possible actions:

```text
view
download
share
delete
```

Privacy requirements must be considered before storing IP-related data.

---

# 50. Security Headers

File responses should use appropriate headers.

Examples:

```text
Content-Type
Content-Disposition
X-Content-Type-Options
Cache-Control
Content-Security-Policy
```

Do not allow browsers to interpret arbitrary uploaded content as executable HTML.

---

# 51. Malware / Virus Scanning

For higher-risk uploads, introduce scanning.

Architecture:

```text
Upload
 ↓
Quarantine
 ↓
Security Scan
 ↓
Safe
 ↓
Available
```

If unsafe:

```text
Quarantine
 ↓
Rejected
```

A scanning service can be introduced initially or as traffic grows.

---

# 52. Quarantine Storage

Potential structure:

```text
quarantine/{file_id}
```

Quarantined files must not be downloadable by normal users.

---

# 53. Encryption

Use encryption at rest through the storage provider.

For AWS S3:

```text
Server-Side Encryption
```

For highly sensitive data, consider customer-managed keys where justified.

All network traffic must use:

```text
HTTPS/TLS
```

---

# 54. Database and Object Storage Relationship

The database stores metadata.

Object storage stores file bytes.

```text
Database
 ├── file_id
 ├── owner
 ├── storage_key
 ├── mime_type
 ├── size
 └── status

Object Storage
 └── actual file bytes
```

Never store large binary files directly in MySQL unless there is a strong reason.

---

# 55. Django File Model

Conceptual model:

```python
class File(models.Model):
    id = models.UUIDField(...)
    owner = models.ForeignKey(User, ...)
    project = models.ForeignKey(Project, null=True, ...)
    original_name = models.CharField(...)
    storage_key = models.CharField(unique=True, ...)
    mime_type = models.CharField(...)
    size = models.BigIntegerField(...)
    checksum = models.CharField(...)
    status = models.CharField(...)
    visibility = models.CharField(...)
    expires_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(...)
    updated_at = models.DateTimeField(...)
```

Actual implementation should follow the project's established Django domain-model architecture.

---

# 56. Storage Service Structure

Suggested backend structure:

```text
apps/
└── files/
    ├── models/
    ├── serializers/
    ├── views/
    ├── services/
    │   ├── storage_service.py
    │   ├── upload_service.py
    │   ├── download_service.py
    │   ├── deletion_service.py
    │   ├── quota_service.py
    │   ├── validation_service.py
    │   └── retention_service.py
    ├── tasks/
    │   ├── cleanup.py
    │   ├── reconciliation.py
    │   └── validation.py
    ├── validators/
    └── permissions/
```

---

# 57. File API

Recommended endpoints:

```text
POST   /api/v1/files/upload-url
POST   /api/v1/files/{id}/complete
GET    /api/v1/files/{id}
GET    /api/v1/files/{id}/download-url
DELETE /api/v1/files/{id}
GET    /api/v1/files
POST   /api/v1/files/{id}/restore
```

For sharing:

```text
POST   /api/v1/files/{id}/share
DELETE /api/v1/shares/{id}
GET    /api/v1/shares/{token}
```

---

# 58. File Listing

File listing must support:

- pagination
- search
- filtering
- sorting
- project filtering
- file type filtering
- date filtering
- status filtering

Never return millions of files in one API response.

---

# 59. Pagination

Use cursor pagination for large collections where appropriate.

Example:

```text
GET /api/v1/files?cursor=...
```

---

# 60. Batch Upload

The frontend may allow:

```text
Select 5–100 files
```

depending on plan.

The backend should create independent file records.

Example:

```text
Batch Upload
 ├── File 1
 ├── File 2
 ├── File 3
 └── File 4
```

---

# 61. Batch Export

After processing:

```text
Results
 ↓
ZIP Worker
 ↓
ZIP File
 ↓
Object Storage
 ↓
Signed Download
```

ZIP files should also have expiration policies.

---

# 62. Large File Uploads

For large files, use multipart/resumable upload.

Potential architecture:

```text
Browser
 ↓
Multipart Upload
 ↓
S3
```

This allows:

- pause
- resume
- parallel upload
- failure recovery

Implement when required by actual product limits.

---

# 63. Storage Cost Optimization

Major cost sources:

```text
Storage
Data Transfer
API Requests
AI Processing
CDN
Backups
```

Optimization:

- automatic expiration
- lifecycle rules
- compression
- deduplication
- thumbnails
- CDN caching for public assets
- delete abandoned uploads
- avoid unnecessary copies
- move cold data to cheaper tiers when appropriate

---

# 64. Storage Cost Monitoring

Track:

```text
storage_bytes
file_count
uploads_per_day
downloads_per_day
egress_bytes
temporary_storage
AI_output_storage
workspace_storage
```

This data should be available to administrators.

---

# 65. Storage Alerts

Set alerts for:

```text
Storage > expected threshold
Unexpected upload spike
Unexpected download spike
High egress
High failed upload rate
High temporary-file accumulation
```

---

# 66. Backup Strategy

The database and object storage require different backup strategies.

Database:

```text
Automated backups
Point-in-time recovery where available
```

Object storage:

```text
Versioning where appropriate
Replication where justified
Lifecycle policies
Backup of critical assets
```

User-generated temporary files generally do not need indefinite backup.

---

# 67. Disaster Recovery

Recovery plan should define:

```text
RPO
RTO
```

Example initial targets:

```text
RPO: 24 hours
RTO: 4 hours
```

Production targets can be improved as the business grows.

---

# 68. Orphan File Detection

An orphan file is:

```text
Object exists
BUT
Database record does not exist
```

The system should periodically detect orphaned objects.

Process:

```text
Object Storage Inventory
 ↓
Compare with Database
 ↓
Find Orphans
 ↓
Review
 ↓
Delete
```

---

# 69. Missing Object Detection

The opposite case:

```text
Database record exists
BUT
Object does not exist
```

Mark the file:

```text
missing
```

and notify administrators if required.

---

# 70. Storage Reconciliation

Scheduled job:

```text
Daily / periodic reconciliation
```

Checks:

- object existence
- database metadata
- storage usage
- expired files
- orphan objects
- missing objects
- inconsistent status

---

# 71. File Processing State

Storage and processing status must remain separate.

Example:

```text
File status:
uploaded

AI Job status:
processing
```

Do not overload one field to represent both.

---

# 72. Storage Events

Future event-driven architecture may use:

```text
Object Uploaded
Object Deleted
Object Validated
Object Expired
```

Events can trigger:

- validation
- thumbnail generation
- AI processing
- cleanup
- analytics

---

# 73. Event Architecture

Future:

```text
S3 Event
 ↓
Queue
 ↓
Worker
 ↓
Application Event
```

This should be introduced only when operationally useful.

---

# 74. Anonymous File Storage

Anonymous tools may create temporary files.

Example:

```text
anonymous/{session_id}/{file_id}
```

Strict rules:

- short retention
- small file limit
- low batch limit
- no permanent workspace
- aggressive cleanup

---

# 75. Authentication Requirements

Authenticated users can access:

```text
Persistent Workspace
History
Projects
Saved Results
```

Anonymous users should generally receive:

```text
Temporary processing
Temporary download
```

without permanent storage.

---

# 76. Storage Permissions

Permissions should be checked at the service layer.

Possible permissions:

```text
file.read
file.write
file.delete
file.share
file.restore
project.manage
```

Subscription entitlements must not replace authorization.

Both should be checked where appropriate.

---

# 77. Admin Access

Administrators may need access to:

- file metadata
- storage usage
- failed files
- quarantined files
- orphan objects
- storage costs
- abuse reports

Admins should not automatically receive unrestricted access to private file contents unless the product's privacy policy and operational procedures explicitly allow it.

---

# 78. Admin Storage Dashboard

Possible metrics:

```text
Total Storage
Active Files
Temporary Files
AI Output Storage
Top Storage Users
Daily Uploads
Daily Downloads
Storage Cost
Expired Files
Orphan Files
Quarantined Files
```

---

# 79. Rate Limiting

Protect file endpoints:

```text
Upload URL
Download URL
Delete
Share
Batch Upload
```

Limits should vary based on:

- IP
- user
- plan
- API key
- endpoint

---

# 80. Abuse Protection

Potential abuse:

- massive uploads
- repeated download requests
- storage exhaustion
- bandwidth abuse
- malicious files
- automated scraping

Controls:

```text
Rate limiting
Quota
CAPTCHA
Authentication
File limits
Download limits
Monitoring
```

---

# 81. Privacy Principles

The platform should follow data minimization.

Store only what is required.

For example, do not retain:

- unnecessary metadata
- unnecessary access logs
- unnecessary copies
- unnecessary temporary files

Provide clear deletion behavior.

---

# 82. User Deletion

When a user deletes their account:

```text
User Deletion Request
 ↓
Disable Account
 ↓
Schedule Data Deletion
 ↓
Delete Workspace Files
 ↓
Delete Temporary Files
 ↓
Delete AI Outputs
 ↓
Delete Projects
 ↓
Delete File Metadata
```

Legal retention requirements must be handled separately where applicable.

---

# 83. Account Data Export

Future feature:

```text
Export My Data
```

The system can create:

```text
ZIP
 ├── files
 ├── metadata
 └── project information
```

The export itself must expire.

---

# 84. Download Tracking

Track downloads for product analytics.

Example:

```text
file_id
user_id
tool
timestamp
size
```

Avoid collecting unnecessary personal information.

---

# 85. Storage Observability

Metrics:

```text
uploads_total
upload_failures
downloads_total
download_failures
storage_bytes
storage_files
expired_files
orphan_files
missing_files
temporary_files
```

---

# 86. Logging

Log:

```text
file_id
action
status
duration
error_code
timestamp
```

Never log:

- file contents
- signed URLs unnecessarily
- private credentials
- secret tokens

---

# 87. Error Handling

Standard error codes:

```text
FILE_TOO_LARGE
UNSUPPORTED_FILE
INVALID_MIME
UPLOAD_FAILED
STORAGE_UNAVAILABLE
FILE_NOT_FOUND
ACCESS_DENIED
QUOTA_EXCEEDED
FILE_EXPIRED
FILE_QUARANTINED
DELETE_FAILED
```

User-facing messages should be understandable.

---

# 88. Frontend Components

Recommended reusable components:

```text
FileUploader
DragDropUploader
UploadProgress
FilePreview
ImagePreview
PDFPreview
FileList
FileCard
FileActions
StorageUsageBar
QuotaWarning
DownloadButton
ShareDialog
DeleteConfirmation
BatchUploader
ProcessingResult
```

---

# 89. Upload UX

The upload UI should show:

```text
Selected files
File size
Upload progress
Validation errors
Processing state
Completed state
Retry
Cancel
Remove
```

For batch processing:

```text
10 files
7 uploaded
2 processing
1 failed
```

---

# 90. Premium Conversion UX

Storage limits can naturally support subscription conversion.

Example:

```text
Storage:
95 MB / 100 MB

"You're almost out of storage."

Upgrade to Pro
```

Another:

```text
Your file is 35 MB.

Free plan supports up to 10 MB.

Upgrade to upload larger files.
```

Premium prompts should be contextual rather than intrusive.

---

# 91. AI + Storage + Subscription Flow

Complete premium workflow:

```text
User
 ↓
Upload
 ↓
Quota Check
 ↓
Subscription Check
 ↓
Signed Upload
 ↓
S3
 ↓
AI Job
 ↓
Queue
 ↓
Worker
 ↓
AI Output
 ↓
S3
 ↓
Storage Usage Update
 ↓
Credit Deduction
 ↓
Signed Download
```

---

# 92. File Lifecycle Example

Example background-removal request:

```text
1. User uploads photo
2. Backend creates File record
3. Browser uploads to S3
4. File becomes uploaded
5. Validation runs
6. AI Job created
7. Worker downloads input
8. AI model processes image
9. Output uploaded to S3
10. Output File record created
11. Credits deducted
12. Job becomes completed
13. User receives signed download URL
14. Temporary files are deleted
15. Output remains according to retention policy
```

---

# 93. Recommended Initial Implementation

Do not build every storage feature immediately.

MVP should include:

1. Private S3 storage
2. Direct browser uploads
3. Signed upload URLs
4. Signed download URLs
5. File metadata model
6. File ownership
7. MIME validation
8. Size validation
9. Temporary file expiration
10. AI input/output storage
11. Automatic cleanup
12. Storage quota
13. Basic file history
14. Secure deletion
15. Basic monitoring

---

# 94. Phase 2

Add:

1. Batch upload
2. Batch output ZIP
3. Thumbnails
4. Workspace
5. Projects
6. File search
7. File sharing
8. Soft delete/trash
9. Storage usage dashboard
10. Advanced retention policies

---

# 95. Phase 3

Add:

1. Multipart upload
2. CDN
3. Advanced virus scanning
4. Deduplication
5. Storage reconciliation
6. Advanced analytics
7. Data export
8. Advanced sharing
9. Storage cost optimization
10. Multi-provider storage abstraction

---

# 96. Phase 4

Add:

1. Multi-region storage
2. Cross-region replication
3. Advanced disaster recovery
4. Intelligent storage tiering
5. Enterprise retention policies
6. Enterprise storage controls
7. Advanced audit logs

---

# 97. Recommended Storage Architecture

```text
                         USER
                           │
                           ▼
                    NEXT.JS FRONTEND
                           │
                           ▼
                    DJANGO REST API
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
      AUTH/ACL         SUBSCRIPTION       QUOTA
          │                │                 │
          └────────────────┼─────────────────┘
                           ▼
                    STORAGE SERVICE
                           │
              ┌────────────┴─────────────┐
              │                          │
              ▼                          ▼
       SIGNED UPLOAD                SIGNED DOWNLOAD
              │                          │
              ▼                          ▲
        OBJECT STORAGE                   │
              │                          │
      ┌───────┼────────┐                 │
      ▼       ▼        ▼                 │
   INPUTS   OUTPUTS  PROJECTS             │
      │       │        │                 │
      └───────┼────────┘                 │
              ▼                          │
         PROCESSING                      │
              │                          │
              ▼                          │
        CPU/GPU WORKERS                  │
              │                          │
              ▼                          │
        GENERATED FILE ──────────────────┘
```

---

# 98. Storage Architecture Rules for AI Coding Agents

AI coding agents must follow these rules:

1. Never store user files permanently on the application server.
2. Never expose the S3 bucket publicly for private files.
3. Always use signed URLs for private uploads/downloads.
4. Never trust file extensions.
5. Always validate MIME type and file size.
6. Always associate files with an owner.
7. Always check authorization before access.
8. Never use user-provided filenames as storage keys.
9. Always generate unique storage keys.
10. Always clean temporary files.
11. Always enforce storage quotas.
12. Always track file lifecycle status.
13. Always separate database metadata from binary storage.
14. Never put large binary files in MySQL by default.
15. Always use the storage service abstraction.
16. Never hard-code AWS logic throughout business code.
17. Always design for S3-compatible storage replacement.
18. Always use private storage by default.
19. Always validate uploaded SVG files.
20. Always protect workers from malicious or oversized files.
21. Always make deletion idempotent.
22. Always support expiration for temporary files.
23. Never expose permanent private object URLs.
24. Never log secrets or signed URLs unnecessarily.
25. Always maintain storage usage information.
26. Always monitor orphan and missing files.
27. Keep AI input/output storage integrated with the same abstraction.
28. Do not implement expensive storage features before they are required.
29. Do not allow a single user to exhaust storage or bandwidth.
30. New file-related features must reuse the existing storage architecture.

---

# 99. Definition of Done

The storage architecture is production-ready when:

- [ ] Object storage is configured
- [ ] Private bucket policy is configured
- [ ] Direct upload works
- [ ] Signed upload URLs work
- [ ] Signed download URLs work
- [ ] File metadata model exists
- [ ] Ownership checks exist
- [ ] MIME validation exists
- [ ] File size validation exists
- [ ] Image validation exists
- [ ] SVG security exists
- [ ] Temporary files expire automatically
- [ ] AI inputs and outputs use object storage
- [ ] Storage quotas work
- [ ] Subscription entitlements affect storage
- [ ] File deletion works
- [ ] Soft delete is available where required
- [ ] Cleanup workers exist
- [ ] Storage lifecycle rules exist
- [ ] Orphan detection exists
- [ ] Storage reconciliation exists
- [ ] Basic monitoring exists
- [ ] Error handling exists
- [ ] Rate limiting exists
- [ ] Backup strategy exists
- [ ] Disaster recovery strategy exists
- [ ] Storage service abstraction exists
- [ ] The system can switch to an S3-compatible provider without rewriting business logic

---

# 100. Final Principle

The platform's file system should be treated as a **core infrastructure service**, not as a simple upload feature.

The long-term architecture is:

```text
Files
   ↓
Storage Service
   ↓
Object Storage
   ↓
Validation
   ↓
Processing
   ↓
AI / Utility Tools
   ↓
Outputs
   ↓
Workspace
   ↓
Subscription
   ↓
Analytics
```

This architecture allows the platform to start with a small number of high-demand tools and progressively grow into a large utility ecosystem while keeping file storage secure, scalable, cost-controlled, and compatible with AI processing.
