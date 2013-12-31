import socket
import readline

from models.client import Client
from models.protocol import Protocol

client = Client(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
client.socket.connect(('localhost', 3535))

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
