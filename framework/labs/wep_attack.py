from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from framework.helper_functions.CONNECT_TMUX import CONFIG_TMUX
from time import sleep
from WifiForge import print_banner
from halo import Halo
import os

description = """This lab demonstrates how to exploit vulnerabilities in WEP encryption using tools like aireplay-ng and aircrack-ng to capture IVs and recover the network key."""

def WEP_ATTACK():

    # BUILD NETWORK 
    spin = Halo(text='Loading', spinner='dots', color='red')
    spin.start()

    net = Mininet_wifi()

    print("Creating Stations...")
    attacker = net.addStation('Attacker', passwd='123456789a', encrypt='wep', wlans=2)
    host1 = net.addStation('host1', passwd='123456789a', encrypt='wep')
    host2 = net.addStation('host2', passwd='123456789a', encrypt='wep')
    ap1 = net.addAccessPoint('ap1', ssid="WEP_NETWORK", mode="g", channel="6",
                             passwd='123456789a', encrypt='wep',
                             failMode="standalone", datapath='user')

    print("Creating the Access Point...")
    net.configureWifiNodes()

    print("Adding Stations...")
    net.addLink(host1, ap1)
    net.addLink(host2, ap1)

    net.build()
    ap1.start([])
    spin.stop()
    CONFIG_TMUX(['Attacker', 'host1', 'host2'], "WEP_ATTACK")

    #KILL LAB
    spin.start()
    net.stop()
    spin.stop()
    os.system('clear')
