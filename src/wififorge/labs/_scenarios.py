"""Reusable network topologies shared by multiple labs.

Five of the labs (recon, capture, and cracking) stood up an identical five-network
"practice range" — roughly 40 duplicated lines each, and the copies had drifted:
some mislabelled stations (two ``host2`` nodes), and several built an AP (``ap4``)
they never started. Defining the range once fixes all of that in a single place.
"""

from __future__ import annotations

from typing import Any


def standard_range(net: Any, attacker_wlans: int = 1) -> list:
    """Build WifiForge's standard multi-network practice range on ``net``.

    Networks created (all co-existing, as a messy real airspace would be):

    * ``WEP_Network``      — legacy WEP, two clients
    * ``WPA2_Network``     — WPA2, two clients (fixed BSSID for reproducible labs)
    * ``Harlow_Home_Wifi`` — WPA2 home network, three clients
    * ``FBI_Van``          — WPA2 decoy, one client
    * ``cantseeme``        — hidden-SSID WPA2, one client

    Plus an ``Attacker`` station with ``attacker_wlans`` radios (one by default).
    Returns the AP list so the caller can ``build()`` then start each one.
    """
    net.addStation("Attacker", wlans=attacker_wlans)

    # --- Legacy WEP network ---------------------------------------------------
    host1 = net.addStation("host1", passwd="123456789a", encrypt="wep")
    host2 = net.addStation("host2", passwd="123456789a", encrypt="wep")
    ap0 = net.addAccessPoint(
        "ap0", ssid="WEP_Network", mode="g", channel="1",
        passwd="123456789a", encrypt="wep", failMode="standalone", datapath="user",
    )

    # --- WPA2 network ---------------------------------------------------------
    host3 = net.addStation("host3", passwd="december2022", encrypt="wpa2")
    host4 = net.addStation("host4", passwd="december2022", encrypt="wpa2")
    ap1 = net.addAccessPoint(
        "ap1", ssid="WPA2_Network", passwd="december2022", encrypt="wpa2",
        mode="g", channel="6", mac="76:df:71:67:40:2b",
    )

    # --- Home network ---------------------------------------------------------
    host5 = net.addStation("host5", passwd="password", encrypt="wpa2")
    host6 = net.addStation("host6", passwd="password", encrypt="wpa2")
    host7 = net.addStation("host7", passwd="password", encrypt="wpa2")
    ap2 = net.addAccessPoint(
        "ap2", ssid="Harlow_Home_Wifi", passwd="password", encrypt="wpa2",
        mode="g", channel="11",
    )

    # --- Decoy network --------------------------------------------------------
    host8 = net.addStation("host8", passwd="supersecurepassword", encrypt="wpa2")
    ap3 = net.addAccessPoint(
        "ap3", ssid="FBI_Van", passwd="supersecurepassword", encrypt="wpa2",
        mode="g", channel="1",
    )

    # --- Hidden SSID ----------------------------------------------------------
    host9 = net.addStation("host9", passwd="iamhidden", encrypt="wpa2")
    ap4 = net.addAccessPoint(
        "ap4", ssid="cantseeme", passwd="iamhidden", encrypt="wpa2",
        mode="g", channel="11",
    )

    net.configureWifiNodes()

    net.addLink(host1, ap0)
    net.addLink(host2, ap0)
    net.addLink(host3, ap1)
    net.addLink(host4, ap1)
    net.addLink(host5, ap2)
    net.addLink(host6, ap2)
    net.addLink(host7, ap2)
    net.addLink(host8, ap3)
    net.addLink(host9, ap4)

    return [ap0, ap1, ap2, ap3, ap4]
