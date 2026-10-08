"""WifiForge lab: wireless drone compromise.

A more involved scenario: two drones, each its own AP with a NAT'd control
service, reachable through the attacker's dual radio. Fixes from the original:

* ``dr2`` previously reused ``dr1``'s coordinates — each drone now uses its own,
* the helper shell is located via :mod:`wififorge.labs.materials` instead of a
  path relative to the source file, so it works wherever WifiForge is installed,
* the lab always tears down and removes its temp file, even on error.
"""

from __future__ import annotations

import json
import os
from typing import Any

from ._harness import clear_screen
from ._schema import Category, Difficulty, LabMeta
from .materials import path as material

LAB = LabMeta(
    title="Drone Hacking",
    category=Category.MISC,
    difficulty=Difficulty.ADVANCED,
    tools=("mininet-wifi", "custom tooling"),
    summary=(
        "Compromise two simulated wireless drones: crack their WPA2 networks, "
        "reach each drone's NAT'd control service, and take over its command "
        "shell."
    ),
)

_DRONES: dict[str, dict[str, Any]] = {
    "dr1": {
        "position": [20.0, 20.0, 0.0],
        "password": "password!",
        "listener": "10.1.0.254",
        "port": "4441",
    },
    "dr2": {
        "position": [10.0, 28.0, 0.0],
        "password": "arcangel",
        "listener": "10.2.0.254",
        "port": "4442",
    },
}
_INFO_FILE = "/tmp/drone-info.json"


def run() -> None:
    from halo import Halo
    from mn_wifi.net import Mininet_wifi

    from ..tmux import config_tmux

    spin = Halo(text="Building drone network", spinner="dots", color="red")
    spin.start()
    net = Mininet_wifi()
    try:
        attacker = net.addStation("Attacker", wlans=2)

        st1 = net.addStation(
            "st1", passwd=_DRONES["dr1"]["password"], encrypt="wpa2",
            mac="00:00:00:00:00:01", ip="10.1.0.10/24",
        )
        dr1 = net.addAccessPoint(
            "dr1", ssid="DRONE1", passwd=_DRONES["dr1"]["password"], encrypt="wpa2",
            mode="g", channel="3", failMode="standalone",
        )

        st2 = net.addStation(
            "st2", passwd=_DRONES["dr2"]["password"], encrypt="wpa2",
            mac="00:00:00:00:00:02", ip="10.2.0.10/24",
        )
        dr2 = net.addAccessPoint(
            "dr2", ssid="DRONE2", passwd=_DRONES["dr2"]["password"], encrypt="wpa2",
            mode="g", channel="6", failMode="standalone",
        )

        net.configureNodes()

        net.addLink(dr1, st1)
        net.addLink(dr2, st2)
        net.addLink(attacker, dr1)
        net.addLink(attacker, dr2)

        nat1 = net.addNAT(name="nat1")
        nat2 = net.addNAT(name="nat2")
        net.addLink(nat1, dr1)
        net.addLink(nat2, dr2)

        nat1.setIP(_DRONES["dr1"]["listener"] + "/24", intf="nat1-eth1")
        nat2.setIP(_DRONES["dr2"]["listener"] + "/24", intf="nat2-eth1")
        for n in (nat1, nat2):
            n.cmd("sysctl -w net.ipv4.ip_forward=1")
            n.cmd("iptables -t nat -A POSTROUTING -o nat1-eth0 -j MASQUERADE")

        st1.cmd(f'ip route add default via {_DRONES["dr1"]["listener"]}')
        st2.cmd(f'ip route add default via {_DRONES["dr2"]["listener"]}')

        net.build()
        dr1.start([])
        dr2.start([])

        # Each drone at its own coordinates (dr2 no longer copies dr1).
        for ap, key in ((dr1, "dr1"), (dr2, "dr2")):
            x, y, z = _DRONES[key]["position"]
            ap.setPosition(f"{x},{y},{z}")

        shell = material("shell.py")
        for ap, key in ((dr1, "dr1"), (dr2, "dr2")):
            ap.cmd(f'python3 {shell} {_DRONES[key]["password"]} {_DRONES[key]["port"]} &')

        with open(_INFO_FILE, "w") as f:
            json.dump(_DRONES, f)

        spin.stop()
        config_tmux(["Attacker", "Attacker", "Attacker"], "DRONES")
    finally:
        spin.start()
        try:
            net.stop()
        finally:
            spin.stop()
            clear_screen()
            if os.path.exists(_INFO_FILE):
                os.remove(_INFO_FILE)
