from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CodeContext:
    relative_path: str
    source: str
    estimated_input_tokens: int


@dataclass(frozen=True, slots=True)
class AIResponse:
    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
