from mininet.net import Mininet
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from halo import Halo
from framework.helper_functions.CONNECT_TMUX import CONFIG_TMUX
from halo import Halo
import os

description = """This lab demonstrates the creation of an Evil Twin access point to impersonate a legitimate network, with the goal of harvesting client credentials or injecting malicious content."""

def EVIL_TWIN():
	spin = Halo(text='Loading', spinner='dots')
	spin.start()

	net = Mininet_wifi()

	print("Creating Stations...")
	host1 = net.addStation('Attacker', passwd='JERRY277626AA', encrypt='wpa2', wlans=2)
	host2 = net.addStation('host1', passwd='JERRY277626AA', encrypt='wpa2', wlans=2)

	print("Creating Access Point...")
	ap1 = net.addAccessPoint('ap1', ssid="CORP_NET", mode='g', channel='1', passwd="JERRY277626AA", encrypt="wpa2")
	net.configureWifiNodes()

	print('Adding Stations')
	net.addLink(host1, ap1)
	net.addLink(host2, ap1)

	net.build()
	ap1.start([])
	spin.stop()
	CONFIG_TMUX(["Attacker"], "EVIL_TWIN")
	spin.start()
	net.stop()
	spin.stop()
	os.system("clear")


