import io
import json
from urllib.error import HTTPError

import pytest

from local_cp.ai.models import CodeContext
from local_cp.ai.openai_compatible import OpenAICompatibleProvider, ProviderError


def test_openai_compatible_provider_sends_one_file(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["payload"] = json.loads(request.data)
        captured["timeout"] = timeout
        return io.BytesIO(
            json.dumps(
                {
                    "model": "test-model",
                    "choices": [{"message": {"content": "It returns 42."}}],
                    "usage": {"prompt_tokens": 55, "completion_tokens": 7},
                }
            ).encode()
        )

    monkeypatch.setattr("local_cp.ai.openai_compatible.urlopen", fake_urlopen)
    provider = OpenAICompatibleProvider("https://example.test/v1/", "test-model", "test-key")
    context = CodeContext("one.py", "def answer(): return 42", 100)

    result = provider.ask("What does it do?", context)

    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == "test-model"
    assert len(captured["payload"]["messages"]) == 2
    assert "one.py" in captured["payload"]["messages"][1]["content"]
    assert captured["payload"]["max_tokens"] == 384
    assert result.text == "It returns 42."
    assert result.input_tokens == 55


def test_provider_error_does_not_expose_response_body(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request, timeout):
        raise HTTPError(request.full_url, 429, "key=secret", {}, None)

    monkeypatch.setattr("local_cp.ai.openai_compatible.urlopen", fake_urlopen)
    provider = OpenAICompatibleProvider("https://example.test/v1/", "test-model", "test-key")

    with pytest.raises(ProviderError, match="rate limit") as caught:
        provider.ask("Question", CodeContext("one.py", "pass", 100))
    assert "secret" not in str(caught.value)


def test_provider_requires_https() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        OpenAICompatibleProvider("http://example.test/v1", "model", "key")
