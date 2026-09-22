"""Project discovery and file access."""

from local_cp.project.explorer import read_text_file, scan_project
from local_cp.project.models import ProjectOverview

__all__ = ["ProjectOverview", "read_text_file", "scan_project"]
