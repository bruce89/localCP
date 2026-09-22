from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FunctionInfo:
    name: str
    line: int
    is_async: bool = False


@dataclass(frozen=True, slots=True)
class ClassInfo:
    name: str
    line: int
    bases: tuple[str, ...] = ()
    methods: tuple[FunctionInfo, ...] = ()


@dataclass(slots=True)
class PythonAnalysis:
    path: str
    line_count: int
    imports: list[str] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    syntax_error: str | None = None
