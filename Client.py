from socket import *
import re
import sys

SIZE = 1024
FORMAT = "utf-8"
ADDR = ('',12345)
SUCCESS = "200"
ERROR = "400"

def print_command_list ():
    print("""

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
    

    """)

def handleLeave(msg,client):
    print("Disconnecting from the server...")
    client.send(msg.encode(FORMAT))
    
    connected = False
    return connected



def handleRegister(msg, client):
    parts = msg.split()
    if len(parts) == 2 and parts[1]:
        print("sending register request to server")
        client.send(msg.encode(FORMAT))
        response = client.recv(SIZE).decode(FORMAT)
        if (response == SUCCESS):
            print(f"Welcome {parts[1]}!")
        elif (response == ERROR):
            print("Error: Registration failed. Handle or alias already exists.")

    else:
        print("Error: Command parameters do not match or is not allowed.")
    


def handleStore():
    pass



def main():
    """
    This section checks if the running command for the Client instance is valid
    """
    if len(sys.argv) != 2:
        print("The format is: python Server.py <client_name>")
        return

    client_name = sys.argv[1]
    joined = False
    print(f"Hello, {client_name}. Start by joining the File Exchange Server. Type \"/?\" for help.\n")

    """
    This section checks if client has joined the server or not
    """
    while not joined:
        user_input = input("Input: ")
        match = re.match(r'^/join (\S+) (\S+)$', user_input)

        if match:
            ip = match.group(1)
            port = int(match.group(2))
            ADDR = (ip, port)
            joined = True
        elif re.match(r'^/leave$', user_input):
            print("Error: Disconnection failed. Please connect to the server first.")
        elif re.match(r'^/\?$', user_input):
            print_command_list()
        else:
            print("Error: Command parameters do not match or is not allowed.")

    client = socket(AF_INET, SOCK_STREAM)



    try:
        client.connect(ADDR)
        print(f"Connection to the File Exchange Server is successful! {ADDR}")

        connected = True
        while connected:
            msg = input("Input: ")

            if re.match(r'^/leave\s*$', msg):
                connected = handleLeave(msg, client)

            elif re.match(r'^/register\s*(\S+)?\s*$', msg) and not re.match(r'^/register\S', msg):
                print("enter register")
                handleRegister(msg, client)
                print("exit register")

            elif re.match(r'^/store\s*$', msg):
                handleStore(msg)

            else:
                print("Error: Command not found.")

    except ConnectionRefusedError:
        print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
    finally:
        client.close()

if __name__ == "__main__":
    main()