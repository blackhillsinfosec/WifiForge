from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.telemetry import telemetry

from framework.helper_functions.CONNECT_TMUX import CONFIG_TMUX
from halo import Halo
import os
import plotext as plt
import time

description = """scoobert doobert (will fill this in later)"""

def drones():
    spin = Halo(text='Loading', spinner='dots')
    spin.start()

    net = Mininet_wifi()

    print("Creating Drones...")
    attacker = net.addStation('attacker', wlans=1) 
    dr1 = net.addStation('dr1', mac='00:00:00:00:00:01', ip='10.0.0.1/8')
    dr2 = net.addStation('dr2', mac='00:00:00:00:00:02', ip='10.0.0.2/8')
    dr3 = net.addStation('dr3', mac='00:00:00:00:00:03', ip='10.0.0.3/8')

    # creates mesh adhoc network - one SSID, three clients
    net.configureNodes()
    net.addLink(dr1, cls=adhoc, intf='dr1-wlan0', ssid='DRONES', proto='batman_adv', mode='g', channel=1, ht_cap='HT40+')
    net.addLink(dr2, cls=adhoc, intf='dr2-wlan0', ssid='DRONES', proto='batman_adv', mode='g', channel=1, ht_cap='HT40+')
    net.addLink(dr3, cls=adhoc, intf='dr3-wlan0', ssid='DRONES', proto='batman_adv', mode='g', channel=1, ht_cap='HT40+')

    # ap1 = net.addAccessPoint('ap1', ssid='DRONE1', encrypt='opn', mode='g', channel='1')
    # ap2 = net.addAccessPoint('ap2', ssid='DRONE2', passwd='Password1!', encrypt='wpa2', mode='g', channel='5')

    print("Starting Network...")
    net.build()

    attacker.setPosition('0,0,0')
    dr1.setPosition('20,20,0')  # x, y, z
    dr2.setPosition('10,28,0')
    dr3.setPosition('4,15,0')
    
    spin.stop()
    CONFIG_TMUX(["Attacker", "Attacker", "Graph"], "UAV")

    nodes = list(net.stations)
    graph(nodes)

    net.stop()
    os.system("clear")

def graph(nodes):
    while True:
        x_vals = [n.position[0] for n in nodes]
        y_vals = [n.position[1] for n in nodes]

        # graph type and other stuff
        plt.clear_figure()
        plt.scatter(x_vals, y_vals, marker="x", color="cyan")

        # graph X and Y max values
        plt.xlim(0, 30)
        plt.ylim(0, 30)
        
        # axes labels
        plt.title("Drone Tracker")
        plt.xlabel("X position")
        plt.ylabel("Y position")
        
        # load the graph
        plt.show()
        time.sleep(1)

if __name__ == '__main__':
    drones()
