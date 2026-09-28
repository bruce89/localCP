from local_cp.ai.models import CodeContext, SourceFile
from local_cp.ai.secret_scan import scan_request


def test_flags_source_and_question_without_returning_values() -> None:
    fake_key = "sk-" + "x" * 25
    source = 'API_KEY = "sample-secret-value"\nprint("safe")\n-----BEGIN PRIVATE KEY-----'
    context = CodeContext((SourceFile("sample.py", source),), 100)

    findings = scan_request(f"Check {fake_key}", context)

    assert [(item.location, item.line, item.reason) for item in findings] == [
        ("question", 1, "credential-shaped value"),
        ("sample.py", 1, "hardcoded credential"),
        ("sample.py", 3, "private key header"),
    ]
    assert fake_key not in repr(findings)
    assert "sample-secret-value" not in repr(findings)


def test_environment_lookup_is_not_flagged() -> None:
    context = CodeContext(
        (SourceFile("safe.py", 'API_KEY = os.environ.get("GEMINI_API_KEY")\n'),), 100
    )

    assert scan_request("Explain this code", context) == ()
