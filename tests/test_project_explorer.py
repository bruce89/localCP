from pathlib import Path

import pytest

from local_cp.project.explorer import detect_file_type, read_text_file, scan_project


def test_scan_project_counts_files_directories_and_languages(tmp_path: Path) -> None:
    (tmp_path / "package").mkdir()
    (tmp_path / "package" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Example\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "ignored.py").write_text("pass\n", encoding="utf-8")

    result = scan_project(tmp_path)

    assert result.file_count == 2
    assert result.directory_count == 1
    assert result.language_counts == {"Markdown": 1, "Python": 1}
    assert result.skipped_count == 1


def test_detect_file_type_is_case_insensitive() -> None:
    assert detect_file_type(Path("example.PY")) == "Python"
    assert detect_file_type(Path("Dockerfile")) == "Dockerfile"
    assert detect_file_type(Path("LICENSE")) == "Other"


def test_read_text_file_rejects_binary_content(tmp_path: Path) -> None:
    path = tmp_path / "image.bin"
    path.write_bytes(b"abc\x00def")

    with pytest.raises(ValueError, match="Binary"):
        read_text_file(path)


def test_read_text_file_rejects_oversized_file(tmp_path: Path) -> None:
    path = tmp_path / "large.txt"
    path.write_text("abcdef", encoding="utf-8")

    with pytest.raises(ValueError, match="too large"):
        read_text_file(path, max_bytes=3)
