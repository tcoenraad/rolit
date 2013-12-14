import pytest
from mock import Mock

from models.server import *

class TestServer():

  def setup_method(self, method):
    self.server = Server()

    self.clients = []
    self.clients.append({ 'socket' : Mock(), 'name' : "Bestuur 35!"} )
    self.clients.append({ 'socket' : Mock(), 'name' : "Yorinf"} )
    self.clients.append({ 'socket' : Mock(), 'name' : "Tegel 14"} )
    self.clients.append({ 'socket' : Mock(), 'name' : "Lalala geld"} )

    for client in self.clients:
      client['socket'].send = Mock()

    self.server.clients = self.clients

  def test_it_checks_user_input(self):
    with pytest.raises(InputError):
      self.server.join(self.clients[0], 1)
    with pytest.raises(InputError):
      self.server.join(self.clients[0], 5)

  def test_join_for_two_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], 2)
    self.server.join(self.clients[1], 2)
    self.server.join(self.clients[2], 2)
    self.server.start_game.assert_called_once_with([self.clients[0], self.clients[1]])

  def test_join_for_three_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], 3)
    self.server.join(self.clients[1], 3)
    self.server.join(self.clients[2], 3)
    self.server.join(self.clients[3], 3)
    self.server.start_game.assert_called_once_with([self.clients[0], self.clients[1], self.clients[2]])

  def test_join_for_four_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], 4)
    self.server.join(self.clients[1], 4)
    self.server.join(self.clients[2], 4)
    self.server.join(self.clients[3], 4)
    self.server.start_game.assert_called_once_with([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])

  def test_two_player_game(self):
    game = TwoPlayerGame()
    game_id = id(game)
    game.balls_left = 1

    game_clients = [self.clients[0], self.clients[1]]
    self.server.games[game_id] = {'game' : game, 'clients' : game_clients}

    for client in game_clients:
      client['game_id'] = game_id

    self.server.place(self.clients[0], 5, 3, Protocol.RED)

    self.clients[0]['socket'].send.assert_called_once_with("%s %s" % (Protocol.GAME_OVER, self.clients[0]['name']))
    self.clients[1]['socket'].send.assert_called_once_with("%s %s" % (Protocol.GAME_OVER, self.clients[0]['name']))
