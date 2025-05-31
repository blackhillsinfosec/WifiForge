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
        "dr2": "arcangel",
        "dr3": "letmein",
    }
    
    print("Creating Attacker Station...")
    attacker = net.addStation('Attacker', wlans=1)
    
    print("Creating Drones and Controllers...")

    # drone 1 network
    cr1 = net.addStation('cr1', passwd=dronepass["dr1"], encrypt='wpa2', mac='00:00:00:00:00:01')
    dr1 = net.addAccessPoint('dr1', ssid='DRONE1', passwd=dronepass["dr1"], encrypt='wpa2', mode='g', channel='3')

    # drone 2 network
    cr2 = net.addStation('cr2', passwd=dronepass["dr2"], encrypt='wpa2', mac='00:00:00:00:00:02')
    dr2 = net.addAccessPoint('dr2', ssid='DRONE2', passwd=dronepass["dr2"], encrypt='wpa2', mode='g', channel='6')

    # drone 3 network
    cr3 = net.addStation('cr3', passwd=dronepass["dr3"], encrypt='wpa2', mac='00:00:00:00:00:03')
    dr3 = net.addAccessPoint('dr3', ssid='DRONE3', passwd=dronepass["dr3"], encrypt='wpa2', mode='g', channel='11')

    net.configureWifiNodes()

    # build out the network 
    print('Configuring Network...')
    net.addLink(cr1, dr1)
    net.addLink(cr2, dr2)
    net.addLink(cr3, dr3)

    net.build()
    dr1.start([])
    dr2.start([])
    dr3.start([])

    # set the drone positions (x, y, z)
    dr1.setPosition('20,20,0')
    dr2.setPosition('10,28,0')
    dr3.setPosition('4,15,0')
    
    # write the drone names and positions to a JSON dictionary (/tmp/drone_positions.json)
    positions = {}
    for n in net.aps:
        positions[n.name] = [float(x) for x in n.position]
    with open('/tmp/drone_positions.json', 'w') as f:
        json.dump(positions, f)

    # write the drone passwords to a JSON dictionary (/tmp/drone_passwords.json)
    passwords = {}
    for n in net.aps:
        if n.name in dronepass:
            passwords[n.name] = [dronepass[n.name]]
    with open('/tmp/drone_passwords.json', 'w') as f:
        json.dump(passwords, f)
    
    spin.stop()
    CONFIG_TMUX(["Attacker", "Attacker", "Attacker"], "DRONES")

    net.stop()
    os.system("clear")

    # remove the tmp files (cleanup)
    for path in ['/tmp/drone_positions.json', '/tmp/drone_passwords.json']:
        if os.path.exists(path):
            os.remove(path)

if __name__ == '__main__':
    drones()
