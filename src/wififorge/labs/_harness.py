"""Shared lab lifecycle helpers.

Every lab used to repeat the same boilerplate: start a Halo spinner, create a
``Mininet_wifi``, build, start each AP, hand off to tmux, then tear everything
down. That is centralised here so a lab is just *metadata + topology*.

Crucially, ``mn_wifi`` is imported **lazily** (inside the functions, not at module
top) so a machine without mininet-wifi installed can still import every lab to
show it in the menu — the heavy dependency is only touched when a lab is actually
launched.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any, Callable, Optional

from halo import Halo

from ..tmux import config_tmux

# A topology callback adds nodes/links to a net and returns the APs to start.
Topology = Callable[[Any], Optional[Sequence[Any]]]
OnReady = Callable[[Any], None]


def clear_screen() -> None:
    os.system("clear")


def _new_net() -> Any:
    from mn_wifi.net import Mininet_wifi  # lazy: keeps the menu usable w/o mininet

    return Mininet_wifi()


@contextmanager
def spinner(text: str = "Building lab network") -> Iterator[Halo]:
    spin = Halo(text=text, spinner="dots", color="red")
    spin.start()
    try:
        yield spin
    finally:
        spin.stop()


def run_lab(
    session_name: str,
    panes: Sequence[str],
    topology: Topology,
    *,
    on_ready: OnReady | None = None,
) -> None:
    """Build a lab network, drop the learner into tmux, then clean up.

    ``topology(net)`` must add the stations/APs/links (and call
    ``configureWifiNodes``) and return the list of access points to start.
    ``on_ready(net)`` runs after ``build()`` and AP start, for any extra setup
    commands a lab needs.
    """
    spin = Halo(text="Building lab network", spinner="dots", color="red")
    spin.start()
    net = _new_net()
    try:
        aps = topology(net) or []
        net.build()
        for ap in aps:
            ap.start([])
        if on_ready is not None:
            on_ready(net)
        spin.stop()
        config_tmux(list(panes), session_name)
    finally:
        spin.start()
        try:
            net.stop()
        finally:
            spin.stop()
            clear_screen()


def reap(process_name: str) -> None:
    """Kill lingering helper processes (e.g. wifiphisher) by name, safely."""
    subprocess.run(
        ["pkill", "-9", "-f", process_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
