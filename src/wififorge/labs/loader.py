"""Discover and load lab modules robustly.

Improvements over the original ``load_functions_from_py_files``:

* **Error isolation** — each module is imported in its own try/except, so a lab
  with a bad import no longer takes down the entire menu. Failures surface as
  disabled entries that show *why* they failed.
* **Lazy execution** — importing a module to read its metadata does not run the
  lab; the entry callable is invoked only when the user launches it.
* **No entry-point guessing** — the loader prefers an explicit ``run`` callable,
  then a declared ``LAB``; only as a last resort does it fall back to the first
  function *defined in that module* (``func.__module__ == module name``), which
  fixes the old "first function alphabetically, including imports" bug.
* **Rich metadata** — ``LabMeta`` drives the UI; legacy modules exposing only a
  ``description`` string still load, with category/difficulty inferred.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import pkgutil
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ._schema import Difficulty, LabMeta, humanize, infer_category

Runner = Callable[[], None]


@dataclass
class Lab:
    """A discovered lab, loadable on demand."""

    key: str                      # unique id (module stem)
    meta: LabMeta
    source: Path
    _module_name: str
    error: str | None = None   # populated if the module failed to import

    @property
    def available(self) -> bool:
        return self.error is None

    def load_runner(self) -> Runner:
        """Import the module (if needed) and return its entry callable.

        Raises if the lab is unavailable or exposes no runnable entry point.
        """
        if self.error:
            raise RuntimeError(self.error)
        module = importlib.import_module(self._module_name)
        runner = _resolve_runner(module)
        if runner is None:
            raise RuntimeError(f"{self.key}: no run() entry point found")
        return runner


def _resolve_runner(module: Any) -> Runner | None:
    run = getattr(module, "run", None)
    if callable(run):
        return run
    # Legacy fallback: first function *defined in this module*.
    import inspect

    mod_name = getattr(module, "__name__", "")
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if func.__module__ == mod_name and not name.startswith("_"):
            return func
    return None


def _meta_from_module(module: Any, stem: str) -> LabMeta:
    declared = getattr(module, "LAB", None)
    if isinstance(declared, LabMeta):
        return declared
    # Legacy: synthesise from `description` + filename inference.
    summary = getattr(module, "description", None) or (module.__doc__ or "")
    summary = " ".join(str(summary).split()) or "No description provided."
    return LabMeta(
        title=humanize(stem),
        summary=summary,
        category=infer_category(stem),
        difficulty=Difficulty.INTERMEDIATE,
    )


def discover(package: str = "wififorge.labs", extra_dir: Path | None = None) -> list[Lab]:
    """Return all labs found in ``package`` and, optionally, ``extra_dir``.

    ``extra_dir`` lets advanced users drop additional lab ``.py`` files in a
    directory (``--labs-dir`` / ``$WIFIFORGE_LABS``) without reinstalling.
    """
    labs: list[Lab] = []
    labs.extend(_discover_package(package))
    if extra_dir is not None:
        labs.extend(_discover_dir(extra_dir))

    # Stable, human-friendly ordering: by category, then title.
    labs.sort(key=lambda lab: (lab.meta.category.order, lab.meta.title.lower()))
    return labs


def _discover_package(package: str) -> list[Lab]:
    try:
        pkg = importlib.import_module(package)
    except Exception:
        return []
    pkg_path = getattr(pkg, "__path__", None)
    if not pkg_path:
        return []

    labs: list[Lab] = []
    for info in pkgutil.iter_modules(pkg_path):
        if info.name.startswith("_") or info.name in {"loader", "_schema"}:
            continue
        module_name = f"{package}.{info.name}"
        source = Path(list(pkg_path)[0]) / f"{info.name}.py"
        lab = _load_one(module_name, info.name, source)
        if lab is not None:
            labs.append(lab)
    return labs


def _discover_dir(directory: Path) -> list[Lab]:
    if not directory.is_dir():
        return []
    labs: list[Lab] = []
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
    for entry in sorted(directory.glob("*.py")):
        if entry.name.startswith("_"):
            continue
        stem = entry.stem
        lab = _load_one(stem, stem, entry)
        if lab is not None:
            labs.append(lab)
    return labs


def _looks_like_lab(module: Any) -> bool:
    """A module is a lab if it opts in with LAB/run, or the legacy `description`.

    This keeps helper modules in the labs package (e.g. ``materials.py``) from
    being misread as labs by the legacy first-function fallback.
    """
    return any(hasattr(module, attr) for attr in ("LAB", "run", "description"))


def _load_one(module_name: str, stem: str, source: Path) -> Lab | None:
    """Import a module just far enough to read its metadata, isolating failures.

    Returns ``None`` for modules that are not labs.
    """
    try:
        module = importlib.import_module(module_name)
    except Exception:
        err = _short_traceback()
        return Lab(
            key=stem,
            meta=LabMeta(
                title=humanize(stem),
                summary="This lab failed to load — see the error below.",
                category=infer_category(stem),
            ),
            source=source,
            _module_name=module_name,
            error=err,
        )
    if not _looks_like_lab(module):
        return None
    return Lab(
        key=stem,
        meta=_meta_from_module(module, stem),
        source=source,
        _module_name=module_name,
    )


def _short_traceback(limit: int = 2) -> str:
    exc = traceback.format_exc().strip().splitlines()
    # Keep the final (most useful) lines.
    return " | ".join(exc[-limit:]) if exc else "unknown import error"


def labs_dir_from_env() -> Path | None:
    raw = os.environ.get("WIFIFORGE_LABS")
    return Path(raw).expanduser() if raw else None
