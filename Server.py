from socket import *
import threading
import sys

SIZE = 1024
FORMAT = "utf-8"

def handle_client(conn, addr):
    print(f"New client connected {addr}")
    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        print(f"User {addr} said: {msg}")
        if msg == "/leave":
            print(f"User {addr} disconnected from the server.")
            connected = False

        msg = f"You sent: {msg}"
        conn.send(msg.encode(FORMAT))

    conn.close()
def main ():
    if len(sys.argv) != 3:
        print("The format is: python Server.py <ip> <port>")
        return

    ip = sys.argv[1]
    port = int(sys.argv[2])
    ADDR = (ip, port)

    server = socket(AF_INET, SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Server is listening on {ADDR}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"\nActive Connections: {threading.active_count() - 1}")

if __name__ == "__main__":
    main()