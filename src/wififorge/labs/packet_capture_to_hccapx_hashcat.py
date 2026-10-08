"""WifiForge lab: Capture to HCCAPX / Hashcat."""

from __future__ import annotations

from ._harness import run_lab
from .materials import path as material
from ._scenarios import standard_range
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Capture to HCCAPX / Hashcat",
    category=Category.CRACKING,
    difficulty=Difficulty.ADVANCED,
    tools=("hcxtools", "hashcat"),
    summary=(
        "Convert a wireless handshake capture to the hashcat 22000/HCCAPX format and "
        "crack the WPA/WPA2 password with GPU-accelerated hashcat."
    ),
)


def run() -> None:
    run_lab("HCCAPX_HASHCAT", ["Attacker", "host_machine"], standard_range)
    # Hashcat refuses to re-crack a hash already in its potfile; reset for next time.
    material("loot", "4whs.pot").unlink(missing_ok=True)
