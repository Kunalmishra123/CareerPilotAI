"""Google Gemini AI client implementation."""

from __future__ import annotations

from google import genai
from google.genai import errors, types

from ai.exceptions import (
    AIConfigurationError,
    AIRequestError,
)
from ai.models import PromptRequest, PromptResponse
from ai.prompts import PromptManager
from core.config import ConfigurationManager


class GeminiClient:
    """Client responsible for communicating with Google's Gemini API."""

    def __init__(self) -> None:
        """Initialize the Gemini client from application configuration."""

        configuration = ConfigurationManager()
        settings = configuration.get_settings()

        ai_settings = settings.get("ai", {})
        gemini_settings = ai_settings.get("gemini", {})

        self._api_key = gemini_settings.get("api_key")
        self._model = gemini_settings.get("model", "gemini-2.5-flash")
        self._temperature = gemini_settings.get("temperature", 0.2)
        self._max_output_tokens = gemini_settings.get(
            "max_output_tokens",
            2048,
        )

        if not self._api_key:
            raise AIConfigurationError(
                "Gemini API key is missing. "
                "Configure ai.gemini.api_key in settings.yaml."
            )

        self._client = genai.Client(api_key=self._api_key)
        self._prompt_manager = PromptManager()

    def generate(self, request: PromptRequest) -> PromptResponse:
        """Generate content using the configured Gemini model."""

        prompt = self._prompt_manager.render(request)

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=request.temperature or self._temperature,
                    max_output_tokens=(
                        request.max_output_tokens or self._max_output_tokens
                    ),
                ),
            )

            return PromptResponse(
                content=response.text or "",
                model=self._model,
                finish_reason=(
                    response.candidates[0].finish_reason.name
                    if response.candidates
                    and response.candidates[0].finish_reason
                    else "UNKNOWN"
                ),
            )

        except errors.APIError as error:
            raise AIRequestError(
                f"Gemini API request failed: {str(error)}"
            ) from error

        except Exception as error:
            raise AIRequestError(
                f"Unexpected AI error: {error}"
            ) from error
  
    @property
    def model(self) -> str:
        """Return the configured Gemini model."""
        return self._model
