from socket import *
import threading
import sys
import re
import os
from datetime import datetime

SIZE = 1024
FORMAT = "utf-8"
SERVER_FILE_DIR = os.path.dirname(os.path.abspath(__file__))


def is_valid_ip(ip):
    try:
        inet_pton(AF_INET, ip)
        return True
    except error:
        try:
            gethostbyname(ip)
            return True
        except error:
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
    print(f"{thisUser} called handleRegister")
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


def handleStore(conn, msg, thisUser):
    parts = msg.split()
    if thisUser is None:
        reply = "Error: File Storage Failed. You are not Registered."
        print("Aboring /store... Client not Registered...")

    elif len(parts) == 2 and parts[1]:
        print(f"{thisUser} called handleStore")
        fileName = parts[1] 
        
        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(currentDirectory, fileName)

        # ask client if file even exists in the first place
        query = msg
        print(f"sending query: {query}")
        conn.send(query.encode(FORMAT))

        # client's response
        fileStatus = conn.recv(SIZE).decode(FORMAT)

        if fileStatus == "FILE_NOT_FOUND":
            print(f"{thisUser} sent non-existent filename... aborting process...")
            reply = "Error: File not found."

        elif fileStatus == "FILE_WAS_FOUND":
            print(f"{thisUser} sent valid filename... attempting to write file...")
            if os.path.exists(filePath): # if file exists in server
                print("File Already Exists in Server Storage... Overwriting File...")
            with open(filePath, "wb") as file:
                while True:
                    print("about to receive")
                    length_content = conn.recv(4)
                    size_content = int.from_bytes(length_content, byteorder='big')
                    content = conn.recv(size_content)
                    print(f"received: {content}")
                    if not content or content == b"FILE_TRANSFER_COMPLETE":
                        print("File Transfer has Finished")
                        break
                    file.write(content)
                timestamp = datetime.now()
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                reply = f"{thisUser} <{formatted_timestamp}>: Uploaded {fileName}"


        # if file exists in client directory
    else:
        reply = "Error: Command parameters do not match or is not allowed."
    
    conn.send(reply.encode(FORMAT))
    


def handleDir (conn, thisUser):
    if (thisUser):
        try:
            print(f"{thisUser} requested for the file directory list.")
            filenames = [f for f in os.listdir(SERVER_FILE_DIR) if os.path.isfile(os.path.join(SERVER_FILE_DIR, f))]
            
            filenames = [filename for filename in filenames if filename != 'Server.py']
            
            if len(filenames) == 0:
                reply = "There are currently no files in the File Exchange Server."
            else:
                reply = "Server Directory:\n\n"
                for i in range(len(filenames)):
                    reply = reply + filenames[i] + "\n"
            
            conn.send(reply.encode(FORMAT))
        except FileNotFoundError:
            reply = f"The directory '{SERVER_FILE_DIR}' does not exist."
            conn.send(reply.encode(FORMAT))
    else:
        reply = "Error: File directory list request failed. Please register an alias first."
        conn.send(reply.encode(FORMAT))


def handle_commands (msg, conn, addr, registeredUsers, thisUser):
    if re.match(r'^/join(?: (\S+)(?: (\S+))?)?$', msg):
        if re.match(r'^/join (\S+) (\S+)?$', msg):
            if(thisUser):
                print(f"{thisUser} tried to join the File Exchange Server again.")
            else:
                print(f"User {addr} tried to join the File Exchange Server again.")
            reply = "You already joined the File Exchange Server."
            conn.send(reply.encode(FORMAT))
            
        else:
            reply = "Error: Command parameters do not match or is not allowed. Also, you already joined the File Exchange Server."
            conn.send(reply.encode(FORMAT))
            
    elif re.match(r'^/\?$', msg):
        if(thisUser):
            print(f"{thisUser} requested for help.")
        else:
            print(f"User {addr} requested for help.")
        help = print_command_list()
        conn.send(help.encode(FORMAT))
            
    elif re.match(r'^/leave$', msg):
        if(thisUser):
            print(f"{thisUser} disconnected from the server.")
        else:
            print(f"User {addr} disconnected from the server.")
        reply = "Connection closed. Thank you!"
        conn.send(reply.encode(FORMAT))
        return False, thisUser
            
    elif re.match(r'^/register\s*((\S+)?\s*)*$', msg) and not re.match(r'^/register\S', msg):
        thisUser = handleRegister(conn, registeredUsers, msg, thisUser)

    elif re.match(r'^/store\s*((\S+)?\s*)*$', msg) and not re.match(r'^/store\S', msg):
        handleStore(conn, msg, thisUser)
    
    elif re.match(r'^/dir$', msg):
        handleDir(conn, thisUser)
            
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