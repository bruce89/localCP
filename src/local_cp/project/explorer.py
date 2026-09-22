from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

from local_cp.project.models import ProjectOverview

MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024

IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)

LANGUAGE_BY_SUFFIX = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".go": "Go",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".json": "JSON",
    ".jsx": "JavaScript JSX",
    ".kt": "Kotlin",
    ".md": "Markdown",
    ".php": "PHP",
    ".ps1": "PowerShell",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Shell",
    ".sql": "SQL",
    ".toml": "TOML",
    ".ts": "TypeScript",
    ".tsx": "TypeScript JSX",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
}


def detect_file_type(path: Path) -> str:
    """Return a friendly, extension-based file type."""
    if path.name.lower() == "dockerfile":
        return "Dockerfile"
    return LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "Other")


def is_probably_binary(path: Path, sample_size: int = 8192) -> bool:
    """Use a null-byte check to avoid decoding typical binary files."""
    with path.open("rb") as handle:
        return b"\x00" in handle.read(sample_size)


def read_text_file(path: Path, max_bytes: int = MAX_TEXT_FILE_BYTES) -> str:
    """Read a reasonably-sized text file with explicit safety checks."""
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"File is too large to display ({size:,} bytes; limit {max_bytes:,}).")
    if is_probably_binary(path):
        raise ValueError("Binary files cannot be displayed.")
    return path.read_text(encoding="utf-8", errors="replace")


def scan_project(root: Path) -> ProjectOverview:
    """Collect deterministic project statistics without following directory links."""
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")

    result = ProjectOverview(root=str(root))
    languages: Counter[str] = Counter()

    def on_error(_error: OSError) -> None:
        result.skipped_count += 1

    for current, directory_names, file_names in os.walk(
        root, topdown=True, onerror=on_error, followlinks=False
    ):
        current_path = Path(current)
        kept_directories: list[str] = []
        for name in directory_names:
            candidate = current_path / name
            if name in IGNORED_DIRECTORIES or candidate.is_symlink():
                result.skipped_count += 1
            else:
                kept_directories.append(name)
        directory_names[:] = sorted(kept_directories, key=str.casefold)
        result.directory_count += len(directory_names)

        for name in sorted(file_names, key=str.casefold):
            path = current_path / name
            if path.is_symlink():
                result.skipped_count += 1
                continue
            try:
                result.total_bytes += path.stat().st_size
            except OSError:
                result.skipped_count += 1
                continue
            result.file_count += 1
            languages[detect_file_type(path)] += 1

    result.language_counts = dict(sorted(languages.items(), key=lambda item: (-item[1], item[0])))
    return result
