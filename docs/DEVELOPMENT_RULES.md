# CareerPilot AI - Development Rules

Version: 1.0
Status: Development Rules (Frozen)

---

# 1. Objective

This document defines the engineering standards for CareerPilot AI.

Every developer, AI assistant, and future contributor must follow these rules.

These rules take precedence over implementation preferences.

---

# 2. General Principles

Always write production-quality code.

Prioritize readability over cleverness.

Keep code simple.

Avoid unnecessary complexity.

Follow Clean Architecture.

Follow SOLID principles.

Follow DRY (Don't Repeat Yourself).

Follow KISS (Keep It Simple).

---

# 3. Coding Standards

Python Version

Python 3.10+

Use

- Type Hints
- Dataclasses where appropriate
- Enum instead of magic strings
- Pathlib instead of string paths
- Logging instead of print()

Never use

Global variables

Hardcoded values

Hardcoded credentials

Business logic inside UI or adapters

---

# 4. Folder Responsibilities

core/

Application infrastructure only.

Never place business logic here.

---

agents/

Decision making.

Agents coordinate workflows.

Agents never communicate directly with databases.

---

services/

Business logic.

Resume generation.

Job scoring.

Tracking.

Application processing.

---

adapters/

Platform-specific code only.

Never place business logic inside adapters.

---

database/

Persistence only.

No business logic.

---

models/

Application entities.

No database logic.

---

config/

YAML configuration only.

---

reports/

Excel and CSV generation.

---

notifications/

Notification integrations.

---

tests/

Unit tests

Integration tests

---

# 5. Naming Convention

Classes

PascalCase

Example

ResumeAgent

JobService

ApplicationTracker

---

Functions

snake_case

Example

generate_resume()

search_jobs()

load_configuration()

---

Variables

snake_case

Example

job_score

application_count

user_profile

---

Constants

UPPER_CASE

Example

DEFAULT_TIMEOUT

MAX_APPLICATIONS

---

Files

snake_case.py

Example

resume_service.py

job_repository.py

---

# 6. Logging Rules

Every important action must be logged.

Examples

Application Started

Configuration Loaded

Database Connected

Resume Generated

Application Submitted

Interview Created

Report Generated

Never log

Passwords

API Keys

Sensitive personal information

---

# 7. Exception Handling

Never silently ignore exceptions.

Never use empty except blocks.

Always log exceptions.

Raise meaningful exceptions.

Provide user-friendly messages.

---

# 8. Configuration Rules

Never hardcode configuration.

Always read from

settings.yaml

platforms.yaml

user_profile.yaml

prompts.yaml

Secrets must come from

.env

---

# 9. AI Rules

AI must never

Invent experience

Invent employment

Invent certifications

Invent skills

Generate fake information

AI may

Improve wording

Optimize formatting

Tailor existing experience

Highlight relevant skills

---

# 10. Database Rules

Use SQLAlchemy ORM.

Never write raw SQL unless required.

Use repository pattern.

Every table should have

Primary Key

Created Date

Updated Date

---

# 11. Browser Automation Rules

Use Playwright.

Never bypass CAPTCHA.

Pause automation when manual verification is required.

Take screenshots when failures occur.

Store screenshots in

storage/screenshots/

---

# 12. Git Workflow

Feature

↓

Run

↓

Review

↓

Test

↓

Commit

↓

Push

Never commit broken code.

Never commit secrets.

Never commit .env.

Never commit venv.

---

# 13. Testing Rules

Every feature should have

Positive test

Negative test

Edge case test

Every bug fix should include a test whenever practical.

---

# 14. Code Review Checklist

Before every commit verify

✓ Code runs

✓ Logging exists

✓ Exception handling exists

✓ Type hints added

✓ No duplicated code

✓ Correct architecture

✓ Configuration externalized

✓ No hardcoded credentials

✓ Naming conventions followed

✓ Clean code

---

# 15. Performance Guidelines

Avoid unnecessary API calls.

Reuse objects.

Cache where appropriate.

Use asynchronous programming only when beneficial.

Avoid premature optimization.

---

# 16. Security Guidelines

Never expose API keys.

Use .env.

Validate user input.

Sanitize file paths.

Handle sensitive information carefully.

---

# 17. Documentation Rules

Every public class should have a docstring.

Complex methods should explain why, not what.

Update documentation whenever architecture changes.

---

# 18. Definition of Done (DoD)

A task is complete only if:

✓ Requirements implemented

✓ Code reviewed

✓ Tests passed

✓ Logging added

✓ Exceptions handled

✓ Documentation updated

✓ Git commit created

✓ Code pushed to GitHub

---

# 19. AI Collaboration Workflow

ChatGPT

↓

Architecture

↓

Codex

↓

Implementation

↓

Developer

↓

Execution

↓

ChatGPT

↓

Review

↓

Git Commit

This workflow must be followed throughout the project.

---

END OF DEVELOPMENT RULES

Every implementation in CareerPilot AI must comply with this document.