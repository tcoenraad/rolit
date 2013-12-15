import random

from models.games import *
from models.protocol import Protocol
from models.game import *

class Server:
  def __init__(self):
    self.clients = []
    self.games = {}
    self.join_list = { 2 : [], 3 : [], 4 : [] }
    self.challenge_list = {}

  def connect(self, client, name):
    if self.get_client(name):
      raise ServerError("Given name is already in use")
    self.clients.append({ 'socket' : client, 'name' : name})

  def get_client(self, name):
    for client in self.clients:
      if client['name'] == name:
        return client
    return False

  def disconnect(self, client):
    self.clients.remove(client)

  def join(self, client, number_of_players):
    if number_of_players < 2 or number_of_players > 4:
      raise UserError("A game is played with 2 to 4 players")

    clients = self.join_list[number_of_players]
    clients.append(client)

    if len(clients) == number_of_players:
      random.shuffle(clients)
      self.start_game(clients)
      self.join_list[number_of_players] = []

  def start_game(self, clients):
    if len(clients) == 2:
      game = TwoPlayerGame()
    elif len(clients) == 3:
      game = ThreePlayerGame()
    elif len(clients) == 4:
      game = FourPlayerGame()

    game_id = id(game)
    self.games[game_id] = { 'clients' : clients, 'game' : game }

    for client in clients:
      client['game_id'] = game_id
      client['socket'].send("%s %s" % (Protocol.START, ' '.join(c['name'] for c in clients)))

    clients[0]['socket'].send(Protocol.PLAY)

    return game

  def place(self, client, coord, color):
    x = int(coord[0])
    y = int(coord[1])

    if 'game_id' not in client:
      raise UserError("Client is not in-game")

    game = self.games[client['game_id']]
    if game['game'].current_player != game['clients'].index(client):
      raise UserError("Client is not current player of game")

    for client in game['clients']:
      client['socket'].send("%s %s %s" % (Protocol.PLACE, color, coord))

    try:
      game['game'].place(x, y, Protocol.COLORS[color])
      game['clients'][game['game'].current_player]['socket'].send(Protocol.PLAY)
    except GameOverError:
      for client in game['clients']:
        client['socket'].send("%s %s" % (Protocol.GAME_OVER, ' '.join(game['clients'][p]['name'] for p in game['game'].winning_players())))
        del(client['game_id'])

class ServerError(Exception): pass
class UserError(Exception): pass
