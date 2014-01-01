import socket
import readline

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
            option = int(data[0])
        except ValueError:
            continue

        if option < 0 or option > len(client.options):
            continue

        if not client.options[option]['args'] == len(data) - 1:
            continue

        if len(data) == 1:
            getattr(client, client.options[option]['method'])()
        elif len(data) == 2:
            getattr(client, client.options[option]['method'])(data[1])

if __name__ == "__main__":
    main()
