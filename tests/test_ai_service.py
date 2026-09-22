from local_cp.ai.models import AIResponse, CodeContext
from local_cp.ai.service import AssistantService


def test_service_accepts_another_provider_without_gui_changes() -> None:
    captured = {}

    class ReplacementProvider:
        def ask(self, question: str, context: CodeContext) -> AIResponse:
            captured["question"] = question
            captured["path"] = context.relative_path
            return AIResponse("Replacement answer", "replacement")

    def factory(base_url: str, model: str, key: str) -> ReplacementProvider:
        captured["config"] = (base_url, model, key)
        return ReplacementProvider()

    service = AssistantService(provider_factory=factory, key_resolver=lambda: "test-key")
    result = service.ask(
        "Explain", CodeContext("one.py", "pass", 100), base_url="https://example.test", model="m"
    )

    assert captured["config"] == ("https://example.test", "m", "test-key")
    assert captured["question"] == "Explain"
    assert captured["path"] == "one.py"
    assert result.text == "Replacement answer"
