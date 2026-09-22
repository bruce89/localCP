from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ProjectOverview:
    root: str
    file_count: int = 0
    directory_count: int = 0
    total_bytes: int = 0
    language_counts: dict[str, int] = field(default_factory=dict)
    skipped_count: int = 0
