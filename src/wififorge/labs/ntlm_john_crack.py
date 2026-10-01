"""WifiForge lab: NTLM hash cracking with John the Ripper."""

from __future__ import annotations

from typing import Any

from ._harness import run_lab
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="NTLM John Crack",
    category=Category.CRACKING,
    difficulty=Difficulty.BEGINNER,
    tools=("john",),
    summary=(
        "Crack captured NTLM password hashes with John the Ripper to practise "
        "offline Windows credential recovery."
    ),
)


def _topology(net: Any) -> list:
    attacker = net.addStation("Attacker", passwd="JERRY277626AA", encrypt="wpa2", wlans=2)
    host1 = net.addStation("host1", passwd="JERRY277626AA", encrypt="wpa2", wlans=2)
    ap1 = net.addAccessPoint(
        "ap1", ssid="CORP_NET", mode="g", channel="1",
        passwd="JERRY277626AA", encrypt="wpa2",
    )
    net.addController("c0")
    net.configureWifiNodes()
    net.addLink(attacker, ap1)
    net.addLink(host1, ap1)
    return [ap1]


def run() -> None:
    run_lab("NTLM_JOHN_CRACK", ["Attacker"], _topology)
