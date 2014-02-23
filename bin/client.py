import readline
import socket
import sys
import threading
import random

from rolit.client import Client, NoPrivateKeyError
from rolit.protocol import Protocol
from rolit.helpers import Helpers

class ServerHandler(threading.Thread):

    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        while True:
            response = self.client.socket.recv(4096)
            # wait for Protocol.EOL
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
                        getattr(self.client.router, Client.Router.routes[data[0]]['method'])(*data[1:])
                except KeyError:
                    self.client.Router.error(line)

            sys.stdout.write('$ ' + readline.get_line_buffer())
            sys.stdout.flush()

def main():

    host = 'localhost'
    port = 3535
    name = "Monitor_%s" % random.randint(0, 3535)
    private_key_file = "./private_key"
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3 and sys.argv[2].isdigit():
        port = int(sys.argv[2])
    if len(sys.argv) >= 4:
        name = sys.argv[3]
    if len(sys.argv) >= 5:
        private_key_file = sys.argv[4]

    try:
        private_key = open(private_key_file, "r").read()
    except IOError:
        private_key = None

    client = Client(socket.socket(socket.AF_INET, socket.SOCK_STREAM), private_key)
    client.socket.connect((host, port))

    thread = ServerHandler(client)
    thread.daemon = True
    thread.start()

    try:
        client.handshake(name)
    except NoPrivateKeyError as e:
        Helpers.error(e)
        return

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
            else:
                getattr(client, Client.options[option]['method'])(data[1:])
        except (KeyError, ValueError):
            continue

if __name__ == "__main__":
    main()
