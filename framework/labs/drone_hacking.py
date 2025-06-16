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
    spin = Halo(text='Loading', spinner='dots')
    spin.start()

    net = Mininet_wifi()

    # configure drone names and passwords here
    dronepass = {
        "dr1": "password!",
        "dr2": "arcangel"
    }
    
    print("Creating Attacker Station...")
    attacker = net.addStation('Attacker', wlans=1)
    
    print("Creating Drones and Controllers...")

    # drone 1 network
    st1 = net.addStation('st1', passwd=dronepass["dr1"], encrypt='wpa2', mac='00:00:00:00:00:01', ip='10.1.0.10/24')
    dr1 = net.addAccessPoint('dr1', ssid='DRONE1', passwd=dronepass["dr1"], encrypt='wpa2', mode='g', channel='3', failMode="standalone")
    
    # drone 2 network
    st2 = net.addStation('st2', passwd=dronepass["dr2"], encrypt='wpa2', mac='00:00:00:00:00:02', ip='10.2.0.10/24')
    dr2 = net.addAccessPoint('dr2', ssid='DRONE2', passwd=dronepass["dr2"], encrypt='wpa2', mode='g', channel='6', failMode="standalone")

    # net.configureWifiNodes()
    net.configureNodes()

    # build out the network
    print('Configuring Network...')
    net.addLink(dr1, st1)
    net.addLink(dr2, st2)
    
    # configure NAT to dr1 and dr2
    nat1 = net.addNAT(name='nat1')
    nat2 = net.addNAT(name='nat2')

    net.addLink(nat1, dr1)
    net.addLink(nat2, dr2)
    
    # LAN address, WAN is applied automatically
    nat1.setIP('10.1.0.254/24', intf='nat1-eth1')
    nat2.setIP('10.2.0.254/24', intf='nat2-eth1')
    
    # configure routing for the stations
    st1.cmd('ip route add default via 10.1.0.254')
    st2.cmd('ip route add default via 10.2.0.254')

    for n in [nat1, nat2]:
        n.cmd('sysctl -w net.ipv4.ip_forward=1')
        n.cmd('iptables -t nat -A POSTROUTING -o nat1-eth0 -j MASQUERADE') 

    net.build()
    dr1.start([])
    dr2.start([])

    # set the drone positions (x, y, z)
    dr1.setPosition('20,20,0')
    dr2.setPosition('10,28,0')

    # userland listener service on port 4444, write the password for the drone
    dr1.cmd('python3 shell.py', dronepass["dr1"], '&')
    dr2.cmd('python3 shell.py', dronepass["dr2"], '&')

    # write drone information for controllers and graph (/tmp/drone-info.json)
    info = {}

    # write ap/drone positions 
    for n in net.aps:
        info[n.name] = {
            "position": [float(x) for x in n.position],
            "password": [dronepass[n.name]]
        }
    print(info)
    with open('/tmp/drone-info.json', 'w') as f:
        json.dump(info, f)

    spin.stop()
    # CLI(net)
    CONFIG_TMUX(["Attacker", "Attacker", "Attacker"], "DRONES")

    print("Stopping Network...")
    net.stop()
    os.system("clear")

    # remove the tmp files (cleanup)
    path = '/tmp/drone-info.json'
    if os.path.exists(path):
        os.remove(path)

if __name__ == '__main__':
    drones()
