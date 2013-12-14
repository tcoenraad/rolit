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
    self.clients.append({ 'client' : client, 'name' : name})

  def join(self, client, amount_of_players):
    if amount_of_players < 2 or amount_of_players > 4:
      raise InputError("A game is played with 2 to 4 players")

    self.join_list[amount_of_players].append(client)

    if len(self.join_list[amount_of_players]) == amount_of_players:
      self.start_game(self.join_list[amount_of_players])
      self.join_list[amount_of_players] = []

  def start_game(self, clients):
    if len(clients) == 2:
      game = TwoPlayerGame()
    elif len(clients) == 3:
      game = ThreePlayerGame()
    elif len(clients) == 4:
      game = FourPlayerGame()

    random.shuffle(clients)

    game_id = id(game)
    self.games[game_id] = { 'clients' : clients, 'game' : game }
    for client in clients:
      client['game_id'] = game_id
      client['socket'].send("%s %s" % (Protocol.START, ' '.join(str(c) for c in clients)))

    clients[0]['socket'].send(Protocol.PLAY)

  def place(self, client, x, y, color):
    game = self.games[client['game_id']]

    if game['game'].current_player != game['clients'].index(client):
      raise InputError("It is not the turn for this player")

    try:
      game['game'].place(x, y, Protocol.COLORS[color])
    except GameOverError:
      for client in game['clients']:
        client['socket'].send("%s %s" % (Protocol.GAME_OVER, ' '.join(game['clients'][p]['name'] for p in game['game'].winning_players())))
        client['game_id'] = None

class InputError(Exception): pass
