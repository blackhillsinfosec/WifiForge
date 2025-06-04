#import subprocess
import sys
import os
#import argparse -alternative option for getting cli args might need


	print(" Example input: python3 WifiProbe.py --capture --intf <interface> --output <snapshot.py> ") #some cli args to make mock snapshot of lab
	print(" --capture (Required) --intf (Required) --output (not necessary) ")

def user_guide(): #make reusable guide with instructions for use and to follow all error messages

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
			i += 1;
		else if arg == '--intf': #check for -intf and a value
			if i + 1 < len(args):
				intf = args[i+1]
				i += 2
			else
				print("Error: --intf requires a value. Ex. --intf <wlan0>")
				sys.exit(1)
		else if arg == '--output':
			if i + 1 < len(args):
				output = args[i+1]
				i += 2
			else
				printf("Error: --output requires a value. Ex. --output <airgeddon_snapshot1.py>")
		else
			print("Error: Unknown cli argument")
			sys.exit(1)

	return capture, intf, output

#def extract_lab(intf): pull data from lab

#def parse_output(     ): read and store data

#def gen_snapshot(     ): generate snapshot

#def main():
