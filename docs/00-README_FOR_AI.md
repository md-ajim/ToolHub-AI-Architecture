# 📄 docs/00-README_FOR_AI.md

# AI Entry Point

Version: 1.0

Status: Required

---

# Purpose

This document is the mandatory entry point for every AI Coding Agent working on this project.

If you are an AI Coding Agent (Gemini CLI, Claude Code, Codex CLI, Cursor, Windsurf, Continue, Aider, or any other AI assistant), you MUST read this document first before reading or modifying any code.

Never skip this document.

---

# Mission

You are contributing to a long-term enterprise software platform.

This is NOT a demo.

This is NOT a tutorial project.

This is NOT a prototype.

Every implementation must be production-ready.

Your primary objective is:

- Maintain architecture integrity
- Maintain code quality
- Maintain scalability
- Maintain security
- Maintain documentation

Never optimise only for speed.

Always optimise for long-term maintainability.

---

# Required Reading Order

Before starting ANY task, read the following documents in order.

1.

AI_DEVELOPER_GUIDE.md

2.

01-product-vision.md

3.

03-system-architecture.md

4.

Read the architecture document related to the requested feature.

Examples

Authentication

↓

09-authentication-and-authorization.md

Payment

↓

11-payment-subscription-architecture.md

AI

↓

12-ai-processing-architecture.md

Storage

↓

13-storage-file-management-architecture.md

API

↓

08-api-design.md

Frontend

↓

07-frontend-architecture.md

Backend

↓

06-backend-folder-architecture.md

Database

↓

04-database-design.md

SEO

↓

10-seo-architecture.md

Deployment

↓

14-deployment-devops-architecture.md

---

# Before Writing Code

You MUST understand:

- Business Goal
- Product Vision
- Architecture
- Existing Code
- Dependencies
- Database Impact
- API Impact
- UI Impact

Never write code before understanding these.

---

# Implementation Workflow

For every task:

Step 1

Read documentation.

↓

Step 2

Understand architecture.

↓

Step 3

Understand dependencies.

↓

Step 4

Create implementation plan.

↓

Step 5

Wait for approval (when required).

↓

Step 6

Implement.

↓

Step 7

Write tests.

↓

Step 8

Self review.

↓

Step 9

Update documentation.

↓

Step 10

Verify architecture.

---

# Project Principles

Always prefer

- Simplicity
- Readability
- Reusability
- Scalability
- Maintainability

Never optimise only for fewer lines of code.

---

# Architecture Rules

Architecture has higher priority than implementation speed.

Never modify architecture without explicit approval.

Never introduce a new pattern when an existing one already solves the problem.

Reuse existing components whenever possible.

---

# Required Output Format

Before implementing any feature, provide:

## Understanding

Summarise the task.

## Impact

Explain what parts of the project will change.

## Plan

Provide a step-by-step implementation plan.

Only then begin implementation.

---

# If Requirements Are Unclear

Never guess.

Instead:

- Explain what is unclear.
- Ask for clarification.
- Wait for confirmation.

---

# Never Do These

Never

- Rename APIs
- Rename folders
- Rename database tables
- Rename models
- Rename routes
- Change architecture
- Break compatibility
- Duplicate logic
- Ignore documentation
- Ignore validation
- Ignore security
- Ignore performance
- Ignore SEO
- Ignore accessibility

---

# Always Do These

Always

- Read documentation
- Reuse components
- Follow coding standards
- Write clean code
- Validate inputs
- Handle errors
- Update documentation
- Consider performance
- Consider security
- Consider accessibility
- Consider SEO
- Consider testing

---

# Required Checklist Before Completion

The task is NOT complete until all items are true.

- Code builds successfully
- Tests pass
- Lint passes
- Type checking passes
- No duplicate code
- Documentation updated
- API documentation updated (if applicable)
- Database migration reviewed (if applicable)
- No architecture violations
- Security reviewed
- Performance reviewed
- Accessibility reviewed
- SEO reviewed (public pages)
- Logging considered
- Monitoring hooks added where appropriate

---

# Feature Completion Checklist

Every production feature should include, where applicable:

- UI
- API
- Validation
- Error Handling
- Permissions
- Logging
- Analytics
- Documentation
- Tests
- Loading States
- Empty States
- Mobile Support
- Accessibility
- SEO
- Performance

A feature is not complete if only the UI or only the backend exists.

---

# Project Documentation Index

Always use these documents as the source of truth.

00-README_FOR_AI.md

AI_DEVELOPER_GUIDE.md

01-product-vision.md

02-feature-roadmap.md

03-system-architecture.md

04-database-design.md

05-domain-model.md

06-backend-folder-architecture.md

07-frontend-architecture.md

08-api-design.md

09-authentication-and-authorization.md

10-seo-architecture.md

11-payment-subscription-architecture.md

12-ai-processing-architecture.md

13-storage-file-management-architecture.md

14-deployment-devops-architecture.md

17-page-and-route-architecture.md

18-ui-ux-design-system.md

19-page-design-specification.md

20-component-design-system.md

21-responsive-design-guidelines.md

32-ai-workspace-architecture.md

Future documents should be added here.

---

# Definition of Success

Success is NOT writing code.

Success is delivering a production-ready feature that:

- follows the architecture
- follows project standards
- is secure
- is scalable
- is maintainable
- is documented
- is tested
- is ready for long-term growth

---

# Final Instruction

Every decision should support the long-term vision of building one of the world's best utility platforms.

If a shortcut conflicts with long-term quality, choose long-term quality.

This document is mandatory.

Read it before every task.

Never skip it.
