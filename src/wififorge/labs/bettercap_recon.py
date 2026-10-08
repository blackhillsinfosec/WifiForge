"""WifiForge lab: Bettercap Recon."""

from __future__ import annotations

from ._harness import run_lab
from ._scenarios import standard_range
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Bettercap Recon",
    category=Category.RECON,
    difficulty=Difficulty.BEGINNER,
    tools=("bettercap",),
    summary=(
        "Drive Bettercap to scan for nearby access points and clients and build a "
        "picture of the surrounding wireless environment."
    ),
)


def run() -> None:
    run_lab("BETTERCAP_RECON", ["Attacker"], standard_range)
