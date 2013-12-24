import random, datetime

from models.games import *
from models.game import *
from models.protocol import Protocol
from models.leaderboard import Leaderboard

class Server(object):
  def __init__(self):
    self.leaderboard = Leaderboard()
    self.clients = []
    self.network_games = {}
    self.join_list = { 2 : [], 3 : [], 4 : [] }
    self.challenge_list = {}

  def connect(self, socket, name):
    if self.get_client(name):
      raise ServerError("Given name is already in use")

    client = { 'socket' : socket, 'name' : name}
    self.clients.append(client)
    return client

  def get_client(self, name):
    for client in self.clients:
      if client['name'] == name:
        return client
    return False

  def disconnect(self, client):
    self.clients.remove(client)

    if 'game_id' in client:
      self.game_over(self.network_games[client['game_id']])

  def join(self, client, number_of_players):
    if not number_of_players.isdigit():
      raise ClientError("Given number is not a number")
    number_of_players = int(number_of_players)

    if number_of_players < 2 or number_of_players > 4:
      raise ClientError("A game is played with 2 to 4 players")

    for clients in self.join_list.values():
      if client in clients:
        clients.remove(client)

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
    self.network_games[game_id] = { 'clients' : clients, 'game' : game }

    for client in clients:
      client['game_id'] = game_id
      client['socket'].send("%s %s%s" % (Protocol.START, ' '.join(c['name'] for c in clients), Protocol.EOL))

    clients[0]['socket'].send("%s%s" % (Protocol.PLAY, Protocol.EOL))

    return game

  def place(self, client, coord, color):
    if color not in Protocol.COLORS:
      raise ClientError("Given color `%s` is not valid, refer to protocol" % color)

    if not coord[0].isdigit() or not coord[1].isdigit():
      raise ClientError("Given coordinate `%s` is not an integer, refer to protocol" % coord)

    x = int(coord[0])
    y = int(coord[1])

    if x < 0 or x >= Board.DIM or y < 0 or y >= Board.DIM:
      raise ClientError("Given coordinate `%s` does not exist on board, refer to protocol" % coord)

    if 'game_id' not in client:
      raise ClientError("Client is not in-game, refer to protocol")

    network_game = self.network_games[client['game_id']]
    if network_game['game'].current_player != network_game['clients'].index(client):
      raise ClientError("Client is not current player of game, refer to protocol")

    for client in network_game['clients']:
      client['socket'].send("%s %s %s%s" % (Protocol.PLACE, color, coord, Protocol.EOL))

    try:
      network_game['game'].place(x, y, Protocol.COLORS[color])
      network_game['clients'][network_game['game'].current_player]['socket'].send("%s%s" % (Protocol.PLAY, Protocol.EOL))
    except (GameOverError, ClientError):
      self.game_over(network_game)

  def game_over(self, network_game):
    for client in network_game['clients']:
      if client in self.clients:
        winning_players = network_game['game'].winning_players()
        winning_clients = [network_game['clients'][p] for p in winning_players]

        client['socket'].send("%s %s%s" % (Protocol.GAME_OVER, ' '.join(client['name'] for client in winning_clients), Protocol.EOL))

        if client in winning_clients:
          self.leaderboard.add_score(client['name'], datetime.datetime.now(), 1)
        else:
          self.leaderboard.add_score(client['name'], datetime.datetime.now(), 0)
        del(client['game_id'])

  def stats(self, client, stat, arg):
    if stat == Protocol.STAT_DATE:
      score = self.leaderboard.best_score_of_date(datetime.datetime.fromtimestamp(arg))
      client['socket'].send("%s %s %s%s" % (Protocol.STAT, score.name, score.score, Protocol.EOL))
    elif stat == Protocol.STAT_PLAYER:
      score = self.leaderboard.best_score_of_player(arg)
      client['socket'].send("%s %s %s%s" % (Protocol.STAT, score.name, score.score, Protocol.EOL))
    else:
      raise ClientError("Given stat `%s` is not recognized, refer to protocol" % stat)

class ServerError(Exception): pass
class ClientError(Exception): pass
