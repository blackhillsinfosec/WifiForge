"""WifiForge lab: Cracking WPA with Aircrack."""

from __future__ import annotations

from ._harness import run_lab
from ._scenarios import standard_range
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Cracking WPA with Aircrack",
    category=Category.CRACKING,
    difficulty=Difficulty.INTERMEDIATE,
    tools=("aircrack-ng",),
    summary=(
        "Take a captured WPA/WPA2 handshake and recover the passphrase with "
        "Aircrack-ng using a dictionary attack."
    ),
)


def run() -> None:
    run_lab("WPA_CRACK", ["Attacker"], standard_range)
