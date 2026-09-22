from pathlib import Path

import pytest

from local_cp.ai.context import prepare_context


def test_prepares_exactly_selected_python_file(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    source = project / "sample.py"
    source.write_text("def answer():\n    return 42\n", encoding="utf-8")
    (project / "other.py").write_text("SECRET = 'not selected'\n", encoding="utf-8")

    context = prepare_context(project, source, "What does this do?")

    assert context.relative_path == "sample.py"
    assert "return 42" in context.source
    assert "SECRET" not in context.source
    assert context.estimated_input_tokens <= 4_000


def test_rejects_file_outside_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("pass\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside"):
        prepare_context(project, outside, "Explain")


def test_rejects_large_context(tmp_path: Path) -> None:
    source = tmp_path / "large.py"
    source.write_text("x" * 12_001, encoding="utf-8")

    with pytest.raises(ValueError, match="too large"):
        prepare_context(tmp_path, source, "Explain")
