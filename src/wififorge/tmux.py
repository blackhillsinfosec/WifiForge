"""Lay out a tmux session with one pane per mininet node.

Refactor of the original ``CONNECT_TMUX.py``. Key fixes:

* no more building a shell pipeline with ``shell=True`` and an interpolated node
  name (a command-injection footgun); node PIDs are found with a plain ``pgrep``
  and ``nsenter`` is invoked with an argument list,
* the session is always torn down via ``try/finally`` instead of a duplicated
  kill call plus a bare ``except Exception`` that swallowed everything,
* typed and documented.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence

try:  # libtmux is a runtime dep, but keep import failure survivable for tests
    import libtmux
    from libtmux.pane import PaneDirection
except Exception:  # pragma: no cover - exercised only without libtmux installed
    libtmux = None  # type: ignore[assignment]
    PaneDirection = None  # type: ignore[misc, assignment]

# Panes named this are left as a plain host shell (GUI apps like a browser don't
# cooperate with the nsenter "remote bash" trick).
HOST_PANE = "host_machine"


def _node_pid(node: str) -> str | None:
    """Return the PID of a running mininet node process, or None if not found."""
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", f"mininet:{node}"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None
    for line in out.splitlines():
        pid = line.strip()
        if pid.isdigit():
            return pid
    return None


def config_tmux(nodes: Sequence[str], lab_name: str) -> None:
    """Open an attached tmux session with a titled pane per node in ``nodes``.

    Each non-host pane is dropped into the network namespace of its mininet node
    via ``nsenter`` so the learner gets a shell that sees that node's interfaces.
    """
    if libtmux is None:  # pragma: no cover
        raise RuntimeError("libtmux is not installed; run the system-deps installer")

    server = libtmux.Server()
    session_name = f"WIFIFORGE-{lab_name}"
    session = server.new_session(session_name=session_name, attach=False)
    try:
        window = session.windows[0]

        # One pane per node.
        while len(window.panes) < len(nodes):
            window.panes[-1].split(direction=PaneDirection.Left, attach=False)

        for index, _pane in enumerate(window.panes):
            node = nodes[index]
            if node == HOST_PANE:
                session.cmd("select-pane", "-t", index, "-T", HOST_PANE)
                continue

            pid = _node_pid(node)
            if pid is None:
                session.cmd("select-pane", "-t", index, "-T", f"{node} (not found)")
                continue

            enter_ns = (
                f"sudo nsenter -t {pid} -m -u -i -n -p "
                "bash -c 'clear; exec bash'"
            )
            subprocess.run(
                ["tmux", "send-keys", "-t", f"{session_name}:0.{index}", enter_ns, "C-m"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            session.cmd("select-pane", "-t", index, "-T", node)

        session.cmd("set", "-g", "pane-border-status", "top")
        session.cmd("set", "-g", "mouse", "on")
        session.cmd("select-layout", "tiled")
        # Attach with the tmux CLI rather than ``session.attach()``: libtmux
        # refreshes the session after attach returns, which raises
        # "no server running" once the learner has exited every pane (tmux
        # shuts its server down when the last session ends).
        subprocess.run(["tmux", "attach-session", "-t", session_name], check=False)
    finally:
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
