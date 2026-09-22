from __future__ import annotations

import os
import sys


def gemini_api_key() -> str | None:
    """Read the current process or Windows user environment; never persist the key."""
    value = os.environ.get("GEMINI_API_KEY")
    if value:
        return value
    if sys.platform != "win32":
        return None
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, "GEMINI_API_KEY")
    except OSError:
        return None
    return value if isinstance(value, str) and value else None
