"""Prompt loading and rendering utilities."""

from __future__ import annotations

from core.config import ConfigurationManager

from ai.exceptions import PromptNotFoundError
from ai.models import PromptRequest


class PromptManager:
    """Load and render prompt templates."""

    def __init__(self) -> None:
        self._prompts = ConfigurationManager().get_prompts()

    def render(self, request: PromptRequest) -> str:
        """Render a prompt using the supplied variables."""

        template = self._prompts.get(request.prompt_name)

        if template is None:
            raise PromptNotFoundError(
                f"Prompt '{request.prompt_name}' not found."
            )

        if not isinstance(template, str):
            raise PromptNotFoundError(
                f"Prompt '{request.prompt_name}' is invalid."
            )

        return template.format(**request.variables)