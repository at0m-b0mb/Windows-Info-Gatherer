"""Collector infrastructure: platform detection and a safe command runner.

On Windows the collectors shell out to native tools (``systeminfo``,
``powershell``, ``netsh`` ...).  On any other OS -- or if a command fails --
they fall back to the bundled demo data so the GUI stays fully populated for
screenshots, demos and development on macOS/Linux.
"""

from __future__ import annotations

import platform
import subprocess
from typing import List

IS_WINDOWS = platform.system() == "Windows"

# Force-demo can be toggled from the CLI (``--demo``) so the live UI can be
# exercised anywhere.  When True, collectors never touch the real system.
_FORCE_DEMO = not IS_WINDOWS


def set_demo_mode(force: bool) -> None:
    global _FORCE_DEMO
    _FORCE_DEMO = force or not IS_WINDOWS


def is_demo() -> bool:
    return _FORCE_DEMO


def run(cmd: List[str], timeout: int = 25) -> str:
    """Run a command and return stdout as text, or ``""`` on any failure.

    Never raises -- collectors depend on this degrading gracefully so a single
    missing tool (e.g. ``wmic`` removed on Windows 11) can't crash a scan.
    """
    if _FORCE_DEMO:
        return ""
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return completed.stdout or ""
    except Exception:
        return ""


def powershell(script: str, timeout: int = 30) -> str:
    """Run a PowerShell snippet and return stdout (or ``""``)."""
    return run(
        [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        timeout=timeout,
    )


def first_line(text: str, default: str = "") -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return default


class Collector:
    """Base class for a single category collector."""

    key = "base"
    name = "Base"
    icon = "•"
    subtitle = ""

    def collect(self):  # -> Category
        raise NotImplementedError
