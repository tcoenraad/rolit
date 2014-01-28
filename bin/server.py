import socket
import threading
import ConfigParser

from rolit.server import Server, ServerError, ClientError
from rolit.protocol import Protocol
from rolit.helpers import Helpers

class ClientHandler(threading.Thread):

    def __init__(self, server, sock, client_address):
        threading.Thread.__init__(self)
        self.server = server
        self.socket = sock
        self.client_address = str(client_address)
        self.name = str(client_address)

    def run(self):
        try:
            line = self.socket.recv(4096).strip()

            Helpers.log_and_whatsapp("`%s`: `%s`" % (self.name, line))

            data = line.split(Protocol.SEPARATOR)

            # before everything else, HANDSHAKE
            if not data[0] == Protocol.HANDSHAKE or len(data) < 2:
                return

            if len(data) == 2:
                self.client = self.server.connect(self.socket, data[1])
            else:
                self.client = self.server.connect(self.socket, data[1], data[2])

            self.name = self.client['name']
            Helpers.notice_and_whatsapp('Client %s introduced itself as `%s`' % (self.client_address, self.name))

            while True:
                line = self.socket.recv(4096).strip()
                if not line:
                    break

                Helpers.log_and_whatsapp("`%s`: `%s`" % (self.name, line))

                data = line.split(Protocol.SEPARATOR)
                try:
                    route = self.server.routes[data[0]]
                    if len(data) >= 2:
                        getattr(self.server, route['method'])(self.client, *data[1:])
                    else:
                        getattr(self.server, route['method'])(self.client)
                except (KeyError, TypeError):
                    raise ClientError('Invalid command `%s`, refer to protocol' % line)
        except ServerError as e:
            Helpers.error_and_whatsapp('500 Internal Server Error: `%s`' % e)
            self.socket.send('%s 500 Internal Server Error: `%s`%s' % (Protocol.ERROR, e, Protocol.EOL))
        except ClientError as e:
            Helpers.error_and_whatsapp('Client `%s` made a 400 Bad Request: `%s`' % (self.name, e))
            self.socket.send('%s 400 Bad Request: `%s`%s' % (Protocol.ERROR, e, Protocol.EOL))
        except IOError as e:
            Helpers.error_and_whatsapp('Connection error `%s` with %s' % (e, self.name))
        finally:
            Helpers.log_and_whatsapp('Connection lost with %s' % self.name)
            self.socket.close()

            if hasattr(self, 'client'):
                self.server.disconnect(self.client)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    port = 3535
    config = ConfigParser.ConfigParser()
    config.read('config')
    if config.has_option('server', 'port'):
        port = config.getint('server', 'port')

    sock.bind(('0.0.0.0', port))
    sock.listen(1)

    server = Server()

    Helpers.log_and_whatsapp('A Rolit server has started for `%s` on port %s' % (socket.gethostname(), port))

    while True:
        conn, client_address = sock.accept()
        Helpers.log_and_whatsapp('Connection established with %s' % str(client_address))
        thread = ClientHandler(server, conn, client_address)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    main()
