from socket import *
import re
import sys
import os

SIZE = 1024
FORMAT = "utf-8"
ADDR = ('',12345)

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

def sendFile(request, client):
    parts = request.split()
    fileName = parts[1]
    print(f"file name: {fileName}")

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    filePath = os.path.join(currentDirectory, fileName)

    # check if file exists
    if not os.path.exists(filePath): 
        client.send("FILE_NOT_FOUND".encode())# response to server
    else:
        client.send("FILE_WAS_FOUND".encode())# response to server
        with open(filePath, "rb") as file:
            content = file.read(SIZE)
            print(content)
            while content:
                print("reading and sending...please wait...")
                client.send(len(content).to_bytes(4, byteorder='big'))
                client.send(content)
                            
                print(f"sent {content}")
                content = file.read(SIZE)
                print("reading done")

            client.send(len(b"FILE_TRANSFER_COMPLETE").to_bytes(4, byteorder='big'))     
            client.send(b"FILE_TRANSFER_COMPLETE")
            

    reply = client.recv(SIZE).decode(FORMAT)
    print(f"{reply}")


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

        if user_input.startswith("/join"):
            if match:
                ip = match.group(1)
                port = match.group(2)

                if is_valid_ip(ip) and is_valid_port(port):
                    ADDR = (ip, int(port))
                    joined = True
                else:
                    print("Error: Invalid value for IP and/or Port")
            elif user_input == "/join" or re.match(r'^/join (\S+)$', user_input):
                print("Error: Command parameters do not match or is not allowed.")
            else:
                print("Error: Command not found.")

        elif user_input.startswith("/register"):
            if re.match(r'^/register (\S+)$', user_input):
                print("Error: Registration failed. Please connect to the server first.")
            elif user_input == "/register":
                print("Error: Command parameters do not match or is not allowed. You also need to join the File Exchange Server first.")
            else:
                print("Error: Command not found.")

        elif user_input.startswith("/store"):
            if re.match(r'^/store (\S+)$', user_input):
                print("Error: File storing failed. Please connect to the server first.")
            elif user_input == "/store":
                print("Error: Command parameters do not match or is not allowed. You also need to join the File Exchange Server first.")
            else:
                print("Error: Command not found.")

        elif user_input.startswith("/get"):
            if re.match(r'^/get (\S+)$', user_input):
                print("Error: File fetching failed. Please connect to the server first.")
            elif user_input == "/get":
                print("Error: Command parameters do not match or is not allowed. You also need to join the File Exchange Server first.")
            else:
                print("Error: Command not found.")

        elif re.match(r'^/leave$', user_input):
            print("Error: Disconnection failed. Please connect to the server first.")

        elif re.match(r'^/dir$', user_input):
            print("Error: File directory list request failed. Please connect to the server first.")
            
        elif re.match(r'^/\?$', user_input):
            print_command_list()
        else:
            print("Error: Command not found.")

    client = socket(AF_INET, SOCK_STREAM)

    try:
        client.connect(ADDR)
        print(f"Connection to the File Exchange Server is successful! {ADDR}")

        connected = True
        while connected:
            msg = input("Input: ")

            client.send(msg.encode(FORMAT))
            reply = client.recv(SIZE).decode(FORMAT)
            print(f"{reply}")

            if msg == ("/leave"):
                print("Disconnecting from the server...")
                connected = False

            if reply.startswith("/store"):
                sendFile(reply, client)

    except ConnectionRefusedError:
        print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
    except ConnectionResetError:
        print("Error: Server shut down.")

    finally:
        client.close()

if __name__ == "__main__":
    main()