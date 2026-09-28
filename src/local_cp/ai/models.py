from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceFile:
    relative_path: str
    source: str


@dataclass(frozen=True, slots=True)
class CodeContext:
    files: tuple[SourceFile, ...]
    estimated_input_tokens: int


@dataclass(frozen=True, slots=True)
class AIResponse:
    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
