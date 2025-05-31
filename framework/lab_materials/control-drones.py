import json
import os
import sys
import tty
import termios

# ansi escapes for text color
RED     = "\033[91m"
GREEN   = "\033[92m"
BLUE = "\033[94m"
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

def control(drone):
    with open("/tmp/drone_positions.json") as f:
        data = json.load(f)

    # load the coordinates for the specified drone
    pos = data[drone]

    while True:
        print(f"{GREEN}Controlling {drone}!{RESET}")
        print(f"Use arrow keys to move. Press q to quit.")
        print(f"Current position: {BLUE}x={pos[0]}, y={pos[1]}{RESET}")
        
        key = getkey()

        # move up
        if key == '\x1b[A':  
            if pos[1] < 30:
                pos[1] += 1
            # print(pos[1])

        # move down
        elif key == '\x1b[B':
            if pos[1] > 0:
                pos[1] -= 1
            # print(pos[1])
        
        # move right
        elif key == '\x1b[C':
            if pos[0] < 30:
                pos[0] += 1
            # print(pos[0])

        # move left
        elif key == '\x1b[D':
            if pos[0] > 0:
                pos[0] -= 1
            # print(pos[0])

        # exit
        elif key == 'q':
            print("Quitting...")
            break

        data[drone] = pos
        with open("/tmp/drone_positions.json", "w") as f:
            json.dump(data, f)

        clearscreen()

def main():
    # pull the drone passwords written by UAV
    with open("/tmp/drone_passwords.json") as f:
            data = json.load(f)
    
    # pull the drone positions written by the drone_hacking script
    drones = list(data.keys())
    passwords = [n[0] for n in data.values()]

    while True:
        print(f"Select a drone to control:")
        for i, n in enumerate(drones, start=1):
            print(f"{i}. {n}")

        cmd = input()
        if not cmd:
            continue

        # ensure the inputted data is an integer
        elif cmd[0].isdigit():
            index = int(cmd[0]) - 1
            
            # check if index exists
            if 0 <= index < len(drones):
                drone  = drones[index]      # store drone name
                passwd = passwords[index]   # store drone password

                # prompt user for password
                print(f"Enter password for {drone}:")
                userpass = input()

                # verification
                if(userpass == passwd):
                    print(f"{GREEN}Correct!{RESET}")
                    clearscreen()
                    control(drone)
                else:
                    print(f"{RED}Incorrect password.{RESET}")
                    halt()
            else:
                print(f"{RED}Invalid option.{RESET}")
                halt()
        else:
            print(f"{RED}Invalid option.{RESET}")
            halt()

if __name__ == '__main__':
    main()