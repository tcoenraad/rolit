import socket, sys, threading

from models.server import *
from models.protocol import Protocol
from models.helpers import Helpers

class ClientHandler(threading.Thread):

    def __init__(self, socket, client_address):
        threading.Thread.__init__(self)
        self.socket = socket
        self.client_address = str(client_address)
        self.name = str(client_address)

    def run(self):
        try:
            data = self.socket.recv(4096).strip().split(Protocol.SEPARATOR)

            # before everything else, greet
            if not data[0] == Protocol.GREET or not data[1]:
                return

            if len(data) == 2:
                self.client = server.connect(self.socket, data[1])
            else:
                self.client = server.connect(self.socket, data[1], data[2], data[3])

            self.name = self.client['name']
            Helpers.notice('Client %s introduced itself as `%s`' % (self.client_address, self.name))

            while True:
                data = self.socket.recv(4096).strip().split(Protocol.SEPARATOR)
        
                if not data:
                    break

                if data[0] == Protocol.JOIN and len(data) == 2:
                    server.join(self.client, data[1])
                elif data[0] == Protocol.PLACE and len(data) == 2:
                    server.place(self.client, data[1])
                elif data[0] == Protocol.CHAT and len(data) == 2:
                    server.chat(self.client, data[1])
                elif data[0] == Protocol.CHALLENGE and len(data) == 2:
                    server.challenge(self.client, data[1])
                elif data[0] == Protocol.CHALLENGE and len(data) == 3:
                    server.challenge(self.client, "%s %s" % (data[1], data[2]))
                elif data[0] == Protocol.CHALLENGE and len(data) == 4:
                    server.challenge(self.client, "%s %s %s" % (data[1], data[2], data[3]))
                elif data[0] == Protocol.CHALLENGE_RESPONSE and len(data) == 2:
                    server.challenge_response(self.client, data[1])
                elif data[0] == Protocol.STAT_REQUEST and len(data) == 3:
                    server.stats(self.client, data[1], data[2])
                elif data[0] == ProtocolExtended.GAMES:
                    server.send_games(self.client)
                elif data[0] == ProtocolExtended.GAME_PLAYERS and len(data) == 2:
                    server.send_game_players(self.client, data[1])
                elif data[0] == ProtocolExtended.GAME_BOARD and len(data) == 2:
                    server.send_game_board(self.client, data[1])
                else:
                    raise ClientError('Invalid command `%s`, refer to protocol' % data)
        except ServerError as e:
            Helpers.error('500 Internal Server Error: `%s`' % e)
            self.socket.send('500 Internal Server Error: `%s`' % (e, Protocol.EOL))
        except ClientError as e:
            Helpers.warning('Client `%s` made a 400 Bad Request: `%s`' % (self.name, e))
            self.socket.send('400 Bad Request: `%s`%s' % (e, Protocol.EOL))
        except IOError:
            Helpers.warning('Connection error with %s' % self.name)
        finally:
            Helpers.log('Connection lost with %s' % self.name)
            self.socket.close()

            if hasattr(self, 'client'):
                server.disconnect(self.client)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    port = 3535
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    sock.bind(('0.0.0.0', port))
    sock.listen(1)

    server = Server()

    Helpers.notice('Server started on port %s' % port)

    while True:
        socket, client_address = sock.accept()
        Helpers.log('Connection established with %s' % str(client_address))
        thread = ClientHandler(socket, client_address)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()
