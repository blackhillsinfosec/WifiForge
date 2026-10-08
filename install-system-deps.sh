#!/usr/bin/env bash
#
# Install the *system* dependencies WifiForge needs: the wireless-security
# tooling the labs drive, mininet-wifi (which is not a pip package), and the
# airgeddon build used by the Airgeddon DoS lab.
#
# The Python side is installed separately with `pip install .`.
#
# Safe to re-run: packages that are already installed are left alone (no
# upgrades), and mininet-wifi is only built if it isn't already importable.
# The WifiForge Docker image runs this same script at build time.
#
# Tested on Kali. Debian/Ubuntu work too, but some lab tools (wifiphisher,
# bettercap, mdk4) only ship in Kali's repositories. Run as root.

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

export DEBIAN_FRONTEND=noninteractive
MININET_WIFI_DIR="${MININET_WIFI_DIR:-/opt/mininet-wifi}"
AIRGEDDON_DIR="${AIRGEDDON_DIR:-/opt/airgeddon-WifiForge-Cloud}"
AIRGEDDON_REPO="https://github.com/JsphByd/airgeddon-WifiForge-Cloud.git"

# Install only what's missing; never upgrade packages that are already there
# (the Docker base image ships a tuned mininet-wifi toolchain).
apt_install() {
    apt-get install -y --no-install-recommends --no-upgrade "$@"
}

echo "[*] Updating package lists..."
apt-get update -y

echo "[*] Installing core tooling and build prerequisites..."
apt_install \
    git ca-certificates build-essential python3 python3-pip python3-venv \
    ifupdown iw iproute2 net-tools wireless-tools rfkill \
    pciutils procps gawk \
    tmux \
    aircrack-ng \
    hashcat hcxtools \
    john \
    reaver bully pixiewps \
    hostapd wpasupplicant \
    iperf \
    dsniff ettercap-text-only \
    openvswitch-switch openvswitch-common openvswitch-testcontroller

# Tools that some distros don't package. Each is tried on its own so one
# missing package doesn't stop the rest; the labs that need them are noted.
echo "[*] Installing lab tools..."
missing=()
for pkg in \
    bettercap:"Bettercap Recon, Bettercap Auth Capture" \
    mdk4:"Airgeddon DoS" \
    wifiphisher:"Wifiphisher" \
    chromium:"Capture to HCCAPX / Hashcat, Wifiphisher (browser)" \
    hashcat-utils:"Capture to HCCAPX / Hashcat"
do
    name="${pkg%%:*}"
    if ! apt_install "${name}" >/dev/null 2>&1; then
        missing+=("${name} (${pkg#*:})")
    fi
done

if python3 -c "import mn_wifi" >/dev/null 2>&1 && command -v mn >/dev/null 2>&1; then
    echo "[*] mininet-wifi is already installed, skipping."
else
    echo "[*] Installing mininet-wifi into ${MININET_WIFI_DIR} (this can take a while)..."
    if [[ ! -d "${MININET_WIFI_DIR}" ]]; then
        git clone https://github.com/intrig-unicamp/mininet-wifi "${MININET_WIFI_DIR}"
    fi
    pushd "${MININET_WIFI_DIR}" >/dev/null
    # -W wireless deps, -l wmediumd, -n mininet core.
    util/install.sh -Wln
    popd >/dev/null
fi

echo "[*] Installing airgeddon (WifiForge build) into ${AIRGEDDON_DIR}..."
if [[ -d "${AIRGEDDON_DIR}/.git" ]]; then
    git -C "${AIRGEDDON_DIR}" pull --ff-only || echo "[!] Could not update airgeddon; keeping existing copy."
else
    git clone --depth 1 "${AIRGEDDON_REPO}" "${AIRGEDDON_DIR}"
fi
# Keep airgeddon from replacing the WifiForge build with upstream on launch.
if [[ -f "${AIRGEDDON_DIR}/.airgeddonrc" ]]; then
    sed -i 's/^AIRGEDDON_AUTO_UPDATE=.*/AIRGEDDON_AUTO_UPDATE=false/' "${AIRGEDDON_DIR}/.airgeddonrc"
fi
chmod +x "${AIRGEDDON_DIR}/airgeddon.sh"
ln -sf "${AIRGEDDON_DIR}/airgeddon.sh" /usr/local/bin/airgeddon

cat <<'MSG'

[+] System dependencies installed.

Next:
    sudo pip install --break-system-packages .
    sudo wififorge
MSG

if (( ${#missing[@]} )); then
    echo
    echo "[!] These packages aren't available on this distro, so these labs won't fully work:"
    printf '      %s\n' "${missing[@]}"
fi
