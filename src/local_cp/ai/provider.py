from __future__ import annotations

from typing import Protocol

from local_cp.ai.models import AIResponse, CodeContext


class AIProvider(Protocol):
    """Provider contract consumed by the application layer."""

    def ask(self, question: str, context: CodeContext) -> AIResponse: ...
