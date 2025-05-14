from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from framework.helper_functions.CONNECT_TMUX import CONFIG_TMUX
import threading
import time
from halo import Halo
import os

description = """This lab uses Wifiphisher to carry out phishing-based attacks on Wi-Fi clients by creating rogue APs and tricking users into entering credentials or installing malware."""

def WIFIPHISHER():
    spin = Halo(text='Loading', spinner='dots')
    spin.start()
    net = Mininet_wifi()

    print('Creating Stations...')
    attacker = net.addStation('Attacker', wlans=2,passwd='december2022', encrypt='wpa2')
    host1 = net.addStation('host1', passwd='december2022', encrypt='wpa2')
    host2 = net.addStation('host2', passwd='december2022', encrypt='wpa2')

    print('Creating the Access Point...')
    ap = net.addAccessPoint('ap1', ssid='mywifi', passwd='december2022', encrypt='wpa2', mode='g', channel='6')
    net.configureWifiNodes()

    print('Adding Stations...')
    net.addLink(attacker,ap)
    net.addLink(host1, ap)
    net.addLink(host2, ap)

    net.build()
    ap.start([])
    spin.stop()
    CONFIG_TMUX(["Attacker", "host1"], "WIFIPHISHER")
    spin.start()
    net.stop()
    spin.stop()
    os.system("ps aux | grep 'wifiphisher' | awk '{print $2}' | xargs -I {} kill -9 {}")
    
