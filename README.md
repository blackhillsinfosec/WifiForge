<a name="top"></a>
<div align="center">

<a href="https://github.com/blackhillsinfosec/WifiForge">
  <img width="78%" src="images/logo-wf.jpg" alt="WifiForge" />
</a>

### A complete WiFi hacking lab - virtual, sandboxed, no radio required.

<samp>mininet-wifi virtual networks in software · spin up a wireless-attack lab with a single command</samp>

<br>
<br>

<img src="https://img.shields.io/badge/license-Apache_2.0-D22128?style=for-the-badge" alt="License" />
<img src="https://img.shields.io/badge/python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux" />
<br>
<img src="https://img.shields.io/badge/radio-mininet--wifi_·_mac80211__hwsim-00857C?style=for-the-badge" alt="mininet-wifi" />
<img src="https://img.shields.io/badge/ui-blessed_·_tmux-FF6600?style=for-the-badge" alt="blessed" />
<img src="https://img.shields.io/badge/install-pip_·_pyproject-2496ED?style=for-the-badge&logo=python&logoColor=white" alt="pip" />
<a href="https://discord.com/invite/bhis"><img src="https://img.shields.io/discord/967097582721572934?style=for-the-badge&logo=discord&logoColor=white&label=discord&color=5865F2" alt="Discord" /></a>

<br>
<br>

<a href="#overview"><b>Overview</b></a> &nbsp;·&nbsp;
<a href="https://wififorge.github.io/"><b>Lab Walkthroughs</b></a> &nbsp;·&nbsp;
<a href="#how-it-works"><b>How It Works</b></a> &nbsp;·&nbsp;
<a href="#quick-start"><b>Quick Start</b></a> &nbsp;·&nbsp;
<a href="#writing-labs"><b>Writing Labs</b></a> &nbsp;·&nbsp;
<a href="#labs"><b>Labs</b></a> &nbsp;·&nbsp;
<a href="#requirements"><b>Requirements</b></a> &nbsp;·&nbsp;
<a href="#safety-and-legal-use"><b>Safety</b></a>

</div>

---

## Overview

**WifiForge** is a terminal-driven framework for building **fully virtual** WiFi networks for security research and training. It gives you a safe, legal, sandboxed place to practice real wireless attacks, recon, handshake capture, cracking, evil twins, WPS, and more, without any of the usual setup.

Traditional wireless practice means adapters that support monitor mode and injection, spare access points, antennas, and a space where it's legal to transmit. WifiForge removes all of it: the radios are [mininet-wifi](https://github.com/intrig-unicamp/mininet-wifi) virtual interfaces (`mac80211_hwsim`), so an entire airspace, access points, client stations, and your attacker, runs in software with nothing sent over the air. Pick a lab from the menu, and WifiForge builds the network, drops you into a per-node terminal, and lets you run the attack hands-on.

> [!NOTE]
> WifiForge creates only virtual networks confined to your machine. Use it only in environments you own or are explicitly authorized to test.

<br>

<table>
<tr>
<td align="center" width="33%">📡<br><br><b>No hardware</b><br>No WiFi adapter, access point, antenna, or RF — the radios are mininet-wifi's virtual <code>mac80211_hwsim</code> interfaces.</td>
<td align="center" width="33%">📦<br><br><b>pip-installable</b><br>A proper <code>pyproject.toml</code> package puts <code>wififorge</code> (and a short <code>wf</code>) on your PATH.</td>
<td align="center" width="33%">📝<br><br><b>Labs as modules</b><br>A lab is a small Python file; drop it in and WifiForge discovers and lists it automatically.</td>
</tr>
<tr>
<td align="center" width="33%">🖥️<br><br><b>Beautiful menu</b><br>A categorised, searchable terminal UI with difficulty ratings, tool badges, and live descriptions.</td>
<td align="center" width="33%">🧩<br><br><b>Robust loading</b><br>Each lab is imported in isolation, so one broken lab can't take down the menu — it just shows disabled.</td>
<td align="center" width="33%">🔬<br><br><b>See the attack</b><br>Work node-by-node in tmux and watch recon, capture, cracking, and rogue-AP attacks unfold.</td>
</tr>
</table>

---

## Quick Start

WifiForge needs a **Linux host** with mininet-wifi and the wireless tooling the labs drive. Clone the repo, install the system dependencies once, then install the launcher:

```bash
git clone https://github.com/blackhillsinfosec/WifiForge.git
cd WifiForge

# System dependencies (mininet-wifi + lab tools). Run once, as root.
sudo ./install-system-deps.sh

# The WifiForge package itself.
pip install .            # or, to keep it isolated:  pipx install .
```

Launch the menu, pick a lab, and press <kbd>Enter</kbd>:

```bash
sudo wififorge           # or:  sudo python3 -m wififorge
```

Navigate with <kbd>↑</kbd> <kbd>↓</kbd> (or <kbd>j</kbd>/<kbd>k</kbd>) &nbsp;·&nbsp; launch with <kbd>Enter</kbd> &nbsp;·&nbsp; search with <kbd>/</kbd> &nbsp;·&nbsp; quit with <kbd>q</kbd>.

> [!TIP]
> You can browse without root or even without mininet installed: `wififorge --list` prints every discovered lab, and `wififorge --allow-non-root` opens the menu for browsing (labs won't build). Root is only needed to actually create the virtual network.

> [!IMPORTANT]
> The **first run builds mininet-wifi**, which compiles components from source and can take several minutes. Later runs are cached. Labs create network namespaces and interfaces, so launching one requires `sudo`.

<div align="right"><a href="#top"><sub>▲ back to top</sub></a></div>

---

## Writing Labs

A lab is a small Python module in `labs/`, discovered automatically at startup. You declare its metadata and a `run()` entry point; the shared harness handles the build → start → tmux → teardown lifecycle for you.

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
    return [ap1]                         # the APs to start

def run():
    run_lab("MY_LAB", ["Attacker", "host1"], _topology)
```

| Piece | What it does |
| :-- | :-- |
| `LAB = LabMeta(...)` | Title, category, difficulty, and tools shown in the menu |
| `run()` | The entry point WifiForge calls when the lab is launched |
| `run_lab(name, panes, topology)` | Builds the network, opens a tmux pane per node, tears down after |
| `standard_range(net)` | Import from `_scenarios` to reuse the shared multi-network practice range |

Drop the file in `src/wififorge/labs/` to bundle it, or point WifiForge at an external directory with `--labs-dir DIR` (or `$WIFIFORGE_LABS`) — no reinstall needed. A lab that fails to import doesn't crash the menu; it appears disabled with the reason why.

<div align="right"><a href="#top"><sub>▲ back to top</sub></a></div>

---

## Labs

| Lab | Category | Difficulty |
| :-- | :-- | :-- |
| Airsuite Recon & Key Discovery | Recon | ●●○ Intermediate |
| Bettercap Recon | Recon | ●○○ Beginner |
| Bettercap Auth Capture | Capture | ●●○ Intermediate |
| NTLM John Crack | Cracking | ●○○ Beginner |
| Cracking WPA with Aircrack | Cracking | ●●○ Intermediate |
| Capture to HCCAPX / Hashcat | Cracking | ●●● Advanced |
| Airgeddon DoS | Attack | ●○○ Beginner |
| WEP Attack | Attack | ●○○ Beginner |
| Evil Twin | Attack | ●●○ Intermediate |
| WPS Pixie Dust | Attack | ●●● Advanced |
| Wifiphisher | Phishing | ●●○ Intermediate |
| Drone Hacking | Misc | ●●● Advanced |

<details>
<summary><b>Command-line usage</b></summary>

<br>

The install provides `wififorge` and the short alias `wf`:

| Command | Purpose |
| :-- | :-- |
| `sudo wififorge` | Launch the lab menu |
| `wififorge --list` | Print discovered labs and exit (no root / no mininet needed) |
| `wififorge --labs-dir DIR` | Also load lab `.py` files from `DIR` |
| `wififorge --allow-non-root` | Skip the root check to browse the menu |
| `wififorge --version` | Show the version |

</details>

<details>
<summary><b>Project layout</b></summary>

<br>

```text
WifiForge/
├── pyproject.toml              # project metadata, dependencies, entry points, tooling
├── install-system-deps.sh      # apt packages + mininet-wifi (the non-pip parts)
├── src/wififorge/              # the Python package
│   ├── __init__.py             #   centralised version
│   ├── __main__.py             #   `python -m wififorge` -> lab menu
│   ├── cli.py                  #   argparse entry point + lab launch
│   ├── banner.py               #   ASCII logo + render helpers
│   ├── theme.py                #   capability-aware colour palette
│   ├── runtime.py              #   root check, FD-limit fix, mininet cleanup
│   ├── tmux.py                 #   one tmux pane per node (nsenter)
│   ├── labs/                   #   drop-in labs, auto-discovered
│   │   ├── _schema.py          #     LabMeta + Category/Difficulty
│   │   ├── _harness.py         #     build/start/tmux/teardown lifecycle
│   │   ├── _scenarios.py       #     shared practice-range topology
│   │   ├── loader.py           #     isolated, lazy lab discovery
│   │   ├── materials/          #     bundled wordlists, captures, helper scripts
│   │   └── *.py                #     the 12 labs
│   └── tui/                    #   the terminal UI
│       ├── geometry.py         #     responsive layout math
│       ├── widgets.py          #     rounded boxes, badges, wrapping
│       └── menu.py             #     the searchable, categorised menu
└── tests/                      # unit tests (no root / mininet required)
```

</details>

<div align="right"><a href="#top"><sub>▲ back to top</sub></a></div>

---

## Requirements

Because the radios are virtual, there is **no hardware to buy**.

| Component | Needed |
| :-- | :-- |
| **Host** | Linux — mininet-wifi uses `mac80211_hwsim`, network namespaces, and `NET_ADMIN` (macOS/Windows can't provide these) |
| **mininet-wifi** | Installed by `./install-system-deps.sh`, along with the lab tooling |
| **Tooling** | aircrack-ng, bettercap, john, hashcat/hcxtools, reaver/bully, hostapd, tmux, and friends |
| **Python** | 3.9 or newer (for the launcher) |
| **Privileges** | `sudo` to build networks; browsing the menu / `--list` needs neither root nor mininet |
| **Hardware** | None — no WiFi adapter, access point, antenna, or RF |

<div align="right"><a href="#top"><sub>▲ back to top</sub></a></div>

---

## Safety and Legal Use

> [!WARNING]
> **WifiForge is for authorized security research and education only.** The techniques you learn here apply to real wireless networks — use them only on networks, devices, and clients you own or are explicitly authorized to test. Never interfere with networks you don't have permission to touch.

> [!NOTE]
> **WifiForge does not transmit RF.** The entire radio path is mininet-wifi's `mac80211_hwsim` virtual interfaces running on your machine, so there is no spectrum use and nothing is sent over the air — the lab itself is safe and legal to run on your own computer.

---

## Troubleshooting

<details>
<summary><b>Common issues</b></summary>

<br>

| Symptom | Fix |
| :-- | :-- |
| `WifiForge must be run as root` | Launch with `sudo wififorge`; or `--allow-non-root` to browse only |
| `'mn' (mininet) was not found` | Run `sudo ./install-system-deps.sh` first |
| A lab shows as *failed to load* | Open it to see the import error; usually a missing system tool — select another or fix the dependency |
| `Terminal too small` | Enlarge the window; the menu needs a little room and will redraw as it grows |
| A lab hangs on "Building" | On high-ulimit distros this is the FD-limit issue WifiForge caps automatically; make sure you're on the current version |
| Won't run on macOS / Windows | Use a Linux host — `mac80211_hwsim` and network namespaces are required |

When opening an issue, please include your OS, Python and mininet-wifi versions, the WifiForge commit, your install method, relevant logs (e.g. a lab's failure output), and steps to reproduce.

</details>

---

## Development

```bash
pip install -e '.[dev]'
pytest          # unit tests — run headlessly, no root or mininet needed
ruff check .    # lint
mypy src        # type-check
```

The menu renders as a pure function of state and terminal size, and the labs import mininet lazily, so the whole test suite runs on any machine without root or mininet-wifi.

---

## Contributing

Contributions are welcome — a new lab can be as small as a single Python file.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test them in an isolated environment.
5. Open a pull request.

For larger changes, opening an issue first helps coordinate development.

---

## References

<div align="center">

[**WifiForge**](https://github.com/blackhillsinfosec/WifiForge) &nbsp;·&nbsp;
[**mininet-wifi**](https://github.com/intrig-unicamp/mininet-wifi) &nbsp;·&nbsp;
[**Black Hills InfoSec**](https://www.blackhillsinfosec.com/) &nbsp;·&nbsp;
[**tmux**](https://github.com/tmux/tmux) &nbsp;·&nbsp;
[**Aircrack-ng**](https://www.aircrack-ng.org/)

<br>

<sub>Made with ❤️ by <b>Black Hills Information Security</b></sub>

<br>

<a href="#top"><sub>▲ back to top</sub></a>

</div>
