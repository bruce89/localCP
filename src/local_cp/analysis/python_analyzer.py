from __future__ import annotations

import ast
from pathlib import Path

from local_cp.analysis.models import ClassInfo, FunctionInfo, PythonAnalysis
from local_cp.project.explorer import read_text_file


def _expression_name(node: ast.expr) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - defensive fallback for unusual AST nodes
        return node.__class__.__name__


def _function_info(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
    return FunctionInfo(
        name=node.name,
        line=node.lineno,
        is_async=isinstance(node, ast.AsyncFunctionDef),
    )


def analyze_python_source(source: str, path: str = "<memory>") -> PythonAnalysis:
    """Extract top-level Python structure without importing or executing code."""
    result = PythonAnalysis(path=path, line_count=len(source.splitlines()))
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as error:
        location = f"line {error.lineno}"
        if error.offset is not None:
            location += f", column {error.offset}"
        result.syntax_error = f"{error.msg} ({location})"
        return result

    for node in tree.body:
        if isinstance(node, ast.Import):
            result.imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            names = ", ".join(alias.name for alias in node.names)
            result.imports.append(f"{module}: {names}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.functions.append(_function_info(node))
        elif isinstance(node, ast.ClassDef):
            methods = tuple(
                _function_info(child)
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            result.classes.append(
                ClassInfo(
                    name=node.name,
                    line=node.lineno,
                    bases=tuple(_expression_name(base) for base in node.bases),
                    methods=methods,
                )
            )
    return result


def analyze_python_file(path: Path) -> PythonAnalysis:
    if path.suffix.lower() != ".py":
        raise ValueError("Python analysis is available only for .py files.")
    return analyze_python_source(read_text_file(path), str(path))
