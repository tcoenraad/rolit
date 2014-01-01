import socket
import sys

from models.client import Client
from models.protocol import Protocol

def main():
    client = Client(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    port = 3535
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    client.socket.connect(('localhost', port))

    client.socket.send('greet Monitor 0 0')
    client.response()
    print("Welcome to the Rolit monitor!")
    client.menu()

    while True:
        s = raw_input('$ ')
        data = s.split(Protocol.SEPARATOR)

        try:
            route = int(data[0])
        except ValueError:
            continue

        if route < 0 or route > len(client.router):
            continue

        if not client.router[route]['args'] == len(data) - 1:
            continue

        if len(data) == 1:
            getattr(client, client.router[route]['method'])()
        elif len(data) == 2:
            getattr(client, client.router[route]['method'])(data[1])

if __name__ == "__main__":
    main()
