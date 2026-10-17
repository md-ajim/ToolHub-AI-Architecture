# 📘 AI_DEVELOPER_GUIDE.md

Version: 1.0

Status: Draft

---

# Purpose

This guide provides conventions, onboarding steps, and expectations for developers (human and AI) contributing to the project.

---

# Quick Onboarding

- Read `00-README_FOR_AI.md` and `00.1-AI_PROJECT_CONTEXT.md` first.
- Read the Product Vision and System Architecture.
- Run local linters and tests before opening PRs.

---

# Coding Standards

- Languages: TypeScript (frontend), Python/Django (backend).
- Formatting: Prettier / Black. Use project's config files.
- Type-safety: Prefer TypeScript types and Django model validations.
- Tests: Write unit tests for logic and integration tests for APIs.

---

# Pull Request Workflow

- Create small, focused PRs.
- Include an implementation summary and impact statement.
- Link relevant docs and architecture decisions.
- Add tests and update documentation when behavior changes.

---

# Documentation Rules

- Every feature change that affects APIs, DB schemas, or UX must update docs.
- Use `docs/templates/Documentation_Template.md` for new documents.
- Add `Last Updated` metadata and `Dependencies` section for traceability.

---

# AI Agent Guidelines

- Always present a short plan before making code changes.
- Use the repository's todo tracking for multi-step tasks.
- Avoid changing architecture without explicit human approval.

---

# Testing & CI

- Ensure unit tests pass locally.
- Run linters and static checks in CI.
# AI_DEVELOPER_GUIDE.md

# AI Developer Guide

**Project:** AI-Powered Utility Platform  
**Document Type:** Master AI Engineering Guide  
**Version:** 1.0  
**Status:** Mandatory  
**Audience:** AI Coding Agents, Developers, Reviewers  
**Priority:** Critical

---

# 1. Purpose

This document defines the mandatory engineering rules for every AI Coding Agent working on this project.

It is the project's:

- AI Development Constitution
- Engineering Standard
- Coding Policy
- Architecture Guardrail
- Quality Gate
- Feature Completion Framework

Every AI Coding Agent MUST follow this document.

No AI agent may intentionally ignore these rules unless an explicit project owner instruction overrides them.

---

# 2. Project Mission

The project is a large-scale, SEO-first, AI-powered online utility platform.

The platform will provide many high-quality tools for everyday users, including but not limited to:

- Image tools
- AI image tools
- PDF tools
- Document tools
- Text tools
- Productivity tools
- Developer tools
- SEO tools
- File processing tools
- Social media tools
- E-commerce tools
- Business tools

The long-term target is 100+ tools and continuous expansion.

The platform must be capable of supporting:

- Large global traffic
- Millions of users
- Large file-processing workloads
- AI workloads
- Subscription customers
- High-volume API usage
- Continuous SEO growth

---

# 3. Business Objectives

Primary objectives:

1. Build a globally useful utility platform.
2. Generate large-scale organic traffic.
3. Provide a strong free tier.
4. Convert a meaningful percentage of users into subscribers.
5. Build recurring revenue.
6. Build a long-term technology brand.

Target revenue:

**$5,000–$20,000+/month**

This target is a business objective.

It must never justify:

- Poor security
- Dark patterns
- Fake claims
- Spam
- Misleading SEO
- Poor user experience
- Unnecessary data collection

---

# 4. Core Engineering Principles

Always prioritize:

1. Correctness
2. Security
3. Maintainability
4. Scalability
5. Performance
6. User experience
7. Accessibility
8. Testability
9. Observability
10. Documentation

Do not optimize only for speed of implementation.

---

# 5. Source of Truth

The project documentation is the primary architectural source of truth.

AI must consult documentation before implementation.

Required starting documents:

```text
00-README_FOR_AI.md

00.1-AI_PROJECT_CONTEXT.md

AI_DEVELOPER_GUIDE.md

01-product-vision.md
```

Then read the relevant architecture documents.

---

# 6. Documentation Hierarchy

When documents conflict, use this priority:

```text
Explicit Project Owner Instruction
        ↓
AI_DEVELOPER_GUIDE.md
        ↓
System Architecture
        ↓
Domain Model
        ↓
Feature Architecture
        ↓
Implementation Details
        ↓
Existing Code
```

If an apparent conflict exists, do not silently choose.

Explain the conflict and request clarification when necessary.

---

# 7. Mandatory Task Workflow

Every significant task MUST follow this process.

```text
Understand
    ↓
Read Documentation
    ↓
Inspect Existing Code
    ↓
Identify Dependencies
    ↓
Identify Risks
    ↓
Create Plan
    ↓
Implement
    ↓
Test
    ↓
Review
    ↓
Update Documentation
    ↓
Final Verification
```

Never skip directly from request to code for complex tasks.

---

# 8. Requirement Analysis

Before implementation, determine:

- What problem is being solved?
- Who is the user?
- What is the expected behaviour?
- What are the inputs?
- What are the outputs?
- What can fail?
- What permissions are required?
- What data is stored?
- What APIs are affected?
- What existing components can be reused?
- What analytics are required?
- What SEO implications exist?
- What security risks exist?
- What performance implications exist?

---

# 9. Requirement Completeness

For every production feature, evaluate:

```text
Product
UI/UX
Frontend
Backend
Database
API
Authentication
Authorization
Validation
Security
Storage
Queue
AI
Analytics
SEO
Accessibility
Performance
Testing
Logging
Monitoring
Documentation
Deployment
```

Not every feature requires every category.

However, every category MUST be considered.

---

# 10. Planning Before Coding

For medium or large tasks, the AI must first provide:

## Understanding

What the task means.

## Impact Analysis

What parts of the system will change.

## Implementation Plan

Step-by-step plan.

## Risks

Potential problems.

## Testing Strategy

How correctness will be verified.

For high-risk architecture changes, implementation must not begin until approved by the project owner.

---

# 11. Architecture Rules

The architecture must remain:

- Modular
- Maintainable
- Scalable
- Testable
- Observable
- Secure

Do not introduce architecture patterns merely because they are fashionable.

Use existing project patterns whenever appropriate.

---

# 12. Separation of Concerns

Never mix unrelated responsibilities.

Frontend:

```text
Presentation
State
User Interaction
API Communication
```

Backend:

```text
API
Validation
Business Logic
Domain Logic
Persistence
Infrastructure
```

Business logic must not be unnecessarily embedded in:

- React components
- Django views
- serializers
- URL configuration

---

# 13. Reusability Rule

Before creating a new component, service, utility, hook, or helper:

Search the existing codebase.

If an existing abstraction can be reused, reuse it.

Do not create duplicates such as:

```text
ImageUpload.tsx
ImageUploader.tsx
UploadImage.tsx
UniversalImageUpload.tsx
```

when one reusable component is sufficient.

---

# 14. Avoid Over-Abstraction

Do not create abstractions only for theoretical future use.

Abstractions should solve real repeated problems.

Prefer:

```text
Simple + Reusable
```

over:

```text
Complex + Generic for every possible future
```

---

# 15. Backend Standards

Backend stack:

- Python
- Django
- Django REST Framework

Backend code must be:

- Typed where practical
- Modular
- Testable
- Explicit
- Secure

---

# 16. Django Architecture

Avoid placing large business logic inside:

- Views
- Serializers
- URL configuration

Use appropriate:

- Services
- Domain logic
- Selectors/query services
- Tasks
- Validators

Use Django models primarily for:

- Data representation
- Relationships
- Constraints
- Model-level behaviour

---

# 17. Django Models

Models MUST use:

- Appropriate indexes
- Appropriate constraints
- Explicit relationships
- Meaningful field names

Avoid unnecessary fields.

Never store derived data unless there is a clear reason.

Database constraints should protect important invariants.

---

# 18. Database Rules

Use PostgreSQL in production.

Database design must consider:

- Indexes
- Constraints
- Foreign keys
- Unique constraints
- Query performance
- Data growth
- Pagination
- Transaction boundaries

Never make destructive schema changes casually.

---

# 19. Migration Rules

Every database change must use a proper migration.

Never manually modify production database schema without an approved migration strategy.

Before applying a destructive migration:

- Identify affected data.
- Create backup strategy.
- Verify rollback strategy.
- Review production impact.

---

# 20. API Standards

All APIs must be:

- Consistent
- Versionable
- Documented
- Secure
- Validated

Use predictable:

```text
GET
POST
PUT/PATCH
DELETE
```

patterns.

API response formats must remain consistent.

---

# 21. API Validation

Never trust client-side validation alone.

Validate on the backend.

Validate:

- Type
- Length
- Format
- File type
- File size
- Permissions
- Business rules

---

# 22. API Error Handling

Errors must be structured.

Never expose:

- Stack traces
- Database errors
- Internal paths
- Secrets
- Infrastructure details

Production errors should provide useful user-safe messages.

---

# 23. Authentication

Authentication must support the architecture defined in:

```text
09-authentication-and-authorization.md
```

Security requirements include:

- Secure password handling
- Token protection
- Refresh token security
- Email verification
- Password reset
- Session management
- Rate limiting

---

# 24. Authorization

Authentication answers:

> Who are you?

Authorization answers:

> What are you allowed to do?

Every protected action must verify authorization.

Never rely only on frontend restrictions.

---

# 25. Role-Based Access

Support appropriate roles such as:

```text
Guest
User
Pro
Team
Enterprise
Moderator
Support Admin
Content Admin
Finance Admin
Platform Admin
Super Admin
```

Only implement roles required by the current product stage.

---

# 26. Frontend Standards

Frontend stack:

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

Prefer:

- Server Components
- Server-side rendering where appropriate
- Static generation where appropriate
- Streaming where useful

Use Client Components only when client-side behaviour is required.

---

# 27. Component Rules

Components must be:

- Reusable
- Accessible
- Predictable
- Focused

Avoid huge components.

If a component has multiple unrelated responsibilities, split it.

---

# 28. UI Consistency

All pages must follow the project Design System.

Do not introduce arbitrary:

- Colors
- Font sizes
- Spacing
- Border radii
- Shadows
- Buttons

Reuse design tokens and shared components.

---

# 29. Responsive Design

Every public feature must work on:

- Mobile
- Tablet
- Desktop
- Large screens

Do not treat mobile as an afterthought.

---

# 30. Accessibility

Every interactive interface should support:

- Keyboard navigation
- Focus states
- Screen readers
- Semantic HTML
- Accessible labels
- Appropriate ARIA attributes

Do not use ARIA when normal semantic HTML already solves the problem.

---

# 31. Loading States

Every asynchronous user action must have an appropriate state:

```text
Idle
Loading
Processing
Success
Error
```

Never leave users wondering whether an operation is running.

---

# 32. Empty States

Empty states must clearly explain:

- What is missing
- Why it matters
- What the user can do next

---

# 33. Error States

Errors should be:

- Understandable
- Actionable
- Non-technical where possible

Bad:

```text
500 Internal Server Error
```

Better:

```text
Something went wrong while processing your file.
Please try again.
```

---

# 34. File Upload Security

Never trust file extensions.

Validate:

- MIME type
- File signature where appropriate
- Size
- Filename
- Content

Use appropriate:

- Storage isolation
- Signed URLs
- Temporary storage
- Expiration policies

Never execute uploaded files.

---

# 35. File Processing

Heavy processing must not block web requests.

Use:

```text
API
 ↓
Job Queue
 ↓
Worker
 ↓
Processor
 ↓
Storage
 ↓
Result
```

Use Celery/Redis or the architecture defined by the project.

---

# 36. AI Processing

AI processing must consider:

- Cost
- Latency
- Queueing
- Retry
- Timeout
- Failure
- Provider availability
- Usage limits

Never assume an external AI API is always available.

---

# 37. AI Provider Abstraction

Avoid tightly coupling the entire application to one AI provider.

Where appropriate, use a provider abstraction that allows:

```text
Provider A
Provider B
Provider C
```

without rewriting business logic.

---

# 38. AI Cost Control

AI features must support:

- Usage tracking
- Credit limits
- Rate limits
- Cost monitoring
- Abuse prevention

Premium AI features must have clear consumption rules.

---

# 39. Storage

Use the architecture defined in:

```text
13-storage-file-management-architecture.md
```

Separate:

- Temporary files
- User files
- Processed files
- Public assets
- Private assets

Do not permanently store temporary files unnecessarily.

---

# 40. Subscription System

Subscription architecture must follow:

```text
11-payment-subscription-architecture.md
```

Every subscription-related feature must consider:

- Plan
- Entitlement
- Usage
- Limits
- Billing
- Renewal
- Cancellation
- Refund
- Failed payment
- Grace period

---

# 41. Entitlement Rule

Do not check subscription status directly throughout the application.

Use a centralized entitlement system.

Example:

```text
Can user perform action?
        ↓
Entitlement Service
        ↓
Allow / Deny
```

This makes plans easier to change.

---

# 42. SEO Rules

SEO is a product-level requirement.

Public pages should have:

- Unique title
- Meta description
- Canonical URL
- Open Graph
- Structured data where appropriate
- Internal links
- Useful content

Avoid:

- Keyword stuffing
- Duplicate pages
- Thin content
- Fake reviews
- Fake ratings
- Misleading structured data

---

# 43. Tool SEO

Every important tool should have a dedicated landing page.

A tool page should consider:

```text
Title
Description
Tool UI
Benefits
How to use
FAQ
Related tools
Internal links
Structured data
```

The content must be genuinely useful.

---

# 44. SEO Programmatic Pages

Programmatic pages must not be generated solely to manipulate search rankings.

Every indexed page should provide meaningful unique value.

---

# 45. Analytics

Important user actions should generate analytics events.

Examples:

```text
tool_opened
tool_started
tool_completed
tool_failed
tool_downloaded
subscription_started
subscription_cancelled
search_started
search_no_results
```

Follow:

```text
16-Analytics-Architecture.md
```

---

# 46. Privacy

Collect only data that is necessary.

Never log:

- Passwords
- Authentication secrets
- Payment credentials
- Private file contents unnecessarily
- API keys

Analytics must follow applicable privacy requirements.

---

# 47. Logging

Logs should provide enough information to diagnose problems.

Include where appropriate:

- Timestamp
- Environment
- Service
- Request ID
- Error code
- Operation

Do not expose secrets.

---

# 48. Audit Logging

Sensitive administrative actions should be auditable.

Examples:

```text
User suspended
Subscription changed
Refund issued
Tool disabled
Settings changed
Admin permission changed
```

---

# 49. Monitoring

Monitor:

- API health
- Database
- Redis
- Queue
- Workers
- Storage
- AI providers
- Payment provider
- Error rate
- Latency

Critical failures should trigger alerts.

---

# 50. Caching

Cache only where appropriate.

Potential cache layers:

```text
Browser
CDN
Next.js
Redis
Database query optimization
```

Never cache private user data incorrectly.

---

# 51. Performance

Always consider:

Frontend:

- Bundle size
- Image optimisation
- Lazy loading
- Server rendering
- Core Web Vitals

Backend:

- Query count
- N+1 queries
- Indexes
- Pagination
- Caching
- Async processing

---

# 52. Pagination

Never return unbounded collections.

Use pagination for:

- Users
- Files
- Jobs
- Logs
- Transactions
- Blog posts
- Analytics data

---

# 53. Background Jobs

Use background processing for:

- AI processing
- Large file processing
- Email
- Reports
- Cleanup
- Scheduled tasks
- Heavy analytics processing

---

# 54. Rate Limiting

Rate-limit:

- Authentication
- Password reset
- Uploads
- AI requests
- API requests
- Search abuse
- Public expensive operations

Limits should be configurable.

---

# 55. Abuse Prevention

The platform must anticipate abuse.

Examples:

- Automated uploads
- AI abuse
- File storage abuse
- API abuse
- Account farming
- Payment abuse

Use appropriate:

- Rate limits
- Quotas
- CAPTCHA where justified
- Usage limits
- Monitoring

---

# 56. Testing Strategy

Critical functionality requires automated tests.

Test:

- Business logic
- API
- Authentication
- Authorization
- Payments
- File processing
- AI processing
- Database constraints
- Critical UI flows

---

# 57. Test Pyramid

Prefer:

```text
Many Unit Tests
       ↓
Integration Tests
       ↓
Fewer E2E Tests
```

E2E tests should focus on critical user journeys.

---

# 58. Regression Prevention

Every important bug should result in a regression test where practical.

Fix:

```text
Bug
 ↓
Test
 ↓
Code Fix
```

not simply:

```text
Bug
 ↓
Code Fix
```

---

# 59. Git Rules

Use meaningful commits.

Examples:

```text
feat: add image resizer
fix: handle invalid image uploads
refactor: simplify tool processing service
docs: update API architecture
test: add subscription entitlement tests
```

Avoid meaningless messages:

```text
update
changes
fix
work
```

---

# 60. Branching

Use appropriate branches such as:

```text
main
develop
feature/*
fix/*
hotfix/*
```

The exact strategy may evolve.

Never push unreviewed experimental code directly to production.

---

# 61. Code Review

Review every meaningful change for:

- Correctness
- Security
- Performance
- Maintainability
- Architecture
- Tests
- Documentation

---

# 62. Dependency Policy

Before adding a dependency, determine:

- Is it necessary?
- Is the project maintained?
- Is it secure?
- Does the project already provide the functionality?
- What is its bundle/runtime cost?

Do not add dependencies casually.

---

# 63. Environment Variables

Never hardcode:

- API keys
- Passwords
- Tokens
- Database credentials
- Payment secrets

Use environment variables or secure secret management.

Never commit `.env` secrets.

---

# 64. Configuration

Separate:

```text
Development
Testing
Staging
Production
```

Do not assume production configuration is identical to development.

---

# 65. Deployment

Deployment architecture must follow:

```text
14-deployment-devops-architecture.md
```

Production deployments must be:

- Repeatable
- Observable
- Rollback-capable
- Automated where appropriate

---

# 66. CI/CD

CI should validate:

```text
Install
 ↓
Lint
 ↓
Type Check
 ↓
Tests
 ↓
Build
```

Deployment should occur only after required checks pass.

---

# 67. Database Deployment

Database migrations must be treated as production changes.

Before deployment:

- Review migration
- Check compatibility
- Consider data volume
- Consider locking
- Verify rollback strategy

---

# 68. Admin Panel

Admin functionality must follow:

```text
15-Admin-Architecture.md
```

Admin actions must have:

- Permission checks
- Audit logging
- Confirmation for destructive actions

---

# 69. Analytics

Analytics architecture must follow:

```text
16-Analytics-Architecture.md
```

Do not add random event names.

Follow established naming conventions.

---

# 70. Tool Architecture

Every new tool should reuse the platform's common tool infrastructure.

A tool should generally consist of:

```text
Tool Definition
 ↓
Input
 ↓
Validation
 ↓
Processing
 ↓
Result
 ↓
Storage
 ↓
Download
 ↓
Analytics
```

---

# 71. New Tool Checklist

Before launching a new tool:

## Product

- [ ] Clear user problem
- [ ] Clear target user
- [ ] Free/Premium decision
- [ ] Usage limits defined

## Frontend

- [ ] Tool page
- [ ] Input UI
- [ ] Loading state
- [ ] Error state
- [ ] Result state
- [ ] Download
- [ ] Mobile support

## Backend

- [ ] API
- [ ] Validation
- [ ] Processing
- [ ] Error handling
- [ ] Rate limiting

## Database

- [ ] Required models
- [ ] Indexes
- [ ] Constraints
- [ ] Migration

## Storage

- [ ] Temporary storage
- [ ] Permanent storage if required
- [ ] Cleanup policy

## Security

- [ ] Input validation
- [ ] File validation
- [ ] Permission checks
- [ ] Abuse prevention

## Analytics

- [ ] Tool opened
- [ ] Tool started
- [ ] Tool completed
- [ ] Tool failed
- [ ] Download

## SEO

- [ ] Metadata
- [ ] Canonical
- [ ] Structured data where appropriate
- [ ] Internal links
- [ ] Useful content

## Testing

- [ ] Unit tests
- [ ] API tests
- [ ] Critical E2E test

## Documentation

- [ ] Feature specification
- [ ] API documentation
- [ ] Architecture update if required

---

# 72. AI Self-Review Protocol

Before declaring a task complete, AI MUST review:

### Architecture

Did I violate any architecture rule?

### Reusability

Did I duplicate existing functionality?

### Security

Did I introduce a vulnerability?

### Performance

Did I introduce expensive queries or operations?

### UX

Does the user understand what is happening?

### Accessibility

Can keyboard and assistive technology users operate it?

### SEO

If public, is the page search-engine friendly?

### Analytics

Can we measure important behaviour?

### Testing

Did I test failure cases?

### Documentation

Did I update relevant documents?

---

# 73. Failure Scenario Review

For every feature, consider:

```text
Invalid Input
Missing Input
Large Input
Slow Processing
Timeout
Network Failure
Database Failure
Queue Failure
Storage Failure
Third-party API Failure
Permission Failure
Rate Limit
Duplicate Request
Concurrent Request
Partial Failure
```

The system should fail safely.

---

# 74. Idempotency

Operations that may be retried must be designed carefully.

Examples:

- Payments
- File processing
- Background jobs
- Webhooks

Do not accidentally create duplicate resources when a request is retried.

---

# 75. Webhooks

Webhook handlers must:

- Verify signatures
- Validate payload
- Be idempotent
- Log processing
- Handle retries
- Avoid long blocking operations

---

# 76. API Versioning

Public APIs must be designed for backward compatibility.

Avoid breaking existing clients.

If a breaking change is unavoidable:

```text
New Version
 ↓
Migration Period
 ↓
Deprecation
 ↓
Removal
```

---

# 77. Feature Flags

Large features should support controlled rollout where appropriate.

Possible states:

```text
Disabled
Internal
Beta
Limited Rollout
Public
Deprecated
```

---

# 78. Launch Strategy

Do not automatically release every feature to 100% of users.

For high-risk features:

```text
Development
 ↓
Testing
 ↓
Internal
 ↓
Beta
 ↓
Limited Rollout
 ↓
Public
```

---

# 79. Documentation Maintenance

When code changes architecture, update the corresponding documentation.

Documentation drift is a defect.

---

# 80. Architecture Decision Records

Major architectural decisions should be recorded.

Each ADR should contain:

```text
Context
Decision
Alternatives
Reason
Consequences
```

---

# 81. Refactoring Rules

Do not refactor unrelated code during feature development unless necessary.

Large refactors should be isolated.

Before refactoring:

- Understand dependencies
- Write/verify tests
- Define expected behaviour

After refactoring:

- Run full relevant test suite
- Verify performance
- Verify API compatibility

---

# 82. Technical Debt

Do not hide technical debt.

If a shortcut is necessary:

Document:

- Why
- Impact
- Risk
- Future solution

Create a task for resolving it.

---

# 83. Accessibility as Definition of Done

Accessibility is not an optional polish step.

Every public UI must consider accessibility from the beginning.

---

# 84. Internationalization

The architecture should allow future localization.

Avoid hardcoding user-facing text deeply inside logic.

Design for future:

- Multiple languages
- Locale-specific dates
- Currency
- Number formats
- RTL languages

---

# 85. Localization

Never assume:

- English is the only language
- USD is the only currency
- One date format fits everyone

The initial implementation may launch in one language, but architecture should avoid unnecessary barriers to localization.

---

# 86. Email System

Email functionality should use:

- Templates
- Queues
- Retry
- Delivery tracking where available

Never send large volumes synchronously from web requests.

---

# 87. Notifications

Notification types:

```text
Transactional
Security
Product
Billing
System
Marketing
```

Users should have appropriate preferences for non-essential notifications.

---

# 88. Search

Global search should support:

- Tools
- Blog
- Documentation
- Categories

Search should provide useful results and handle no-result cases.

---

# 89. Recommendation System

Where appropriate, recommend:

- Related tools
- Recently used tools
- Popular tools
- Trending tools

Recommendations should improve usability, not become spam.

---

# 90. Internal Linking

Tool pages should link naturally to:

- Related tools
- Guides
- Blog posts
- Categories

Avoid excessive artificial linking.

---

# 91. Monetization Rules

Premium features must provide genuine value.

Good premium value:

- Higher limits
- Faster processing
- Bulk processing
- Higher quality
- Cloud history
- Advanced features
- API access
- Ad-free experience

Do not intentionally cripple basic functionality solely to force payment.

---

# 92. Free Tier Philosophy

Free tools are a major traffic acquisition mechanism.

A free tool should still be genuinely useful.

The free experience should create trust.

---

# 93. Subscription Integrity

Never:

- Hide cancellation
- Mislead pricing
- Fake scarcity
- Create deceptive countdowns
- Misrepresent free trials

Subscriptions must be transparent.

---

# 94. Cost Awareness

Every expensive feature should have a measurable cost.

Especially:

- AI
- Image processing
- PDF processing
- Storage
- Bandwidth
- Email
- External APIs

Track:

```text
Cost per Job
Cost per User
Cost per Tool
Cost per Subscription
```

---

# 95. Scalability

Design for horizontal scaling where appropriate.

Avoid single-server assumptions.

Heavy workloads should be separable from web traffic.

Example:

```text
Web Servers
      |
      +---- API
      |
      +---- Queue
              |
        Worker Pool
              |
        Processing
```

---

# 96. Reliability

Important operations should support:

- Retry
- Timeout
- Fallback
- Circuit breaking where appropriate
- Graceful degradation

Do not retry blindly.

---

# 97. Graceful Degradation

If an external service fails:

The platform should provide an appropriate fallback where possible.

Example:

AI Provider unavailable

↓

Queue request

or

↓

Offer alternative processing

or

↓

Clearly inform user

---

# 98. Data Integrity

Never prioritise convenience over data integrity.

Use:

- Transactions
- Constraints
- Validation
- Idempotency
- Proper locking where necessary

---

# 99. Concurrency

Consider race conditions for:

- Credits
- Payments
- File processing
- Subscription changes
- Usage limits

Never assume requests happen sequentially.

---

# 100. Security Review Checklist

Before release:

- [ ] Authentication verified
- [ ] Authorization verified
- [ ] Input validation
- [ ] File validation
- [ ] Rate limiting
- [ ] CSRF protection where applicable
- [ ] XSS protection
- [ ] SQL injection protection
- [ ] Secrets protected
- [ ] Secure headers
- [ ] Private files protected
- [ ] Admin permissions reviewed

---

# 101. Performance Review Checklist

Before release:

- [ ] Database queries reviewed
- [ ] N+1 queries checked
- [ ] Pagination implemented
- [ ] Large files handled asynchronously
- [ ] Images optimized
- [ ] Bundle impact checked
- [ ] Caching considered
- [ ] API latency checked

---

# 102. SEO Review Checklist

For every public page:

- [ ] Unique title
- [ ] Meta description
- [ ] Canonical
- [ ] Open Graph
- [ ] Semantic headings
- [ ] Useful content
- [ ] Internal links
- [ ] Structured data where appropriate
- [ ] Mobile friendly
- [ ] Fast loading
- [ ] No accidental noindex

---

# 103. Final Definition of Done

A task is complete ONLY when applicable requirements are satisfied.

```text
Requirement
        ↓
Implementation
        ↓
Validation
        ↓
Security
        ↓
Testing
        ↓
Performance
        ↓
Analytics
        ↓
SEO
        ↓
Documentation
        ↓
Review
        ↓
Production Ready
```

---

# 104. AI Completion Report

After completing a significant task, AI should report:

```text
## Implementation Summary

What was implemented.

## Files Changed

List important files.

## Architecture Impact

None / Describe changes.

## Database Impact

None / Describe migrations.

## API Impact

None / Describe endpoints.

## Security

What was considered.

## Testing

What was tested.

## Documentation

What was updated.

## Remaining Risks

List unresolved issues.

## Recommended Next Step

Next logical task.
```

---

# 105. When AI Must Stop

AI MUST stop and ask the project owner before proceeding if:

- Requirements conflict
- Architecture must change
- A destructive database migration is required
- A breaking API change is required
- Security is uncertain
- Payment behaviour is ambiguous
- Data deletion is irreversible
- Production infrastructure must be changed significantly
- A major dependency must be introduced
- Business rules are unclear

Never guess in high-risk situations.

---

# 106. AI Must Not Claim Success Without Verification

Do not say:

```text
Done
```

unless the relevant checks have actually been performed.

Do not claim:

- Tests passed
- Build passed
- Deployment succeeded
- API works
- Payment works

unless verified.

---

# 107. No Fake Implementation

Never create:

- Fake API responses
- Fake payment success
- Fake analytics
- Fake AI results
- Fake database data
- Placeholder functionality presented as production functionality

If something is mocked for development, clearly mark it as a mock.

---

# 108. No Silent Scope Expansion

Do not add unrelated features simply because they seem useful.

If a useful improvement is discovered:

```text
Current Task
+
Optional Recommendation
```

Keep the implementation scope controlled.

---

# 109. No Silent Breaking Changes

Never silently change:

- API contracts
- Database schema
- URLs
- Authentication
- Subscription rules
- Component contracts

Breaking changes require explicit acknowledgement.

---

# 110. AI Prompt Template

Use this template for major tasks:

```text
TASK

[Describe the task]

READ FIRST

- 00-README_FOR_AI.md
- 00.1-AI_PROJECT_CONTEXT.md
- AI_DEVELOPER_GUIDE.md
- [Relevant documents]

REQUIREMENTS

[List requirements]

CONSTRAINTS

[List constraints]

IMPLEMENTATION

1. Analyse
2. Plan
3. Implement
4. Test
5. Review
6. Update documentation

DO NOT

- Change architecture without approval
- Introduce unnecessary dependencies
- Duplicate existing functionality
- Skip tests
- Skip documentation
```

---

# 111. AI Planning Template

Before implementation:

```text
## Task Understanding

...

## Existing Components

...

## Architecture Impact

...

## Database Impact

...

## API Impact

...

## Security Considerations

...

## Performance Considerations

...

## Analytics

...

## SEO

...

## Testing Plan

...

## Implementation Plan

1.
2.
3.
4.
```

---

# 112. AI Review Template

After implementation:

```text
## Architecture Review

PASS / FAIL

## Security Review

PASS / FAIL

## Performance Review

PASS / FAIL

## Test Review

PASS / FAIL

## SEO Review

PASS / FAIL

## Accessibility Review

PASS / FAIL

## Documentation Review

PASS / FAIL

## Remaining Issues

...

## Final Status

READY / NOT READY
```

---

# 113. Golden Rule

The AI must always remember:

> Do not merely write code. Build a maintainable product.

Every implementation must consider the entire lifecycle:

```text
Idea
 ↓
Architecture
 ↓
Implementation
 ↓
Testing
 ↓
Deployment
 ↓
Monitoring
 ↓
Maintenance
 ↓
Scaling
```

---

# 114. Final AI Instruction

You are not working on an isolated coding task.

You are contributing to a long-term, production-grade, globally scalable utility platform.

Before making any decision, ask:

1. Does this follow the architecture?
2. Does this solve the actual user problem?
3. Is it secure?
4. Is it scalable?
5. Is it maintainable?
6. Is it testable?
7. Is it measurable?
8. Is it accessible?
9. Is it SEO-friendly where applicable?
10. Is it documented?

If the answer to any important question is no, do not consider the task complete.

---

# END OF AI DEVELOPER GUIDE

This document is mandatory for all AI Coding Agents working on the project.