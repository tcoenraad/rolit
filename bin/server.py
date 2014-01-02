import socket
import sys
import threading

from rolit.server import *
from rolit.protocol import Protocol
from rolit.helpers import Helpers

router = {
    Protocol.JOIN : { 'args' : 1, 'method' : 'join' },
    Protocol.PLACE : { 'args' : 1, 'method' : 'place' },
    Protocol.CHAT : { 'args' : 1, 'method' : 'chat' },
    Protocol.CHALLENGE : { 'args' : 1, 'method' : 'challenge' },
    Protocol.CHALLENGE : { 'args' : 2, 'method' : 'challenge' },
    Protocol.CHALLENGE : { 'args' : 3, 'method' : 'challenge' },
    Protocol.CHALLENGE_RESPONSE : { 'args' : 1, 'method' : 'challenge_response' },
    Protocol.STAT : { 'args' : 2, 'method' : 'stats' },
    ProtocolExtended.GAMES: { 'args' : 0, 'method' : 'send_games'},
    ProtocolExtended.GAME_PLAYERS : { 'args' : 1, 'method' : 'send_game_players'},
    ProtocolExtended.GAME_BOARD : { 'args' : 1, 'method' : 'send_game_board'}
}

class ClientHandler(threading.Thread):

    def __init__(self, server, sock, client_address):
        threading.Thread.__init__(self)
        self.server = server
        self.socket = sock
        self.client_address = str(client_address)
        self.name = str(client_address)

    def run(self):
        try:
            data = self.socket.recv(4096).strip().split(Protocol.SEPARATOR)
            Helpers.log("`%s`: `%s`" % (self.name, data))

            # before everything else, greet
            if not data[0] == Protocol.GREET or not data[1]:
                return

            if len(data) == 2:
                self.client = self.server.connect(self.socket, data[1])
            else:
                self.client = self.server.connect(self.socket, data[1], data[2], data[3])

            self.name = self.client['name']
            Helpers.notice('Client %s introduced itself as `%s`' % (self.client_address, self.name))

            while True:
                data = self.socket.recv(4096).strip().split(Protocol.SEPARATOR)

                Helpers.log("`%s`: `%s`" % (self.name, data))
                if not data:
                    break
                try:
                    route = router[data[0]]
                    if not route['args'] == len(data) - 1:
                        break
                    if route['args'] == 0:
                        getattr(self.server, route['method'])(self.client)
                    elif route['args'] == 1:
                        getattr(self.server, route['method'])(self.client, data[1])
                    elif route['args'] == 2:
                        getattr(self.server, route['method'])(self.client, data[1], data[2])
                    elif route['args'] == 3:
                        getattr(self.server, route['method'])(self.client, data[1], data[2], data[3])
                except KeyError:
                    raise ClientError('Invalid command `%s`, refer to protocol' % data)
        except ServerError as e:
            Helpers.error('500 Internal Server Error: `%s`' % e)
            self.socket.send('500 Internal Server Error: `%s`%s' % (e, Protocol.EOL))
        except ClientError as e:
            Helpers.warning('Client `%s` made a 400 Bad Request: `%s`' % (self.name, e))
            self.socket.send('400 Bad Request: `%s`%s' % (e, Protocol.EOL))
        except IOError:
            Helpers.warning('Connection error with %s' % self.name)
        finally:
            Helpers.log('Connection lost with %s' % self.name)
            self.socket.close()

            if hasattr(self, 'client'):
                self.server.disconnect(self.client)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    port = 3535
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    sock.bind(('0.0.0.0', port))
    sock.listen(1)

    server = Server()

    Helpers.notice('Rolit server started on port %s' % port)

    while True:
        conn, client_address = sock.accept()
        Helpers.log('Connection established with %s' % str(client_address))
        thread = ClientHandler(server, conn, client_address)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()
