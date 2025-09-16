from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from framework.helper_functions.CONNECT_TMUX import CONFIG_TMUX
from halo import Halo
import os

description = """This lab involves cracking NTLM password hashes using John the Ripper, illustrating common techniques for offline Windows hash cracking."""

def NTLM_JOHN_CRACK():
	spin = Halo(text='Loading', spinner='dots', color='red')
	spin.start()
	net = Mininet_wifi()

	print("Creating Stations...")
	host1 = net.addStation('Attacker', passwd='JERRY277626AA', encrypt='wpa2', wlans=2)
	host2 = net.addStation('host1', passwd='JERRY277626AA', encrypt='wpa2', wlans=2)

	print("Creating Access Point...")
	ap1 = net.addAccessPoint('ap1', ssid="CORP_NET", mode='g', channel='1', passwd="JERRY277626AA", encrypt="wpa2")
	c0 = net.addController('c0')
	net.configureWifiNodes()

	print('Adding Stations')
	net.addLink(host1, ap1)
	net.addLink(host2, ap1)

	net.build()
	ap1.start([])
	spin.stop()
	CONFIG_TMUX(["Attacker"], "NTLM_JOHN_CRACK")
	spin.start()
	net.stop()
	spin.stop()
	os.system("rm /WifiForge/framework/loot/4whs.pot")
	os.system("clear")


