# stop airmon-ng
airmon-ng stop wlan0mon

# restore the Attacker-wlan0 interface
ip link set wlan0 down
ip link set wlan0 name Attacker-wlan0
ip link set Attacker-wlan0 up

# restore the Attacker-wlan1 interface
ip addr flush dev Attacker-wlan1
ip link set Attacker-wlan1 down
ip link set Attacker-wlan1 up

# connect to DRONE1 via wpa supplicant
cat > /tmp/attacker.conf <<EOF
network={
    ssid="DRONE1"
    psk="password!"
}
EOF
wpa_supplicant -B -i Attacker-wlan1 -c /tmp/attacker.conf

# configure routes for DRONE1 network
ip addr add 10.0.0.1/8 dev Attacker-wlan1
