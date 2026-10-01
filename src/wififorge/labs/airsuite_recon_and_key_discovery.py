"""WifiForge lab: Airsuite Recon & Key Discovery."""

from __future__ import annotations

from ._harness import run_lab
from ._scenarios import standard_range
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Airsuite Recon & Key Discovery",
    category=Category.RECON,
    difficulty=Difficulty.INTERMEDIATE,
    tools=("airodump-ng", "aircrack-ng", "aireplay-ng"),
    summary=(
        "Use the Aircrack-ng suite to survey the airspace, capture handshakes, and "
        "attempt key discovery against the WEP and WPA/WPA2 networks in range."
    ),
)


def run() -> None:
    run_lab("AIRSUITE_RECON", ["Attacker", "Attacker"], standard_range)
