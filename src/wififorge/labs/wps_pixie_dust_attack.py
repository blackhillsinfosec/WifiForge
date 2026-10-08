"""WifiForge lab: WPS Pixie Dust."""

from __future__ import annotations

from typing import Any

from ._harness import run_lab
from ._schema import Category, Difficulty, LabMeta

LAB = LabMeta(
    title="WPS Pixie Dust",
    category=Category.ATTACK,
    difficulty=Difficulty.ADVANCED,
    tools=("reaver", "bully"),
    summary=(
        "Exploit weak WPS Diffie-Hellman parameters with a Pixie Dust attack to "
        "recover the WPS PIN offline, then derive the WPA/WPA2 passphrase."
    ),
)


def run() -> None:
    nodes: dict = {}

    def topology(net: Any) -> list:
        attacker = net.addStation("Attacker", encrypt="wpa2")
        host1 = net.addStation("host1", encrypt="wpa2")
        ap1 = net.addAccessPoint(
            "ap1", ssid="secure_wifi", mode="g", channel="1",
            passwd="123456789a", encrypt="wpa2", failMode="standalone",
            datapath="user", wps_state="2",
            config_methods="label display push_button keypad",
        )
        net.configureWifiNodes()
        net.addLink(attacker, ap1)
        net.addLink(host1, ap1)
        nodes["attacker"] = attacker
        nodes["ap1"] = ap1
        return [ap1]

    def on_ready(net: Any) -> None:
        # Seed a known WPS PIN and bring up a monitor interface on the attacker.
        # (Original used "a-wlan0" — a leftover from when the node was named "a";
        # the real interface for the "Attacker" node is "Attacker-wlan0".)
        nodes["ap1"].cmd("hostapd_cli -i ap1-wlan1 wps_ap_pin set 12345670")
        nodes["attacker"].cmd("iw dev Attacker-wlan0 interface add mon0 type monitor")
        nodes["attacker"].cmd("ip link set mon0 up")

    run_lab("WPS", ["Attacker", "host1"], topology, on_ready=on_ready)
