from pathlib import Path

import pytest

from local_cp.ai.context import prepare_context


def test_prepares_exactly_selected_python_file(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    source = project / "sample.py"
    source.write_text("def answer():\n    return 42\n", encoding="utf-8")
    (project / "other.py").write_text("SECRET = 'not selected'\n", encoding="utf-8")

    context = prepare_context(project, [source], "What does this do?")

    assert [file.relative_path for file in context.files] == ["sample.py"]
    assert "return 42" in context.files[0].source
    assert all("SECRET" not in file.source for file in context.files)
    assert context.estimated_input_tokens <= 4_000


def test_rejects_file_outside_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("pass\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside"):
        prepare_context(project, [outside], "Explain")


def test_rejects_large_context(tmp_path: Path) -> None:
    source = tmp_path / "large.py"
    source.write_text("x" * 12_001, encoding="utf-8")

    with pytest.raises(ValueError, match="too large"):
        prepare_context(tmp_path, [source], "Explain")


def test_multiple_files_have_stable_order_and_one_budget(tmp_path: Path) -> None:
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("A = 1\n", encoding="utf-8")
    second.write_text("B = 2\n", encoding="utf-8")

    context = prepare_context(tmp_path, [second, first], "Compare them")

    assert [file.relative_path for file in context.files] == ["second.py", "first.py"]
    assert context.estimated_input_tokens <= 4_000


def test_rejects_duplicate_and_too_many_files(tmp_path: Path) -> None:
    files = [tmp_path / f"{index}.py" for index in range(4)]
    for path in files:
        path.write_text("pass\n", encoding="utf-8")

    with pytest.raises(ValueError, match="same file"):
        prepare_context(tmp_path, [files[0], files[0]], "Explain")
    with pytest.raises(ValueError, match="at most 3"):
        prepare_context(tmp_path, files, "Explain")


def test_rejects_combined_source_over_budget(tmp_path: Path) -> None:
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("x" * 7_000, encoding="utf-8")
    second.write_text("y" * 6_000, encoding="utf-8")

    with pytest.raises(ValueError, match="too large|Combined source"):
        prepare_context(tmp_path, [first, second], "Explain")
