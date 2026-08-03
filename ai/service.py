"""High-level AI service for interacting with the configured AI provider."""

from __future__ import annotations

from ai.client import GeminiClient
from ai.models import PromptRequest, PromptResponse


class AIService:
    """Provide high-level AI operations for CareerPilot."""

    def __init__(self, client: GeminiClient | None = None) -> None:
        """
        Initialize the AI service.

        Args:
            client: Optional AI client. Used for dependency injection
                during testing.
        """
        self._client = client if client is not None else GeminiClient()

    def generate(self, request: PromptRequest) -> PromptResponse:
        """Generate AI content using the configured provider."""
        return self._client.generate(request)

    def generate_resume(
        self,
        candidate: str,
        job_description: str,
    ) -> PromptResponse:
        """Generate a tailored resume."""

        request = PromptRequest(
            prompt_name="resume",
            variables={
                "candidate": candidate,
                "job_description": job_description,
            },
        )

        return self.generate(request)

    def generate_cover_letter(
        self,
        candidate: str,
        job_description: str,
    ) -> PromptResponse:
        """Generate a tailored cover letter."""

        request = PromptRequest(
            prompt_name="cover_letter",
            variables={
                "candidate": candidate,
                "job_description": job_description,
            },
        )

        return self.generate(request)

    def calculate_match_score(
        self,
        candidate: str,
        job_description: str,
    ) -> PromptResponse:
        """Calculate resume-job match score."""

        request = PromptRequest(
            prompt_name="match_score",
            variables={
                "candidate": candidate,
                "job_description": job_description,
            },
        )

        return self.generate(request)

    def generate_interview_questions(
        self,
        job_description: str,
    ) -> PromptResponse:
        """Generate interview questions."""

        request = PromptRequest(
            prompt_name="interview",
            variables={
                "job_description": job_description,
            },
        )

        return self.generate(request)

    @property
    def model(self) -> str:
        """Return the configured AI model."""
        return self._client.model