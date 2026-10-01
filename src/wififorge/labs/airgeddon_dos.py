"""WifiForge lab: Airgeddon DoS."""

from __future__ import annotations

from ._harness import run_lab
from ._scenarios import standard_range
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Airgeddon DoS",
    category=Category.ATTACK,
    difficulty=Difficulty.BEGINNER,
    tools=("airgeddon", "aireplay-ng"),
    summary=(
        "Use Airgeddon to run a deauthentication denial-of-service against the "
        "practice range, forcing clients off their access points and observing "
        "the disruption."
    ),
)


def run() -> None:
    run_lab("AIRGEDDON_DOS", ["Attacker"], standard_range)
