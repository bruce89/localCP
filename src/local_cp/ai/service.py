from __future__ import annotations

from collections.abc import Callable

from local_cp.ai.models import AIResponse, CodeContext
from local_cp.ai.openai_compatible import OpenAICompatibleProvider
from local_cp.ai.provider import AIProvider
from local_cp.config.credentials import gemini_api_key


class AssistantService:
    """Builds a configured provider without exposing it to Qt widgets."""

    def __init__(
        self,
        provider_factory: Callable[[str, str, str], AIProvider] = OpenAICompatibleProvider,
        key_resolver: Callable[[], str | None] = gemini_api_key,
    ) -> None:
        self._provider_factory = provider_factory
        self._key_resolver = key_resolver

    def ask(self, question: str, context: CodeContext, *, base_url: str, model: str) -> AIResponse:
        key = self._key_resolver()
        if not key:
            raise ValueError("GEMINI_API_KEY is not set in the Windows user environment.")
        provider = self._provider_factory(base_url, model, key)
        return provider.ask(question, context)
