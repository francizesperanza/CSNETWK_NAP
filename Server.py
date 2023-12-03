from socket import *
import threading
import sys

SIZE = 1024
FORMAT = "utf-8"
SUCCESS = "200"
ERROR = "400"

def register(conn, registeredUsers, msg):
    parts = msg.split(" ")
    username = parts[1]

    if username in registeredUsers:
        conn.send(ERROR.encode(FORMAT))
    else:
        conn.send(SUCCESS.encode(FORMAT))
        registeredUsers.append(username)
        print(f"new users: {registeredUsers}")
    


def handle_client(conn, addr, registeredUsers):
    print(f"New client connected {addr}")
    connected = True

    while connected:
        msg = conn.recv(SIZE).decode(FORMAT) #error here if a client forcibly closes
        print(f"User {addr} said: {msg}")
        if msg == "/leave":
            print(f"User {addr} disconnected from the server.")
            connected = False

        if msg.startswith("/register"):
            register(conn, registeredUsers, msg)

    conn.close()

def main ():
    if len(sys.argv) != 3:
        print("The format is: python Server.py <ip> <port>")
        return

    ip = sys.argv[1]
    port = int(sys.argv[2])
    ADDR = (ip, port)
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