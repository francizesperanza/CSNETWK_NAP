from socket import *
import re

SIZE = 1024
FORMAT = "utf-8"
ADDR = ('',12345)

def main():
    joined = False
    print("Hello, Client. Start by joining the File Exchange Server.\n")

    """
    This section checks
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
        else:
            print("Error: Command parameters do not match or is not allowed.")

    client = socket(AF_INET, SOCK_STREAM)

    try:
        client.connect(ADDR)
        print(f"Client connected to {ADDR}")

        connected = True
        while connected:
            msg = input("Input: ")

            client.send(msg.encode(FORMAT))

            if msg == ("/leave"):
                print("Disconnecting from the server...")
                connected = False
            else:
                msg = client.recv(SIZE).decode(FORMAT)
                print(f"{msg}")
    except ConnectionRefusedError:
        print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
    finally:
        client.close()

if __name__ == "__main__":
    main()