"""Checks that the labs have what they need to run out of the box.

These don't need mininet-wifi: a recording stand-in for the network object lets
us inspect each topology, and the bundled materials are checked on disk.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import types
from functools import partial

import pytest

from wififorge import runtime, tmux
from wififorge.banner import banner_height, banner_lines, banner_width
from wififorge.labs import airgeddon_dos
from wififorge.labs.materials import path as material
from wififorge.tui import geometry


class FakeNet:
    """Records topology calls so a lab's network can be inspected."""

    def __init__(self) -> None:
        self.stations: dict[str, dict] = {}
        self.aps: dict[str, dict] = {}

    def addStation(self, name, **kw):  # noqa: N802 - mirrors mininet-wifi's API
        self.stations[name] = kw
        return name

    def addAccessPoint(self, name, **kw):  # noqa: N802
        self.aps[name] = kw
        return name

    def addLink(self, *a, **kw):  # noqa: N802
        pass

    def addController(self, *a, **kw):  # noqa: N802
        pass

    def configureWifiNodes(self):  # noqa: N802
        pass


# Files the walkthroughs and lab code point learners at.
@pytest.mark.parametrize(
    "parts",
    [
        ("rockyou.txt",),
        ("loot", "4whs"),
        ("loot", "4whs-01.cap"),
        ("eaphammer",),
        ("browser",),
        ("shell.py",),
        ("graph-drones.py",),
        ("control-drones.py",),
        ("hashcat.net", "cap2hashcat", "index.html"),
    ],
)
def test_bundled_material_exists(parts):
    assert material(*parts).is_file(), material(*parts)


def test_airgeddon_attacker_has_two_radios(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        airgeddon_dos, "run_lab", lambda name, panes, topo: captured.setdefault("topo", topo)
    )
    airgeddon_dos.run()
    net = FakeNet()
    topo = captured["topo"]
    assert isinstance(topo, partial)
    topo(net)
    assert net.stations["Attacker"]["wlans"] == 2


def test_eaphammer_saves_next_to_itself():
    src = material("eaphammer").read_text()
    assert "/WifiForge/framework" not in src
    assert "LOOT_DIR" in src


def test_mininet_class_state_is_reset(monkeypatch):
    mob = types.ModuleType("mn_wifi.mobility")
    mod = types.ModuleType("mn_wifi.module")

    class Mobility:
        aps = ["stale"]

    class ConfigMobLinks(Mobility):
        aps = ["stale"]

    class Mac80211Hwsim:
        hwsim_ids = [1, 2, 3]

    mob.Mobility, mob.ConfigMobLinks, mod.Mac80211Hwsim = Mobility, ConfigMobLinks, Mac80211Hwsim
    monkeypatch.setitem(sys.modules, "mn_wifi", types.ModuleType("mn_wifi"))
    monkeypatch.setitem(sys.modules, "mn_wifi.mobility", mob)
    monkeypatch.setitem(sys.modules, "mn_wifi.module", mod)
    monkeypatch.setattr(runtime, "mininet_available", lambda: False)

    runtime.clean_mininet_state()

    assert Mobility.aps == [] and ConfigMobLinks.aps == [] and Mac80211Hwsim.hwsim_ids == []


@pytest.mark.skipif(shutil.which("tmux") is None, reason="tmux not installed")
def test_main_menu_ends_only_wififorge_sessions():
    sock = ["tmux", "-L", "wififorge-test"]
    subprocess.run([*sock, "new-session", "-d", "-s", "WIFIFORGE-X"], check=True)
    subprocess.run([*sock, "new-session", "-d", "-s", "other"], check=True)
    real = subprocess.check_output

    def on_test_socket(cmd, **kw):
        return real([*sock, *cmd[1:]], **kw)

    orig_run = subprocess.run
    try:
        tmux.subprocess.check_output = on_test_socket
        tmux.subprocess.run = lambda cmd, **kw: orig_run([*sock, *cmd[1:]], **kw)
        assert tmux.kill_lab_sessions() == 1
        names = real([*sock, "list-sessions", "-F", "#{session_name}"], text=True).split()
        assert names == ["other"]
    finally:
        tmux.subprocess.check_output = real
        tmux.subprocess.run = orig_run
        orig_run([*sock, "kill-server"], check=False)


def test_menu_never_shows_a_banner_that_crowds_out_the_labs():
    for compact in (False, True):
        h = banner_height(compact)
        too_short = geometry.compute(100, h + geometry.MIN_LIST_ROWS, h)
        assert not too_short.show_banner
        roomy_h = max(geometry.BANNER_MIN_HEIGHT, h + geometry.MIN_LIST_ROWS + 2)
        roomy = geometry.compute(100, roomy_h, h)
        assert roomy.show_banner


def test_compact_banner_is_the_wordmark():
    lines = banner_lines(compact=True)
    assert len(lines) == banner_height(compact=True) == 7
    assert banner_width(compact=True) <= geometry.BANNER_MIN_WIDTH
