"""WifiForge lab: Wifiphisher rogue-AP phishing."""

from __future__ import annotations

from typing import Any

from ._harness import reap, run_lab
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="Wifiphisher",
    category=Category.PHISHING,
    difficulty=Difficulty.INTERMEDIATE,
    tools=("wifiphisher",),
    summary=(
        "Run Wifiphisher to stand up a rogue AP and a captive-portal phishing "
        "page, demonstrating how clients can be tricked into handing over "
        "credentials."
    ),
)


def _topology(net: Any) -> list:
    attacker = net.addStation("Attacker", wlans=2, passwd="december2022", encrypt="wpa2")
    host1 = net.addStation("host1", passwd="december2022", encrypt="wpa2")
    host2 = net.addStation("host2", passwd="december2022", encrypt="wpa2")
    ap = net.addAccessPoint(
        "ap1", ssid="mywifi", passwd="december2022", encrypt="wpa2",
        mode="g", channel="6",
    )
    net.configureWifiNodes()
    net.addLink(attacker, ap)
    net.addLink(host1, ap)
    net.addLink(host2, ap)
    return [ap]


def run() -> None:
    run_lab("WIFIPHISHER", ["Attacker", "host1"], _topology)
    # Wifiphisher can outlive the lab; reap any stragglers it left behind.
    reap("wifiphisher")
