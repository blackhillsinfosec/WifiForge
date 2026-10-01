#!/usr/bin/env bash
#
# Install the *system* dependencies WifiForge needs: the wireless-security
# tooling the labs drive, plus mininet-wifi (which is not a pip package).
#
# The Python side is installed separately with `pip install .` — this script no
# longer touches your global pip configuration the way the old setup.sh did.
#
# Tested on Kali / Debian / Ubuntu. Run as root.

set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "Please run as root: sudo ./install-system-deps.sh" >&2
    exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
    echo "This installer targets apt-based distros (Kali/Debian/Ubuntu)." >&2
    echo "Install the equivalent packages for your distro, then 'pip install .'." >&2
    exit 1
fi

MININET_WIFI_DIR="${MININET_WIFI_DIR:-/opt/mininet-wifi}"

echo "[*] Updating package lists..."
apt-get update -y

echo "[*] Installing wireless-security tooling and build prerequisites..."
# Grouped by purpose for readability; adjust to taste.
apt-get install -y --no-install-recommends \
    git build-essential python3 python3-pip python3-venv \
    ifupdown iw iproute2 net-tools wireless-tools rfkill \
    tmux \
    aircrack-ng \
    bettercap \
    hashcat hashcat-utils hcxtools \
    john \
    reaver bully pixiewps \
    hostapd wpasupplicant \
    dsniff ettercap-text-only \
    openvswitch-switch openvswitch-common

echo "[*] Installing mininet-wifi into ${MININET_WIFI_DIR}..."
if [[ ! -d "${MININET_WIFI_DIR}" ]]; then
    git clone https://github.com/intrig-unicamp/mininet-wifi "${MININET_WIFI_DIR}"
fi
pushd "${MININET_WIFI_DIR}" >/dev/null
# -W installs mininet-wifi and its wmediumd dependency.
util/install.sh -Wln
popd >/dev/null

cat <<'EOF'

[+] System dependencies installed.

Next:
    pip install .          # or: pipx install .
    sudo wififorge         # launch the menu

EOF
