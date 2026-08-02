"""Unit tests for CareerPilot SQLAlchemy domain models."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from database.base import Base
from database.connection import DatabaseConnection
from database.session import SessionManager
from domain.models import Application, Company, Interview, Job, Report, Resume


class DomainModelTests(unittest.TestCase):
    """Verify the domain schema, relationships, CRUD operations, and constraints."""

    def setUp(self) -> None:
        """Create all domain tables in an isolated SQLite database."""
        self._temporary_directory = TemporaryDirectory()
        database_path = Path(self._temporary_directory.name) / "storage" / "models.db"
        self.connection = DatabaseConnection(database_path)
        self.session_manager = SessionManager(self.connection.engine)
        Base.metadata.create_all(self.connection.engine)

    def tearDown(self) -> None:
        """Drop the isolated schema and dispose its database engine."""
        Base.metadata.drop_all(self.connection.engine)
        self.connection.dispose()
        self._temporary_directory.cleanup()

    def test_creates_all_requested_tables(self) -> None:
        """Create every requested domain table from the shared declarative base."""
        table_names = set(inspect(self.connection.engine).get_table_names())

        self.assertEqual(
            {
                "applications",
                "companies",
                "interviews",
                "jobs",
                "reports",
                "resumes",
            },
            table_names,
        )

    def test_persists_the_requested_relationship_graph(self) -> None:
        """Persist and retrieve company, job, resume, application, and interview links."""
        company, job, resume, application, interview = self._build_relationship_graph()

        with self.session_manager.session_scope() as session:
            session.add_all([company, job, resume, application, interview])

        with self.session_manager.session_scope() as session:
            persisted_job = session.get(Job, job.id)
            persisted_application = session.get(Application, application.id)

            self.assertEqual("CareerPilot", persisted_job.company.name)
            self.assertEqual(1, len(persisted_job.applications))
            self.assertEqual("resume-v1.pdf", persisted_application.resume.file_path)
            self.assertEqual(1, len(persisted_application.interviews))
            self.assertEqual(
                "Technical",
                persisted_application.interviews[0].round,
            )

    def test_supports_crud_operations_and_audit_timestamps(self) -> None:
        """Insert, update, retrieve, and delete a company with audit fields populated."""
        company = Company(name="CareerPilot", country="India")

        with self.session_manager.session_scope() as session:
            session.add(company)

        self.assertIsNotNone(company.created_at)
        self.assertIsNotNone(company.updated_at)

        with self.session_manager.session_scope() as session:
            persisted_company = session.get(Company, company.id)
            persisted_company.industry = "Technology"

        with self.session_manager.session_scope() as session:
            persisted_company = session.get(Company, company.id)
            self.assertEqual("Technology", persisted_company.industry)
            session.delete(persisted_company)

        with self.session_manager.session_scope() as session:
            self.assertIsNone(session.get(Company, company.id))

    def test_exposes_foreign_keys_for_required_relationships(self) -> None:
        """Declare foreign keys from jobs, applications, and interviews to their parents."""
        inspector = inspect(self.connection.engine)

        job_foreign_keys = inspector.get_foreign_keys("jobs")
        application_foreign_keys = inspector.get_foreign_keys("applications")
        interview_foreign_keys = inspector.get_foreign_keys("interviews")

        self.assertEqual("companies", job_foreign_keys[0]["referred_table"])
        self.assertEqual(
            {"jobs", "resumes"},
            {item["referred_table"] for item in application_foreign_keys},
        )
        self.assertEqual(
            "applications",
            interview_foreign_keys[0]["referred_table"],
        )

    def test_enforces_unique_company_job_resume_and_report_constraints(self) -> None:
        """Reject duplicates that would corrupt normalized data."""
        company, job, resume, application, _ = self._build_relationship_graph()

        with self.session_manager.session_scope() as session:
            session.add_all([company, job, resume, application])

        self._assert_integrity_error(Company(name="CareerPilot"))

        self._assert_integrity_error(
            Job(
                company_id=company.id,
                title="Another Role",
                description="Another description",
                platform="linkedin",
                job_url=job.job_url,
                status="discovered",
            )
        )

        self._assert_integrity_error(
            Resume(version=2, file_path=resume.file_path)
        )

        report = Report(report_date=date.today())

        with self.session_manager.session_scope() as session:
            session.add(report)

        self._assert_integrity_error(
            Report(report_date=report.report_date)
        )

    def test_allows_multiple_applications_for_the_same_job(self) -> None:
        """Allow multiple application records for the same job."""

        company = Company(name="Microsoft")

        job = Job(
            company=company,
            title="Software Engineer",
            description="Backend role",
            platform="linkedin",
            job_url="https://example.com/job1",
            status="open",
        )

        resume1 = Resume(
            version=1,
            file_path="resume1.pdf",
        )

        resume2 = Resume(
            version=2,
            file_path="resume2.pdf",
        )

        application1 = Application(
            job=job,
            resume=resume1,
            platform="linkedin",
            status="applied",
        )

        application2 = Application(
            job=job,
            resume=resume2,
            platform="linkedin",
            status="applied",
        )

        with self.session_manager.session_scope() as session:
            session.add_all(
                [
                    company,
                    job,
                    resume1,
                    resume2,
                    application1,
                    application2,
                ]
            )

        with self.session_manager.session_scope() as session:
            persisted_job = session.get(Job, job.id)
            self.assertEqual(2, len(persisted_job.applications))

    def test_persists_structured_resume_interview_and_report_fields(self) -> None:
        """Store JSON-backed fields needed by tailoring, interview, and reporting workflows."""
        resume = Resume(
            version=1,
            file_path="resume.pdf",
            skills=["C#", ".NET"],
        )

        report = Report(
            report_date=date.today(),
            india_jobs_found=20,
            international_jobs_found=5,
            total_jobs_applied=10,
            platform_summary={
                "linkedin": 6,
                "naukri": 4,
            },
        )

        with self.session_manager.session_scope() as session:
            session.add_all([resume, report])

        with self.session_manager.session_scope() as session:
            self.assertEqual(
                ["C#", ".NET"],
                session.get(Resume, resume.id).skills,
            )

            self.assertEqual(
                {
                    "linkedin": 6,
                    "naukri": 4,
                },
                session.get(
                    Report,
                    report.id,
                ).platform_summary,
            )

    def _assert_integrity_error(self, entity: object) -> None:
        """Assert that persisting an entity violates one of the declared constraints."""
        with self.assertRaises(IntegrityError):
            with self.session_manager.session_scope() as session:
                session.add(entity)
                session.flush()

    @staticmethod
    def _build_relationship_graph() -> tuple[
        Company,
        Job,
        Resume,
        Application,
        Interview,
    ]:
        """Create a complete domain graph for relationship tests."""

        company = Company(
            name="CareerPilot",
            country="India",
        )

        job = Job(
            company=company,
            title="Software Engineer",
            description="Build reliable software.",
            location="Bengaluru",
            country="India",
            employment_type="Full-time",
            work_mode="Hybrid",
            salary="20 LPA",
            currency="INR",
            visa_sponsorship=False,
            platform="linkedin",
            job_url="https://example.com/jobs/1",
            match_score=85.0,
            status="qualified",
            posted_date=date.today(),
        )

        resume = Resume(
            version=1,
            file_path="resume-v1.pdf",
            summary="Verified .NET developer profile.",
            skills=["C#", ".NET"],
        )

        application = Application(
            job=job,
            resume=resume,
            cover_letter_path="cover-letter.pdf",
            platform="linkedin",
            status="applied",
            applied_at=datetime.now(timezone.utc),
            notes="Submitted through LinkedIn.",
        )

        interview = Interview(
            application=application,
            round="Technical",
            scheduled_at=datetime.now(timezone.utc),
            interviewer="Hiring Manager",
            meeting_link="https://example.com/meeting",
            questions=["Explain dependency injection."],
            notes="Prepare ASP.NET Core examples.",
            result="pending",
        )

        return company, job, resume, application, interview


if __name__ == "__main__":
    unittest.main()