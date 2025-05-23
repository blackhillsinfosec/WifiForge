from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.telemetry import telemetry

from framework.helper_functions.CONNECT_TMUX import CONFIG_TMUX
from halo import Halo
import os

description = """scoobert doobert (will fill this in later)"""

def DRONES():
    spin = Halo(text='Loading', spinner='dots')
    spin.start()

    net = Mininet_wifi()

    print("Creating Drones...")
    attacker = net.addStation('Attacker', wlans=1) 

    dr1 = net.addStation('dr1', mac='00:00:00:00:00:01', ip='10.0.0.1/8', position='30,60,0')
    dr2 = net.addStation('dr2', mac='00:00:00:00:00:02', ip='10.0.0.2/8', position='70,30,0')
    dr3 = net.addStation('dr3', mac='00:00:00:00:00:03', ip='10.0.0.3/8', position='10,20,0')

    net.configureNodes()
    net.addLink(dr1, cls=adhoc, intf='dr1-wlan0', ssid='DRONES', proto='batman_adv', mode='g', channel=1, ht_cap='HT40+')
    net.addLink(dr2, cls=adhoc, intf='dr2-wlan0', ssid='DRONES', proto='batman_adv', mode='g', channel=1, ht_cap='HT40+')
    net.addLink(dr3, cls=adhoc, intf='dr3-wlan0', ssid='DRONES', proto='batman_adv', mode='g', channel=1, ht_cap='HT40+')

    print("Starting network...")
    net.build() 
  
    spin.stop()
    CONFIG_TMUX(["Attacker", "Attacker"], "UAV")

    # when user exits CLI:
    net.stop()
    os.system("clear")

if __name__ == '__main__':
    DRONES()
