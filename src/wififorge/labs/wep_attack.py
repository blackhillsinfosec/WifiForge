"""WifiForge lab: WEP key recovery."""

from __future__ import annotations

from typing import Any

from ._harness import run_lab
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="WEP Attack",
    category=Category.ATTACK,
    difficulty=Difficulty.BEGINNER,
    tools=("aireplay-ng", "aircrack-ng"),
    summary=(
        "Exploit WEP's broken encryption: generate traffic with aireplay-ng to "
        "collect initialization vectors, then recover the key with aircrack-ng."
    ),
)


def _topology(net: Any) -> list:
    net.addStation("Attacker", passwd="123456789a", encrypt="wep", wlans=2)
    host1 = net.addStation("host1", passwd="123456789a", encrypt="wep")
    host2 = net.addStation("host2", passwd="123456789a", encrypt="wep")
    ap1 = net.addAccessPoint(
        "ap1", ssid="WEP_NETWORK", mode="g", channel="6",
        passwd="123456789a", encrypt="wep", failMode="standalone", datapath="user",
    )
    net.configureWifiNodes()
    net.addLink(host1, ap1)
    net.addLink(host2, ap1)
    return [ap1]


def run() -> None:
    run_lab("WEP_ATTACK", ["Attacker", "host1", "host2"], _topology)
