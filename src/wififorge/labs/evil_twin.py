"""WifiForge lab: Evil Twin."""

from __future__ import annotations

from typing import Any

from ._harness import run_lab
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Evil Twin",
    category=Category.ATTACK,
    difficulty=Difficulty.INTERMEDIATE,
    tools=("hostapd", "mininet-wifi"),
    summary=(
        "Stand up a rogue access point impersonating a legitimate network to "
        "lure clients into associating with you, a stepping stone to credential "
        "harvesting or content injection."
    ),
)


def _topology(net: Any) -> list:
    attacker = net.addStation("Attacker", passwd="JERRY277626AA", encrypt="wpa2", wlans=2)
    host1 = net.addStation("host1", passwd="JERRY277626AA", encrypt="wpa2", wlans=2)
    ap1 = net.addAccessPoint(
        "ap1", ssid="CORP_NET", mode="g", channel="1",
        passwd="JERRY277626AA", encrypt="wpa2",
    )
    net.configureWifiNodes()
    net.addLink(attacker, ap1)
    net.addLink(host1, ap1)
    return [ap1]


def run() -> None:
    run_lab("EVIL_TWIN", ["Attacker"], _topology)
