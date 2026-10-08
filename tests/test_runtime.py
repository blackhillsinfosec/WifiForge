"""Tests for the Open vSwitch startup helper (no real services are touched)."""

from __future__ import annotations

import subprocess

from wififorge import runtime


def _fake_run(calls, returncode=0, stderr=""):
    def run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, returncode, stderr=stderr)

    return run


def test_uses_service_command(monkeypatch):
    calls = []
    monkeypatch.setattr(runtime.shutil, "which", lambda name: f"/usr/sbin/{name}")
    monkeypatch.setattr(runtime.subprocess, "run", _fake_run(calls))
    assert runtime.start_openvswitch() is None
    assert calls == [["service", "openvswitch-switch", "start"]]


def test_falls_back_to_systemctl(monkeypatch):
    calls = []
    monkeypatch.setattr(
        runtime.shutil, "which", lambda name: "/bin/systemctl" if name == "systemctl" else None
    )
    monkeypatch.setattr(runtime.subprocess, "run", _fake_run(calls))
    assert runtime.start_openvswitch() is None
    assert calls == [["systemctl", "start", "openvswitch-switch"]]


def test_reports_failure(monkeypatch):
    monkeypatch.setattr(runtime.shutil, "which", lambda name: f"/usr/sbin/{name}")
    monkeypatch.setattr(
        runtime.subprocess, "run", _fake_run([], returncode=1, stderr="Unit not found.\n")
    )
    assert runtime.start_openvswitch() == "Unit not found."


def test_no_service_manager(monkeypatch):
    monkeypatch.setattr(runtime.shutil, "which", lambda name: None)
    assert runtime.start_openvswitch() is not None
