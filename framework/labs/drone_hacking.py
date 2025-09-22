from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.telemetry import telemetry

from framework.helper_functions.CONNECT_TMUX import CONFIG_TMUX
from halo import Halo
import os
import json

description = """This lab demonstrates wireless drone hacking and compromise."""

def drones():
    spin = Halo(text='Loading', spinner='dots', color='clear')
    spin.start()

    net = Mininet_wifi()

    # configure drone information here, retrieve the information when setting up
    drones = {
        "dr1": {                                # drone name
            "position": [20.0, 20.0, 0.0],      # x, y, z coordinates for the drone
            "password": "password!",            # password for the drone
            "listener": "10.1.0.254",           # IP address for the service listener on the NAT interface
            "port":     "4441"                  # port for the service listener on the NAT interface
        },
        "dr2": {
            "position": [10.0, 28.0, 0.0],
            "password": "arcangel",
            "listener": "10.2.0.254",
            "port":     "4442"
        }
    }
    
    attacker = net.addStation('Attacker', wlans=2)

    # drone 1 network
    st1 = net.addStation('st1', passwd=drones["dr1"]["password"], encrypt='wpa2', mac='00:00:00:00:00:01', ip='10.1.0.10/24')
    dr1 = net.addAccessPoint('dr1', ssid='DRONE1', passwd=drones["dr1"]["password"], encrypt='wpa2', mode='g', channel='3', failMode="standalone")
    
    # drone 2 network
    st2 = net.addStation('st2', passwd=drones["dr2"]["password"], encrypt='wpa2', mac='00:00:00:00:00:02', ip='10.2.0.10/24')
    dr2 = net.addAccessPoint('dr2', ssid='DRONE2', passwd=drones["dr2"]["password"], encrypt='wpa2', mode='g', channel='6', failMode="standalone")

    # net.configureWifiNodes()
    net.configureNodes()

    # build out the network
    net.addLink(dr1, st1)
    net.addLink(dr2, st2)

    net.addLink(attacker, dr1)
    net.addLink(attacker, dr2)
    
    # configure NAT to dr1 and dr2
    nat1 = net.addNAT(name='nat1')
    nat2 = net.addNAT(name='nat2')

    net.addLink(nat1, dr1)
    net.addLink(nat2, dr2)
    
    # LAN address, WAN is applied automatically
    nat1.setIP(drones["dr1"]["listener"]+'/24', intf='nat1-eth1')
    nat2.setIP(drones["dr2"]["listener"]+'/24', intf='nat2-eth1')
    for n in [nat1, nat2]:
        n.cmd('sysctl -w net.ipv4.ip_forward=1')
        n.cmd('iptables -t nat -A POSTROUTING -o nat1-eth0 -j MASQUERADE')

    # configure routing for the stations
    st1.cmd(f'ip route add default via {drones["dr1"]["listener"]}')
    st2.cmd(f'ip route add default via {drones["dr2"]["listener"]}')

    net.build()
    dr1.start([])
    dr2.start([])

    # set the drone positions (x, y, z)
    x, y, z = drones["dr1"]["position"]
    dr1.setPosition(f'{x},{y},{z}')

    x, y, z = drones["dr2"]["position"]
    dr2.setPosition(f'{x},{y},{z}')

    # userland listener service on associated port, write the password for the drone
    basedir = os.path.dirname(os.path.abspath(__file__))                                    # path for drone_hacking.py (WifiForge/framework/labs/drone_hacking.py)
    shellpath = os.path.join(basedir, '..', 'lab_materials', 'shell.py')                    # path for shell.py (../lab_materials/shell.py)

    dr1.cmd(f"python3 {shellpath} {drones["dr1"]["password"]} {drones["dr1"]["port"]} &")   # run the shell for dr1
    dr2.cmd(f"python3 {shellpath} {drones["dr2"]["password"]} {drones["dr2"]["port"]} &")   # run the shell for dr2

    # output to config file
    with open('/tmp/drone-info.json', 'w') as f:
        json.dump(drones, f)

    spin.stop()
    # CLI(net)
    CONFIG_TMUX(["Attacker", "Attacker", "Attacker"], "DRONES")

    # cleanup
    spin.start()
    net.stop()
    os.system("clear")
    spin.start()

    path = '/tmp/drone-info.json'
    if os.path.exists(path):
        os.remove(path)

if __name__ == '__main__':
    drones()
