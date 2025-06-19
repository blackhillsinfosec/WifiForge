import json
import os
import sys
import tty
import termios
from pwn import *

# ansi escapes for text color
RED     = "\033[91m"
GREEN   = "\033[92m"
BLUE    = "\033[94m"
RESET   = "\033[0m"

def clearscreen():
    os.system("clear")

def halt():
    print(f"Press any key to continue.")
    input()
    clearscreen()

def getkey():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)              
        ch = sys.stdin.read(1)      
        if ch == '\x1b':            
            ch += sys.stdin.read(2) 
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) 

def moveongraph(drone, position, data):

    while True:
        print(f"{GREEN}Controlling {drone}!{RESET}")
        print(f"Use arrow keys to move. Press q to quit.")
        print(f"Current position: {BLUE}x={position[0]}, y={position[1]}{RESET}")
        
        key = getkey()
        # print(f"You pressed: {repr(key)}")

        # move up
        if key in ('\x1b[A', '\x1bOA'):
            if position[1] < 30:
                position[1] += 1
            # print(position[1])

        # move down
        elif key in ('\x1b[B', '\x1bOB'):
            if position[1] > 0:
                position[1] -= 1
            # print(position[1])
        
        # move right
        elif key in ('\x1b[C', '\x1bOC'):
            if position[0] < 30:
                position[0] += 1
            # print(position[0])

        # move left
        elif key in ('\x1b[D', '\x1bOD'):
            if position[0] > 0:
                position[0] -= 1
            # print(position[0])

        # exit
        elif key == 'q':
            print("Quitting...")
            clearscreen()
            break

        data[drone]["position"] = position
        with open("/tmp/drone-info.json", "w") as f:
            json.dump(data, f)

        clearscreen()

def restoreinterfaces():
    basedir = os.path.dirname(os.path.abspath(__file__))
    restore = os.path.join(basedir, 'restore-interfaces.sh') # /lab_materials/restore-interfaces.sh
    os.system(f"chmod +x {restore} ; bash {restore}")

def connectshell(drone, listener, passwd, port):
    print(f"Connecting to {drone}...")
    
    # connect to the drones
    context.log_level = 'error'
    p = remote(listener, port)
    p.sendline(passwd.encode())

    p.interactive()
    p.sendline("exit")
    p.close()
    
    clearscreen()

def main():
    restoreinterfaces()
    clearscreen()

    # pull the drone passwords written by UAV
    with open("/tmp/drone-info.json") as f:
            data = json.load(f)
    
    # pull the drone positions written by the drone_hacking script
    drones = list(data.keys())
    positions = [data[name]["position"] for name in drones]
    passwords = [data[name]["password"] for name in drones]
    listeners = [data[name]["listener"] for name in drones]
    ports     = [data[name]["port"] for name in drones]
    pwned = [0] * len(drones)   # pwned boolean as a dynamic list

    while True:
        print(f"Select a drone to control:")
        for i, n in enumerate(drones, start=1):
            if pwned[i-1] == 1:
                print(f"{i}. {n} {GREEN}(Pwn3d!){RESET}")
            else:
                print(f"{i}. {n}")

        cmd = input()
        if not cmd:
            continue

        # ensure the inputted data is an integer
        elif cmd.isdigit():
            index = int(cmd) - 1
            
            # check if index exists
            if 0 <= index < len(drones):
                drone  = drones[index]      # store drone name
                position = positions[index]   # store drone position
                passwd = passwords[index]   # store drone password
                listener = listeners[index] # store drone listener
                port = ports[index]         # store drone port

                # check if pwned already
                if pwned[index] == 1:
                    clearscreen()

                # if not pwned, prompt user for password
                else:
                    print(f"Enter password for {drone}:")
                    userpass = input()

                    # pass verification
                    if(userpass == passwd):
                        print(f"{GREEN}Correct!{RESET}")
                        pwned[index] = 1
                        clearscreen()
                    else:
                        print(f"{RED}Incorrect password.{RESET}")
                        halt()

                # after authentication (either pwned or correct pass)
                print(f"{GREEN}Correct password for {drone}!{RESET}")
                print(f"What would you like to do?")
                print(f"1. Fly drone around")
                print(f"2. Drone remote shell")

                cmd = int(input())

                if cmd == 1:
                    clearscreen()
                    moveongraph(drone, position, data)          # need to pass everything so file updates work
                elif cmd == 2:
                    clearscreen()
                    connectshell(drone, listener, passwd, port)

            else:
                print(f"{RED}Invalid option.{RESET}")
                halt()
        else:
            print(f"{RED}Invalid option.{RESET}")
            halt()

if __name__ == '__main__':
    main()
