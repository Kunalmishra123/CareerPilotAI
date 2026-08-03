"""Shared request and response models for the AI service."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PromptRequest:
    """Represent one AI generation request."""

    prompt_name: str
    variables: dict[str, str] = field(default_factory=dict)

    temperature: float = 0.2
    max_output_tokens: int = 2048


@dataclass(frozen=True, slots=True)
class PromptResponse:
    """Represent one AI generation response."""

    content: str
    model: str
    finish_reason: str