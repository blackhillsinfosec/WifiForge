"""Locate bundled lab data files (wordlists, captures, helper scripts).

Labs and walkthroughs that need a supporting file should resolve it through
:func:`path` rather than hard-coding an absolute location like the original
``/WifiForge/framework/...`` paths, which broke whenever the repo lived anywhere
else.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent / "materials"


def path(*parts: str) -> Path:
    """Return the absolute path to a bundled material, e.g. ``path("shell.py")``."""
    return _ROOT.joinpath(*parts)


def root() -> Path:
    return _ROOT
