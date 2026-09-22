from __future__ import annotations

from pathlib import Path

from local_cp.ai.models import CodeContext
from local_cp.project.explorer import read_text_file

MAX_CONTEXT_BYTES = 12_000
MAX_ESTIMATED_INPUT_TOKENS = 4_000
MAX_QUESTION_CHARS = 1_000


def estimate_tokens(text: str) -> int:
    """Conservative approximation, not a provider tokenizer."""
    return (len(text.encode("utf-8")) + 2) // 3


def prepare_context(root: Path, selected: Path, question: str) -> CodeContext:
    """Prepare exactly one selected Python file for an explicit send action."""
    if not question.strip():
        raise ValueError("Enter a question before preparing context.")
    if len(question) > MAX_QUESTION_CHARS:
        raise ValueError(f"Question exceeds {MAX_QUESTION_CHARS:,} characters.")
    if selected.is_symlink():
        raise ValueError("Symbolic-link files are not available as AI context.")
    resolved_root = root.resolve(strict=True)
    resolved_file = selected.resolve(strict=True)
    if not resolved_file.is_relative_to(resolved_root):
        raise ValueError("The selected file is outside the open project.")
    if resolved_file.suffix.lower() != ".py":
        raise ValueError("This prototype accepts one Python file at a time.")
    source = read_text_file(resolved_file, max_bytes=MAX_CONTEXT_BYTES)
    relative_path = resolved_file.relative_to(resolved_root).as_posix()
    estimate = estimate_tokens(question + source + relative_path) + 300
    if estimate > MAX_ESTIMATED_INPUT_TOKENS:
        raise ValueError("Estimated request exceeds the input budget. Choose a smaller file.")
    return CodeContext(relative_path, source, estimate)
