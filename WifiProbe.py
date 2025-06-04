import subprocess
import sys
import os
#import argparse -alternative option for getting cli args might need

def user_guide(): #guide with usage instructions
	guide = """
Usage Guide: python3 WifiProbe.py --capture --intf <interface> --output <snapshot.py>

Arguments:

--capture		Argument to capture a snapshot (required)
--intf <interface>      Argument for interface (ex. wlan0) (required)
--output <file>		Argument to name the output file (default: snapshot.py)
"""
	print(guide)

def parse_cli():

	args = sys.argv[1:]
	capture = False
	intf = None
	output = 'snapshot.py'

	i = 0
	while i < len(args):
		arg = args[i]
		if arg == '--capture': #check for --capture
			capture = True
			i += 1
		else if arg == '--intf': #check for -intf and a value
			if i + 1 < len(args):
				intf = args[i+1]
				i += 2
			else
				print("Error: --intf requires a value. Ex. --intf <wlan0>")
				user_guide()
				sys.exit(1)
		else if arg == '--output': #check for --output and a value
			if i + 1 < len(args):
				output = args[i+1]
				i += 2
			else
				print("Error: --output requires a value. Ex. --output <airgeddon_snapshot1.py>")
				user_guide()
				sys.exit(1)
		else
			print("Error: Unknown cli argument")
			user_guide()
			sys.exit(1)

	return capture, intf, output

#def extract_intf_data(intf): pull network data
	# option iw intf scan - output = subprocess.check_output(['sudo', 'iw', intf, 'scan'], text=True)
	# for essid, channel, signal, encyption
	#library backend libnl for parsing insteaad of iw or libiw
	#json

#def pars_airmon-ng_output():
	#parse airmon-ng? - phys, intf, driver, chipset

#def parse_output(     ): read and store data


#def gen_snapshot(     ): generate snapshot to labs folder

#def main():
