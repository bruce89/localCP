from pathlib import Path

import pytest

from local_cp.analysis.python_analyzer import analyze_python_file, analyze_python_source


def test_extracts_top_level_python_structure() -> None:
    source = """\
import os
from pathlib import Path

async def fetch() -> None:
    pass

class Service(BaseService):
    def run(self) -> None:
        pass

    async def stop(self) -> None:
        pass
"""

    result = analyze_python_source(source, "service.py")

    assert result.syntax_error is None
    assert result.line_count == 12
    assert result.imports == ["os", "pathlib: Path"]
    assert [(item.name, item.line, item.is_async) for item in result.functions] == [
        ("fetch", 4, True)
    ]
    assert len(result.classes) == 1
    assert result.classes[0].name == "Service"
    assert result.classes[0].bases == ("BaseService",)
    assert [method.name for method in result.classes[0].methods] == ["run", "stop"]


def test_returns_syntax_error_as_data() -> None:
    result = analyze_python_source("def broken(:\n    pass\n", "broken.py")

    assert result.syntax_error is not None
    assert "line 1" in result.syntax_error


def test_analyze_python_file_rejects_other_extensions(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="only for .py"):
        analyze_python_file(path)
