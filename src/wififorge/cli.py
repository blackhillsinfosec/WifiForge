"""Command-line entry point for WifiForge.

Wires together discovery, the menu, and lab execution. Lab functions import
``mn_wifi`` lazily, so this module (and the menu) stay import-clean on machines
without mininet-wifi — useful for browsing labs or running the test suite.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from blessed import Terminal

from . import __version__
from .labs.loader import Lab, discover, labs_dir_from_env
from .runtime import (
    OVS_SERVICE,
    cap_open_file_limit,
    clean_mininet_state,
    is_root,
    mininet_available,
    start_openvswitch,
)
from .tui import Menu


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wififorge",
        description="A safe, legal, sandboxed environment for learning WiFi hacking.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"WifiForge {__version__}")
    parser.add_argument(
        "--labs-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Additional directory of lab .py files to load (also $WIFIFORGE_LABS).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List discovered labs and exit (no root or terminal UI required).",
    )
    parser.add_argument(
        "--allow-non-root",
        action="store_true",
        help="Skip the root check (labs will fail to build, but the menu is browsable).",
    )
    return parser


def _discover(args: argparse.Namespace) -> list[Lab]:
    extra = args.labs_dir or labs_dir_from_env()
    return discover(extra_dir=extra)


def _print_lab_list(labs: Sequence[Lab]) -> None:
    if not labs:
        print("No labs found.")
        return
    width = max(len(lab.meta.title) for lab in labs)
    last_cat = None
    for lab in labs:
        cat = lab.meta.category.value
        if cat != last_cat:
            print(f"\n{cat}")
            last_cat = cat
        status = "" if lab.available else "  (failed to load)"
        print(f"  {lab.meta.title.ljust(width)}  {lab.meta.difficulty.value}{status}")


def _launch(lab: Lab) -> None:
    """Run a lab, then clean up leftover mininet state."""
    try:
        runner = lab.load_runner()
    except Exception as exc:  # noqa: BLE001 - surface any load error to the user
        print(f"\nCould not start '{lab.meta.title}': {exc}")
        input("Press Enter to return to the menu...")
        return
    try:
        runner()
    finally:
        clean_mininet_state()


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    cap_open_file_limit()
    labs = _discover(args)

    if args.list:
        _print_lab_list(labs)
        return 0

    if not args.allow_non_root and not is_root():
        print("WifiForge must be run as root (labs create network namespaces and interfaces).")
        print("Re-run with sudo, or use --allow-non-root to browse the menu only.")
        return 1

    if not mininet_available():
        print("Warning: 'mn' (mininet) was not found on PATH — labs will not run.")
        print("Install system dependencies first (see ./install-system-deps.sh).\n")

    # mininet-wifi needs Open vSwitch running; start it once up front. Skipped
    # when browsing as non-root, since starting a service requires root anyway.
    if is_root():
        error = start_openvswitch()
        if error:
            print(f"Warning: could not start {OVS_SERVICE} ({error}) — labs may fail to build.")
            print(f"Try: sudo service {OVS_SERVICE} start\n")

    term = Terminal()
    menu = Menu(term=term, labs=labs)
    try:
        menu.run(on_launch=_launch)
    except KeyboardInterrupt:
        pass
    finally:
        print(term.normal + term.clear, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
