"""Process/environment concerns that sit outside the UI and the labs themselves.

Covers four things the original scattered across ``WifiForge.py``:

* capping ``RLIMIT_NOFILE`` so mininet-wifi starts quickly on high-ulimit distros,
* checking we are root (labs create network namespaces and interfaces),
* starting the Open vSwitch service mininet-wifi's access points depend on,
* tearing down mininet state between labs.

The teardown shells out to ``mn -c`` and also resets the few class-level lists
mininet-wifi keeps between networks (radio IDs, mobility APs). Those survive in the
Python process, so without the reset the *second* lab launched from the same menu
session inherits stale radio IDs and fails to build. Everything is no-op-safe when
mininet isn't installed, so the menu still runs for browsing on non-lab machines.
"""

from __future__ import annotations

import os
import shutil
import subprocess

# mininet-wifi iterates over every FD up to the soft limit at startup. On distros
# with a huge default (Kali 2025+ uses 1,048,576) that loop can take minutes,
# showing up as a lab stuck on "Loading". 2048 is comfortably above its real need.
# See: https://github.com/blackhillsinfosec/WifiForge/issues/91
_FD_SOFT_CAP = 2048


def cap_open_file_limit(cap: int = _FD_SOFT_CAP) -> None:
    """Lower the soft open-file limit if it is set absurdly high."""
    try:
        import resource

        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft > cap:
            resource.setrlimit(resource.RLIMIT_NOFILE, (cap, hard))
    except (ImportError, ValueError, OSError):
        # Non-POSIX or restricted sandbox: nothing we can do, and it's non-fatal.
        pass


def is_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def mininet_available() -> bool:
    return shutil.which("mn") is not None


OVS_SERVICE = "openvswitch-switch"


def start_openvswitch(service: str = OVS_SERVICE) -> str | None:
    """Start the Open vSwitch service (``service openvswitch-switch start``).

    mininet-wifi builds its access points on OVS bridges, so labs fail with
    "ovs-vsctl: unix:/var/run/openvswitch/db.sock: database connection failed"
    if the service isn't running. Starting an already-running service is a
    no-op, so this is safe to call on every launch.

    Returns ``None`` on success, or a short error message on failure. Falls back
    to ``systemctl`` on systems without the ``service`` wrapper.
    """
    if shutil.which("service"):
        cmd = ["service", service, "start"]
    elif shutil.which("systemctl"):
        cmd = ["systemctl", "start", service]
    else:
        return "neither 'service' nor 'systemctl' was found"
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return str(exc)
    if result.returncode != 0:
        return (result.stderr or "").strip() or f"exit status {result.returncode}"
    return None


def _reset_mininet_wifi_class_state() -> None:
    """Clear mininet-wifi's per-process radio bookkeeping (as the original did)."""
    try:
        from mn_wifi.mobility import ConfigMobLinks, Mobility
        from mn_wifi.module import Mac80211Hwsim
    except Exception:  # noqa: BLE001 - mininet-wifi absent or API changed
        return
    for cls, attr in ((Mobility, "aps"), (ConfigMobLinks, "aps"), (Mac80211Hwsim, "hwsim_ids")):
        if hasattr(cls, attr):
            setattr(cls, attr, [])


def clean_mininet_state() -> None:
    """Best-effort teardown of leftover mininet nodes/links between labs.

    Safe to call when mininet is absent (e.g. browsing the menu on a laptop).
    """
    _reset_mininet_wifi_class_state()
    if not mininet_available():
        return
    subprocess.run(
        ["mn", "-c"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
