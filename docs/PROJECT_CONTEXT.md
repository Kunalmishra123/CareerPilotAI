# CareerPilot AI

Version: 1.0
Status: Project Vision (Frozen)
Author: Kunal Mishra
Architecture Owner: ChatGPT

---

# 1. Project Overview

CareerPilot AI is an AI-powered career assistant that automates the complete job application lifecycle for software engineers.

The objective is to eliminate repetitive manual work involved in job searching and applying while maximizing interview opportunities.

CareerPilot AI should operate like a personal recruiter that works 24×7.

---

# 2. Primary Goal

Automatically perform the following tasks:

- Search jobs
- Analyze job descriptions
- Match jobs with user profile
- Tailor resume
- Generate cover letter (when required)
- Apply automatically wherever possible
- Track application status
- Generate daily reports
- Notify user about interviews
- Prepare interview questions

---

# 3. User Profile

Primary User:

Name:
Kunal Mishra

Profession:
Software Engineer

Experience:
4.2 Years

Primary Skills:

- C#
- .NET
- ASP.NET Core
- SQL Server
- REST API
- Entity Framework

Target Salary:

15–20 LPA

Primary Goal:

Switch to a better Software Engineering role.

---

# 4. Daily Objective

Target Applications:

25 jobs/day

Distribution:

India: 20

International: 5

Quality is always more important than quantity.

The AI should apply only to jobs that meet the configured match score.

---

# 5. Supported Platforms

India

- LinkedIn
- Naukri
- Indeed
- Instahyre
- Hirist

International

- LinkedIn
- Indeed
- Wellfound
- Company Career Pages

The architecture must allow adding new platforms without modifying existing platform implementations.

---

# 6. Functional Requirements

The system shall:

Search jobs from multiple platforms.

Remove duplicate jobs.

Score every job.

Tailor resume.

Generate cover letter.

Apply automatically.

Store every application.

Track application progress.

Generate reports.

Generate interview questions.

---

# 7. AI Agents

CareerPilot AI consists of multiple independent AI agents.

Search Agent

Responsible for discovering jobs.

Resume Agent

Responsible for tailoring resumes.

Cover Letter Agent

Responsible for generating cover letters.

Apply Agent

Responsible for browser automation.

Tracker Agent

Responsible for application tracking.

Notification Agent

Responsible for daily summaries.

Interview Agent

Responsible for interview preparation.

Future agents may be added without changing the overall architecture.

---

# 8. Project Principles

The project must follow:

- Clean Architecture
- SOLID Principles
- Modular Design
- Adapter Pattern
- Dependency Injection (where appropriate)
- Configuration Driven Development
- Production Quality Code

---

# 9. Coding Rules

Never hardcode values.

Never hardcode API keys.

Always use logging.

Always use type hints.

Always handle exceptions.

Always write reusable code.

Never duplicate business logic.

---

# 10. Resume Rules

The AI must NEVER:

Invent experience.

Add fake skills.

Modify employment history.

Change years of experience.

The AI may:

Reorder content.

Highlight relevant experience.

Optimize wording.

Tailor skills based on actual experience.

---

# 11. Browser Automation Rules

The assistant may automate application forms.

If CAPTCHA or mandatory human verification appears:

Pause automation.

Notify the user.

Wait for manual completion.

Resume afterwards.

---

# 12. Reporting

Generate daily reports.

Include:

Company

Role

Country

Platform

Resume Used

Status

Applied Date

Interview Status

Export:

Excel

CSV

Future:

Dashboard

---

# 13. Notifications

Future notification channels:

Email

WhatsApp

Desktop Notification

Telegram

---

# 14. Long-Term Vision

CareerPilot AI should evolve into a complete AI Career Operating System.

Future capabilities include:

Recruiter Email Monitoring

Salary Analytics

Interview Calendar

Application Analytics

Offer Comparison

Career Recommendation Engine

---

# 15. Success Criteria

CareerPilot AI will be considered successful when it can:

Automatically search jobs.

Tailor resumes.

Generate cover letters.

Apply automatically where supported.

Track every application.

Generate reports.

Prepare interview questions.

Operate daily with minimal manual effort.

---

END OF PROJECT CONTEXT

This document is the single source of truth for the project.

Every implementation must follow this document.