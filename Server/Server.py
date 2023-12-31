from socket import *
import threading
import sys
import re
import os
from datetime import datetime

SIZE = 1024
FORMAT = "utf-8"
SERVER_FILE_DIR = os.path.dirname(os.path.abspath(__file__))


# This function checks if the IP address is valid format-wise
# param ip - IP address of the server
# returns True if valid, False if not

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

# This function checks if the port number is valid format-wise
# param port - port where the server is listening in
# returns True if valid, False if not

def is_valid_port(port):
    try:
        port = int(port)
        return 0 < port < 65536
    except:
        return False

# This function returns the command list when the user uses the command /?
# returns a string containing the command list

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

# This function assigns the client a unique alias
# param conn - a socket object that is connected to the client
# param registeredUsers - an array of strings that contain the aliases of
#                         current registered users
# param msg - a message from the client
# param thisUser - the current alias of the client
# returns a string that contains the new alias of the user

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

# This function allows the client to store a file in the server
# param conn - a socket object that is connected to the client
# param msg - a message from the client
# param thisUser - the current alias of the client

def handleStore(conn, msg, thisUser):
    parts = msg.split()
    if thisUser is None:
        reply = "Error: File Storage Failed. You are not Registered."
        print("Aborting /store... Client not Registered...")

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
            reply = ""

            if os.path.exists(filePath): # if file exists in server
                print("File Already Exists in Server Storage... Overwriting File...")
                reply += "Note: A File with the Same Name Already Exists in Server Storage. Overwriting File...\n"

            with open(filePath, "wb") as file:
                while True:
                    length_content = conn.recv(4)
                    size_content = int.from_bytes(length_content, byteorder='big')
                    content = conn.recv(size_content)
                    if not content or content == b"FILE_TRANSFER_COMPLETE":
                        print("File Transfer has Finished")
                        break
                    file.write(content)
                timestamp = datetime.now()
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                reply += f"{thisUser} <{formatted_timestamp}>: Uploaded {fileName}"


        # if file exists in client directory
    else:
        reply = "Error: Command parameters do not match or is not allowed."
    
    conn.send(reply.encode(FORMAT))

# This function allows the client to fetch a file from the server
# param conn - a socket object that is connected to the client
# param msg - a message from the client
# param thisUser - the current alias of the client

def handleGet(conn, msg, thisUser):
    parts = msg.split()

    if thisUser is None:
        reply = "Error: Get File Failed. You are not Registered."
        print("Aborting /get... Client not Registered...")
        conn.send(reply.encode(FORMAT))
    
    elif len(parts) == 2 and parts[1]:
        print(f"{thisUser} called handleGet")
        fileName = parts[1]

        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        filePath = os.path.join(currentDirectory, fileName)

        if not os.path.exists(filePath): 
            print("FILE_NOT_FOUND")
            conn.send("File Does Not Exist in the Server".encode())
            # reply = "FILE_NOT_FOUND_IN_THE_SERVER"
        else:
            print("FILE_WAS_FOUND")
            conn.send("File Exists in the Server".encode())
            # reply = "FILE_WAS_FOUND_IN_THE_SERVER"
            with open(filePath, "rb") as file:
                content = file.read(SIZE)
                while content:
                    print("reading and sending...please wait...")
                    conn.send(len(content).to_bytes(4, byteorder='big'))
                    conn.send(content)
                                
                    content = file.read(SIZE)
                print(f"File Sent {fileName}")
                print("File Transfer has Finished")
                conn.send(len(b"FILE_TRANSFER_COMPLETE").to_bytes(4, byteorder='big'))     
                conn.send(b"FILE_TRANSFER_COMPLETE")

    else:
        reply = "Error: Command parameters do not match or is not allowed."
        conn.send(reply.encode(FORMAT))

# This function sends the file directory list to the client
# param conn - a socket object that is connected to the client
# param thisUser - the current alias of the client

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

# This function handles all the commands from the client
# param msg - a message from the client
# param conn - a socket object that is connected to the client
# param addr - the client's address
# param registeredUsers - an array of strings that contain the aliases of
#                         current registered users
# param thisUser - the current alias of the client
# returns:
#        True if client is still connected, False if not
#        a string containing the current alias of the client

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

    elif re.match(r'^/get\s*((\S+)?\s*)*$', msg) and not re.match(r'^/get\S', msg):
        handleGet(conn, msg, thisUser)

    elif re.match(r'^/dir$', msg):
        handleDir(conn, thisUser)
            
    else:
        reply = "Error: Command not found."
        conn.send(reply.encode(FORMAT))

    return True, thisUser

# This function handles the client in its assigned thread
# param conn - a socket object that is connected to the client
# param addr - the client's address
# param registeredUsers - an array of strings that contain the aliases of
#                         current registered users

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
