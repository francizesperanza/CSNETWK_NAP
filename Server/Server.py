from socket import *
import threading
import sys
import re

SIZE = 1024
FORMAT = "utf-8"


def is_valid_ip(ip):
    try:
        inet_aton(ip)
        return True
    except:
        return False


def is_valid_port(port):
    try:
        port = int(port)
        return 0 < port < 65536
    except:
        return False


def print_command_list ():
    return """

    File Exchange System Command List:
          
    /join <ip> <port>
          - connects you to the File Exchange Server.
    
    /leave
          - disconnects you from the File Exchange Server.
    
    /register <handle>
          - registers you under a unique alias and allows you
            to use the server's functionalities.
    
    /store <filename>
          - allows the client to send a file to the server.
    
    /dir
          - requests the server for a list of all the files in
            in the server
    
    /get <filename>
          - fetches a file from the server

    /?
          - shows all Input Syntax commands for reference
    

    """

def handleRegister(conn, registeredUsers, msg, thisUser):
    parts = msg.split()

    if len(parts) == 2 and parts[1]:
        username = parts[1]

        if thisUser is not None:
            reply = "Error: Registration failed. You are already registered."
        elif username in registeredUsers:
            reply = "Error: Registration failed. Handle or alias already exists."
        else: 
            registeredUsers.append(username)
            reply = f"Welcome {username}!"
            print(registeredUsers)
            thisUser = username 
    else:
        reply = "Error: Command parameters do not match or is not allowed."

    conn.send(reply.encode(FORMAT))
    return thisUser


def handle_commands (msg, conn, addr, registeredUsers, thisUser):
    if msg.startswith("/join"):
        if re.match(r'^/join (\S+) (\S+)$', msg):
            if(thisUser):
                print(f"{thisUser} tried to join the File Exchange Server again.")
            else:
                print(f"User {addr} tried to join the File Exchange Server again.")
            reply = "You already joined the File Exchange Server."
            conn.send(reply.encode(FORMAT))
            
        else:
            reply = "Error: Command parameters do not match or is not allowed."
            conn.send(reply.encode(FORMAT))
            
    elif msg.startswith("/?"):
        if re.match(r'^/\?$', msg):
            if(thisUser):
                print(f"{thisUser} requested for help.")
            else:
                print(f"User {addr} requested for help.")
            help = print_command_list()
            conn.send(help.encode(FORMAT))
            
        else:
            reply = "Error: Command parameters do not match or is not allowed."
            conn.send(reply.encode(FORMAT))
            
    elif msg.startswith("/leave"):
        if re.match(r'^/leave$', msg):
            if(thisUser):
                print(f"{thisUser} disconnected from the server.")
            else:
                print(f"User {addr} disconnected from the server.")
            reply = "Connection closed. Thank you!"
            conn.send(reply.encode(FORMAT))
            return False, thisUser
        else:
            reply = "Error: Command parameters do not match or is not allowed."
            conn.send(reply.encode(FORMAT))
            
    elif re.match(r'^/register\s*(\S+)?\s*$', msg) and not re.match(r'^/register\S', msg):
        thisUser = handleRegister(conn, registeredUsers, msg, thisUser)
            
    else:
        reply = "Error: Command not found."
        conn.send(reply.encode(FORMAT))

    return True, thisUser

def handle_client(conn, addr, registeredUsers):
    print(f"New client connected {addr}")
    connected = True
    thisUser = None
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if (thisUser):
            print(f"{thisUser} said: {msg}")
        else:
            print(f"User {addr} said: {msg}")
        connected, thisUser = handle_commands(msg, conn, addr, registeredUsers, thisUser)
    conn.close()

def main ():
    if len(sys.argv) != 3:
        print("The format is: python Server.py <ip> <port>")
        return

    ip = sys.argv[1]
    port = sys.argv[2]
    if is_valid_ip(ip) and is_valid_port(port):
        ADDR = (ip, int(port))
    else:
        print("Error: Invalid value for IP and/or Port")
        return
    registeredUsers = []

    server = socket(AF_INET, SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Server is listening on {ADDR}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, registeredUsers))
        thread.start()
        print(f"\nActive Connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    main()