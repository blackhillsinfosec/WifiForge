"""Regression tests for the issues raised in the v4.0.0 QA/QC review.

Each test names the lab whose failure it guards against. None of them need
mininet-wifi, a display, or root.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

from wififorge.labs._scenarios import standard_range
from wififorge.labs.materials import path as material

REPO = Path(__file__).resolve().parents[1]

# LLC/SNAP header announcing an EAPOL (0x888e) payload in an 802.11 data frame.
_EAPOL_SNAP = bytes.fromhex("aaaa03000000888e")


class _FakeNet:
    def __init__(self) -> None:
        self.aps: dict[str, dict] = {}

    def addStation(self, name, **kw):  # noqa: N802 - mirrors mininet-wifi's API
        return name

    def addAccessPoint(self, name, **kw):  # noqa: N802
        self.aps[name] = kw
        return name

    def addLink(self, *a, **kw):  # noqa: N802
        pass

    def configureWifiNodes(self):  # noqa: N802
        pass


# --- Lab 02: Airsuite ---------------------------------------------------------

def test_standard_range_leaves_ap_macs_to_hwsim():
    """A pinned MAC moved WPA2_Network off the BSSID the walkthrough filters on."""
    net = _FakeNet()
    standard_range(net)
    assert net.aps["ap1"]["ssid"] == "WPA2_Network"
    pinned = {name: kw["mac"] for name, kw in net.aps.items() if "mac" in kw}
    assert pinned == {}, f"APs must use hwsim's default MACs, found {pinned}"


# --- Lab 01: HCCAPX / Hashcat -------------------------------------------------

def test_lab01_capture_contains_a_handshake():
    """The walkthrough's capture must hold EAPOL frames (loot/4whs is a 1-frame stub)."""
    data = material("loot", "4whs-01.cap").read_bytes()
    assert data.count(_EAPOL_SNAP) >= 2


@pytest.mark.skipif(shutil.which("hcxpcapngtool") is None, reason="hcxtools not installed")
def test_lab01_capture_converts_to_22000(tmp_path):
    out = tmp_path / "lab01.hc22000"
    subprocess.run(
        ["hcxpcapngtool", "-o", str(out), str(material("loot", "4whs-01.cap"))],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    assert out.is_file() and b"WPA2_Network".hex() in out.read_text()


# --- Labs 01 and 07: browser launcher -----------------------------------------

def _browser():
    loader = importlib.machinery.SourceFileLoader("wf_browser", str(material("browser")))
    spec = importlib.util.spec_from_loader("wf_browser", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("argv", "ua_has", "url"),
    [
        (["linux"], None, None),
        (["linux", "/wififorge/x/index.html"], None, "file:///wififorge/x/index.html"),
        (["linux", "file:///tmp/a.html"], None, "file:///tmp/a.html"),
        (["linux", "10.0.0.1"], None, "http://10.0.0.1"),
        (["windows"], "Windows NT 10.0", None),
        (["windows", "8.1"], "Windows NT 6.3", None),  # a version is not a URL
        (["windows", "7", "http://10.0.0.1"], "Windows NT 6.1", "http://10.0.0.1"),
        (["mac os"], "Macintosh", None),
    ],
)
def test_browser_argument_parsing(argv, ua_has, url):
    ua, got_url = _browser().parse_args(argv)
    assert (ua is None) if ua_has is None else (ua_has in ua)
    assert got_url == url


def test_browser_uses_an_isolated_profile_and_no_empty_args():
    b = _browser()
    cmd = b.build_command("chromium", None, "http://10.0.0.1", "/tmp/prof")
    assert "--user-data-dir=/tmp/prof" in cmd
    assert "--no-sandbox" in cmd and "--disable-dev-shm-usage" in cmd
    assert "" not in cmd and not any(a.startswith("--user-agent") for a in cmd)
    assert cmd[-1] == "http://10.0.0.1"


def test_browser_reports_missing_local_files(capsys):
    rc = _browser().main(["linux", "/definitely/not/here.html"])
    assert rc == 1
    assert "/definitely/not/here.html" in capsys.readouterr().out


# --- Lab 04 and 06: system installer -----------------------------------------

def test_installer_is_valid_bash():
    subprocess.run(["bash", "-n", str(REPO / "install-system-deps.sh")], check=True)


def test_installer_launches_airgeddon_through_a_wrapper():
    script = (REPO / "install-system-deps.sh").read_text()
    assert "ln -sf \"${AIRGEDDON_DIR}/airgeddon.sh\"" not in script
    assert "AIRGEDDON_WINDOWS_HANDLING" in script and "tmux" in script


def test_installer_ensures_jumbo_john():
    script = (REPO / "install-system-deps.sh").read_text()
    assert "john_has_netntlm" in script and "openwall/john" in script


# --- Lab 09: drone tracker ----------------------------------------------------

def test_plotext_is_pinned_below_6():
    assert '"plotext>=5.2,<6"' in (REPO / "pyproject.toml").read_text()


def test_drone_controller_writes_atomically():
    src = material("control-drones.py").read_text()
    assert "os.replace" in src
    assert 'open("/tmp/drone-info.json", "w")' not in src
