from __future__ import annotations

import re
from dataclasses import dataclass

from local_cp.ai.models import CodeContext

_PRIVATE_KEY_HEADER = re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")
_KEY_SHAPE = re.compile(r"\b(?:AIza[0-9A-Za-z_-]{30,}|AKIA[0-9A-Z]{16}|sk-[0-9A-Za-z_-]{20,})\b")
_LITERAL_ASSIGNMENT = re.compile(
    r"(?i)\b(?:api_?key|secret|token|password|passwd|client_?secret|access_?key)\b"
    r"[^\n=]{0,30}=\s*[rubfRUBF]*(['\"])([^'\"\n]{8,})\1"
)


@dataclass(frozen=True, slots=True)
class SecretFinding:
    location: str
    line: int
    reason: str


def scan_request(question: str, context: CodeContext) -> tuple[SecretFinding, ...]:
    """Flag a few high-signal patterns locally; never return matched values."""
    findings: list[SecretFinding] = []
    sources = [("question", question)] + [
        (file.relative_path, file.source) for file in context.files
    ]
    for location, source in sources:
        for line_number, line in enumerate(source.splitlines(), start=1):
            if _PRIVATE_KEY_HEADER.search(line):
                findings.append(SecretFinding(location, line_number, "private key header"))
            elif _KEY_SHAPE.search(line):
                findings.append(SecretFinding(location, line_number, "credential-shaped value"))
            elif _LITERAL_ASSIGNMENT.search(line):
                findings.append(SecretFinding(location, line_number, "hardcoded credential"))
    return tuple(findings)
