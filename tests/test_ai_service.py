"""Unit tests for the AI service layer."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from ai.models import PromptRequest, PromptResponse
from ai.service import AIService


class AIServiceTests(unittest.TestCase):
    """Verify AI service behaviour."""

    def setUp(self) -> None:
        """Create the service under test with a mocked client."""
        self.mock_client = MagicMock()
        self.service = AIService(client=self.mock_client)

    def test_generate_delegates_to_client(self) -> None:
        """Generate should delegate to GeminiClient."""

        expected = PromptResponse(
            content="Generated response",
            model="gemini-2.5-flash",
            finish_reason="STOP",
        )

        self.mock_client.generate.return_value = expected

        request = PromptRequest(
            prompt_name="resume",
            variables={
                "candidate": "Candidate",
                "job_description": "Developer",
            },
        )

        response = self.service.generate(request)

        self.assertEqual(expected, response)
        self.mock_client.generate.assert_called_once_with(request)

    def test_generate_resume_creates_request(self) -> None:
        """Generate resume should build the correct prompt."""

        self.service.generate = MagicMock(
            return_value=PromptResponse(
                content="Resume",
                model="gemini-2.5-flash",
                finish_reason="STOP",
            )
        )

        self.service.generate_resume(
            candidate="Resume",
            job_description="Job",
        )

        request = self.service.generate.call_args.args[0]

        self.assertEqual("resume", request.prompt_name)
        self.assertEqual("Resume", request.variables["candidate"])
        self.assertEqual("Job", request.variables["job_description"])

    def test_generate_cover_letter_creates_request(self) -> None:
        """Generate cover letter should build the correct prompt."""

        self.service.generate = MagicMock(
            return_value=PromptResponse(
                content="Letter",
                model="gemini-2.5-flash",
                finish_reason="STOP",
            )
        )

        self.service.generate_cover_letter(
            candidate="Resume",
            job_description="Job",
        )

        request = self.service.generate.call_args.args[0]

        self.assertEqual("cover_letter", request.prompt_name)

    def test_calculate_match_score_creates_request(self) -> None:
        """Match score should build the correct prompt."""

        self.service.generate = MagicMock(
            return_value=PromptResponse(
                content="95",
                model="gemini-2.5-flash",
                finish_reason="STOP",
            )
        )

        self.service.calculate_match_score(
            candidate="Resume",
            job_description="Job",
        )

        request = self.service.generate.call_args.args[0]

        self.assertEqual("match_score", request.prompt_name)

    def test_generate_interview_questions_creates_request(self) -> None:
        """Interview questions should build the correct prompt."""

        self.service.generate = MagicMock(
            return_value=PromptResponse(
                content="Questions",
                model="gemini-2.5-flash",
                finish_reason="STOP",
            )
        )

        self.service.generate_interview_questions(
            job_description="Backend Developer",
        )

        request = self.service.generate.call_args.args[0]

        self.assertEqual("interview", request.prompt_name)
        self.assertEqual(
            "Backend Developer",
            request.variables["job_description"],
        )


if __name__ == "__main__":
    unittest.main()