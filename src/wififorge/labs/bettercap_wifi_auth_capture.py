"""WifiForge lab: Bettercap Auth Capture."""

from __future__ import annotations

from ._harness import run_lab
from ._scenarios import standard_range
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Bettercap Auth Capture",
    category=Category.CAPTURE,
    difficulty=Difficulty.INTERMEDIATE,
    tools=("bettercap",),
    summary=(
        "Use Bettercap to deauthenticate a client and capture the WPA/WPA2 "
        "authentication handshake for later offline cracking."
    ),
)


def run() -> None:
    run_lab("BETTERCAP_AUTH_CAP", ["Attacker"], standard_range)
