"""Enumerations shared by CareerPilot AI domain models."""

from enum import Enum


class ApplicationStatus(str, Enum):
    """Lifecycle states for a job application."""

    PENDING_APPROVAL = "pending_approval"
    APPLIED = "applied"
    IN_PROGRESS = "in_progress"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"


class InterviewStatus(str, Enum):
    """Lifecycle states for a scheduled interview."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewType(str, Enum):
    """Categories of interview preparation and scheduling activities."""

    TECHNICAL = "technical"
    HR = "hr"
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    OTHER = "other"


class JobPlatform(str, Enum):
    """Job platforms currently recognized by the domain model."""

    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    INDEED = "indeed"
    INSTAHYRE = "instahyre"
    HIRIST = "hirist"
    WELLFOUND = "wellfound"
    COMPANY_CAREER_PAGE = "company_career_page"


class ReportType(str, Enum):
    """Supported report aggregation periods."""

    DAILY = "daily"
    WEEKLY = "weekly"


class ResumeType(str, Enum):
    """Categories of source and generated resume documents."""

    MASTER = "master"
    TAILORED = "tailored"
