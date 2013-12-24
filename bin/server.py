import socket, sys, threading
from termcolor import colored

from models.server import *
from models.protocol import Protocol

def notice(notification):
  print(colored(notification, 'blue'))

def warning(notification):
  print(colored(notification, 'yellow'))

def error(notification):
  print(colored(notification, 'red'))

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
      self.client = server.connect(self.socket, data[1])
      self.name = self.client['name']
      notice('Client %s introduced itself as `%s`' % (self.client_address, self.name))

      while True:
        data = self.socket.recv(4096).strip().split(Protocol.SEPARATOR)
    
        if not data:
          break

        if data[0] == Protocol.JOIN and len(data) == 2:
          server.join(self.client, data[1])
        elif data[0] == Protocol.PLACE and len(data) == 3:
          server.place(self.client, data[1], data[2])
        else:
          raise ClientError('Invalid command `%s`, refer to protocol' % data)
    except ServerError as e:
      error('500 Internal Server Error: `%s`' % e)
      self.socket.send('500 Internal Server Error: `%s`%s' % (e, Protocol.EOL))
    except ClientError as e:
      warning('Client `%s` made a 400 Bad Request: `%s`%s' % (self.name, e, Protocol.EOL))
      self.socket.send('400 Bad Request: `%s`%s' % (e, Protocol.EOL))
    finally:
      print('Connection lost with %s' % self.name)
      self.socket.close()

      if hasattr(self, 'client'):
        server.disconnect(self.client)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

port = 3535
if len(sys.argv) >= 2 and sys.argv[1].isdigit():
  port = int(sys.argv[1])

sock.bind(('0.0.0.0', port))
sock.listen(1)

server = Server()

print('Server started on port %s' % port)

while True:
  socket, client_address = sock.accept()
  print('Connection established with %s' % str(client_address))
  thread = ClientHandler(socket, client_address)
  thread.daemon = True
  thread.start()
