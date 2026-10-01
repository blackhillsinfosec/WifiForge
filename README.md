# WifiForge

**A safe, legal, sandboxed environment for learning WiFi hacking.**

WifiForge spins up virtual wireless networks with
[mininet-wifi](https://github.com/intrig-unicamp/mininet-wifi) and drops you into
hands-on labs — recon, handshake capture, cracking, evil twins, WPS attacks and
more — so you can practice real wireless-security techniques without real
hardware, without a lab full of radios, and without touching anyone else's
network.

Brought to you by [Black Hills Information Security](https://www.blackhillsinfosec.com/).

```
                       ▁ ▃ ▅ ▇ █ ▇ ▅ ▃ ▁

       ██╗    ██╗██╗███████╗██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
       ██║    ██║██║██╔════╝██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
       ██║ █╗ ██║██║█████╗  ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
       ██║███╗██║██║██╔══╝  ██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
       ╚███╔███╔╝██║██║     ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
        ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝

                forge wireless attacks in a safe, legal sandbox
```

---

## What's new in 4.0

WifiForge 4.0 is a ground-up refactor:

- **Modern, pretty TUI** — a categorised, searchable menu with difficulty
  ratings, per-lab tool badges, live descriptions, scrolling, and a responsive
  layout that degrades gracefully on small terminals.
- **`pip`-installable** — a proper `pyproject.toml` package with a `wififorge`
  (and short `wf`) command on your `PATH`. No more running a script from a fixed
  directory.
- **Robust lab loading** — each lab is discovered and imported in isolation, so a
  single broken lab can no longer crash the whole menu; it simply shows up
  disabled with the reason why.
- **Browse anywhere** — the menu and `--list` work even on machines without
  mininet-wifi installed, because the heavy dependencies are only imported when a
  lab is actually launched.
- **Drop-in labs** — add your own lab modules without touching the package
  (`--labs-dir` / `$WIFIFORGE_LABS`).

## Requirements

- Linux (tested on Kali/Debian/Ubuntu). Labs need root.
- Python 3.9+
- System tooling installed by `./install-system-deps.sh` — most importantly
  **mininet-wifi**, plus the wireless-security tools the labs drive (aircrack-ng,
  bettercap, john, hashcat, reaver, tmux, and friends).

## Install

```bash
# 1. System dependencies (mininet-wifi + lab tools). Run once, as root.
sudo ./install-system-deps.sh

# 2. The WifiForge package itself.
pip install .
#   …or, to keep it isolated from system Python:
pipx install .
```

For development:

```bash
pip install -e '.[dev]'
```

## Usage

```bash
sudo wififorge            # launch the menu (root required to build networks)
wififorge --list          # list labs and exit (no root / no mininet needed)
wififorge --version
```

Useful flags:

| Flag                 | Purpose                                                            |
| -------------------- | ----------------------------------------------------------------- |
| `--list`             | Print the discovered labs and exit.                               |
| `--labs-dir DIR`     | Also load lab `.py` files from `DIR` (see **Writing a lab**).      |
| `--allow-non-root`   | Skip the root check to browse the menu (labs won't build).        |

### Menu keys

| Key                    | Action                        |
| ---------------------- | ----------------------------- |
| `↑` `↓` / `k` `j`      | Move selection                |
| `PgUp` `PgDn`          | Jump a page                   |
| `Home` `End`          | First / last lab              |
| `Enter`                | Launch the selected lab       |
| `/`                    | Search; `Esc` clears          |
| `q` / `Esc`            | Quit                          |

When a lab launches, WifiForge builds the virtual network and opens a **tmux**
session with one pane per node (the attacker station, target hosts, etc.). Work
through the lab there; when you exit tmux, WifiForge tears the network down and
cleans up.

## Labs

| Lab                              | Category | Difficulty    |
| -------------------------------- | -------- | ------------- |
| Airsuite Recon & Key Discovery   | Recon    | Intermediate  |
| Bettercap Recon                  | Recon    | Beginner      |
| Bettercap Auth Capture           | Capture  | Intermediate  |
| NTLM John Crack                  | Cracking | Beginner      |
| Cracking WPA with Aircrack       | Cracking | Intermediate  |
| Capture to HCCAPX / Hashcat      | Cracking | Advanced      |
| Airgeddon DoS                    | Attack   | Beginner      |
| WEP Attack                       | Attack   | Beginner      |
| Evil Twin                        | Attack   | Intermediate  |
| WPS Pixie Dust                   | Attack   | Advanced      |
| Wifiphisher                      | Phishing | Intermediate  |
| Drone Hacking                    | Misc     | Advanced      |

## Writing a lab

A lab is just a Python module exposing a `LAB` description and a `run()`
function. Drop it in `src/wififorge/labs/` (bundled) or any directory you pass
with `--labs-dir`:

```python
from wififorge.labs._schema import LabMeta, Category, Difficulty
from wififorge.labs._harness import run_lab

LAB = LabMeta(
    title="My Lab",
    category=Category.ATTACK,
    difficulty=Difficulty.INTERMEDIATE,
    tools=("aircrack-ng",),
    summary="One or two sentences describing what the learner will do.",
)

def _topology(net):
    net.addStation("Attacker", wlans=1)
    host1 = net.addStation("host1", passwd="password123", encrypt="wpa2")
    ap1 = net.addAccessPoint("ap1", ssid="MyNet", passwd="password123",
                             encrypt="wpa2", mode="g", channel="1")
    net.configureWifiNodes()
    net.addLink(host1, ap1)
    return [ap1]            # the APs to start

def run():
    run_lab("MY_LAB", ["Attacker", "host1"], _topology)
```

The shared `run_lab` helper handles the build/start/tmux/teardown lifecycle, and
the common multi-network "practice range" used by the recon/capture/cracking labs
is available as `from wififorge.labs._scenarios import standard_range`.

## Development

```bash
pip install -e '.[dev]'
pytest          # unit tests (no root / mininet required)
ruff check .    # lint
mypy src        # type-check
```

## Legal

WifiForge is for **education and authorised testing only**. Every network it
creates is virtual and confined to your machine. Do not use the techniques you
learn here against networks you do not own or do not have explicit permission to
test.

## License

See [LICENSE](LICENSE).
