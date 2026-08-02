# CareerPilot AI - Software Architecture

Version: 1.0
Status: Architecture (Frozen)
Author: Kunal Mishra
Architecture Owner: ChatGPT

---

# 1. Architecture Overview

CareerPilot AI follows a layered, modular architecture based on Clean Architecture principles.

The objective is to ensure:

- High maintainability
- Scalability
- Testability
- Separation of concerns
- Easy addition of new job platforms
- Easy addition of new AI agents

---

# 2. High-Level Architecture

                    User
                      │
                      ▼
               Scheduler / CLI
                      │
                      ▼
                AI Orchestrator
                      │
 ┌────────────────────┼────────────────────┐
 │                    │                    │
 ▼                    ▼                    ▼
Search Agent     Resume Agent      Apply Agent
 │                    │                    │
 ▼                    ▼                    ▼
Platform        OpenAI Service      Playwright
Adapters             │
 │                    ▼
 ▼              Prompt Service
Job Results
 │
 ▼
Database
 │
 ▼
Reporting Engine
 │
 ▼
Notifications

---

# 3. Project Structure

CareerPilotAI/

core/
Application startup, configuration, logging, exceptions

config/
YAML configuration files

agents/
AI agents

adapters/
Platform-specific integrations

services/
Business logic

database/
Database connection and repositories

models/
Application models

scheduler/
Daily automation

reports/
Excel report generation

prompts/
Prompt templates

notifications/
WhatsApp, Email

interview/
Interview preparation

storage/
Database, screenshots, backups

data/
Temporary runtime data

scripts/
Utility scripts

tests/
Unit and integration tests

docs/
Project documentation

logs/
Application logs

---

# 4. Layer Responsibilities

Core Layer

Responsible for:

- Configuration
- Logger
- Constants
- Startup
- Security
- Shared utilities

No business logic should exist here.

---

Service Layer

Responsible for:

Business rules.

Examples:

Job scoring

Resume tailoring

Application tracking

Cover letter generation

Services never communicate directly with browsers.

---

Agent Layer

Responsible for decision making.

Agents coordinate services.

Each agent has a single responsibility.

Agents never know implementation details of external platforms.

---

Adapter Layer

Responsible for communicating with external systems.

Examples:

LinkedIn

Naukri

Indeed

Wellfound

Company Career Pages

Every platform implementation stays isolated.

Adding a new platform should only require a new adapter.

---

Database Layer

Responsible only for:

Reading

Writing

Updating

Deleting

No business logic.

---

Reporting Layer

Responsible for:

Excel

CSV

Future Dashboard

Reports are generated from database data only.

---

# 5. AI Agents

Search Agent

Searches jobs.

Resume Agent

Tailors resumes.

Cover Letter Agent

Generates cover letters.

Apply Agent

Automates applications.

Tracker Agent

Tracks status.

Notification Agent

Sends summaries.

Interview Agent

Creates interview preparation.

---

# 6. Platform Adapter Pattern

Search Agent

↓

LinkedIn Adapter

↓

Naukri Adapter

↓

Indeed Adapter

↓

Instahyre Adapter

↓

Hirist Adapter

↓

Company Adapter

Each adapter implements the same interface.

This allows adding future platforms without changing Search Agent.

---

# 7. Data Flow

Scheduler

↓

Search Agent

↓

Platform Adapters

↓

Merge Results

↓

Duplicate Removal

↓

Job Scoring

↓

Resume Tailoring

↓

Cover Letter

↓

Apply

↓

Database

↓

Reporting

↓

Notification

---

# 8. Database Design

Tables

Jobs

Applications

Companies

Resumes

Reports

Interviews

Notifications

Future tables may be added without affecting existing schema.

---

# 9. Configuration Flow

Application Starts

↓

Load .env

↓

Load YAML Configuration

↓

Validate Configuration

↓

Initialize Logger

↓

Initialize Database

↓

Initialize AI

↓

Create Agents

↓

Ready

---

# 10. Error Handling Strategy

Every module must:

Catch expected exceptions.

Log every error.

Raise meaningful exceptions.

Never silently ignore failures.

---

# 11. Logging Strategy

Every important action should be logged.

Examples:

Application Started

Configuration Loaded

Resume Generated

Job Applied

Interview Created

Database Updated

Notification Sent

---

# 12. Security Principles

Never hardcode credentials.

Use .env.

Never store passwords in code.

Never log sensitive data.

Support future secret managers.

---

# 13. Scalability

The architecture should support:

Additional job platforms

Multiple users

Multiple resumes

Cloud deployment

Background workers

REST API

Web dashboard

Future mobile application

without major refactoring.

---

# 14. Future Enhancements

REST API

Web Dashboard

Recruiter Email Parsing

AI Career Coach

Salary Analytics

Offer Comparison

Interview Calendar

Recruiter CRM

Multiple Users

Cloud Database

Docker Deployment

Kubernetes Deployment

---

END OF ARCHITECTURE DOCUMENT

Every module implemented in CareerPilot AI must follow this architecture.