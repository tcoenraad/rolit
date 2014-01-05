import readline
import socket
import sys
import threading
import random

from rolit.client import Client
from rolit.protocol import Protocol

class ServerHandler(threading.Thread):

    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        while True:
            response = self.client.socket.recv(4096)
            if not response:
                break

            sys.stdout.write('\r')
            lines = response.strip().split(Protocol.EOL)
            for line in lines:
                data = line.split(Protocol.SEPARATOR)
                try:
                    if len(data) == 1:
                        getattr(self.client.router, Client.Router.routes[data[0]]['method'])()
                    else:
                        getattr(self.client.router, Client.Router.routes[data[0]]['method'])(data[1:])
                except KeyError:
                    self.client.Router.error(line)

            sys.stdout.write('$ ' + readline.get_line_buffer())
            sys.stdout.flush()

def main():
    client = Client(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    port = 3535
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    name = "Monitor_%s" % random.randint(0, 3535)
    client.socket.connect(('localhost', port))

    thread = ServerHandler(client)
    thread.daemon = True
    thread.start()

    client.socket.send("%s %s %s %s" % (Protocol.GREET, name, Protocol.TRUE, Protocol.TRUE))
    print("Welcome to the Rolit monitor, %s!" % name)
    Client.menu()

    while True:
        s = raw_input('$ ')
        data = s.split(Protocol.SEPARATOR)

        try:
            option = data[0]
            if not Client.options[option]['args'] == len(data) - 1:
                continue
            if len(data) == 1:
                getattr(client, Client.options[option]['method'])()
            elif len(data) >= 2:
                getattr(client, Client.options[option]['method'])(data[1:])
        except (KeyError, ValueError):
            continue

if __name__ == "__main__":
    main()
