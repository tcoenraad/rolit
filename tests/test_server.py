import pytest
import mock
from mock import Mock, call

from models.server import *

class TestServer():

  def setup_method(self, method):
    self.server = Server()

    self.clients = []
    self.clients.append({ 'socket' : Mock(), 'name' : "Bestuur 35!"} )
    self.clients.append({ 'socket' : Mock(), 'name' : "Yorinf"} )
    self.clients.append({ 'socket' : Mock(), 'name' : "Tegel 14"} )
    self.clients.append({ 'socket' : Mock(), 'name' : "Lalala geld"} )
    self.clients.append({ 'socket' : Mock(), 'name' : "Met TOM op de koffie!"} )

    for client in self.clients:
      client['socket'].send = Mock()

    self.server.clients = self.clients

  def test_it_validates_requested_number_of_player(self):
    with pytest.raises(InputError):
      self.server.join(self.clients[0], 1)
    with pytest.raises(InputError):
      self.server.join(self.clients[0], 5)

  def test_it_validates_client_is_in_game(self):
    with pytest.raises(InputError):
      self.server.place(self.clients[0], '53', Protocol.RED)

    game = self.server.start_game([self.clients[0], self.clients[1]])
    game.balls_left = 1

    self.server.place(self.clients[0], '53', Protocol.RED)
    with pytest.raises(InputError):
      self.server.place(self.clients[0], '53', Protocol.RED)

  def test_it_validates_it_is_clients_turn(self):
    self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
    with pytest.raises(InputError):
      self.server.place(self.clients[1], '52', Protocol.YELLOW)

  def test_it_joins_for_two_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], 2)
    self.server.join(self.clients[1], 2)
    self.server.join(self.clients[2], 2)
    assert sorted(self.server.start_game.call_args[0][0]) == sorted([self.clients[0], self.clients[1]])

    self.server.join(self.clients[3], 2)
    assert sorted(self.server.start_game.call_args[0][0]) == sorted([self.clients[2], self.clients[3]])

  def test_it_joins_for_three_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], 3)
    self.server.join(self.clients[1], 3)
    self.server.join(self.clients[2], 3)
    self.server.join(self.clients[3], 3)

    assert sorted(self.server.start_game.call_args[0][0]) == sorted([self.clients[0], self.clients[1], self.clients[2]])

  def test_it_joins_for_four_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], 4)
    self.server.join(self.clients[1], 4)
    self.server.join(self.clients[2], 4)
    self.server.join(self.clients[3], 4)
    self.server.join(self.clients[4], 4)

    assert sorted(self.server.start_game.call_args[0][0]) == sorted([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])

  def test_it_starts_for_two_players(self):
    self.server.start_game([self.clients[0], self.clients[1]])
    args = "%s %s %s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'])

    self.clients[0]['socket'].send.assert_has_calls(call(args))
    self.clients[0]['socket'].send.assert_has_calls(call("%s" % (Protocol.PLAY)))
    self.clients[1]['socket'].send.assert_called_once_with(args)
    assert self.clients[2]['socket'].send.call_count == 0

  def test_it_starts_for_three_players(self):
    self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
    args = "%s %s %s %s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'])

    self.clients[0]['socket'].send.assert_has_calls(call(args))
    self.clients[0]['socket'].send.assert_has_calls(call("%s" % (Protocol.PLAY)))
    self.clients[1]['socket'].send.assert_called_once_with(args)
    self.clients[2]['socket'].send.assert_called_once_with(args)
    assert self.clients[3]['socket'].send.call_count == 0
  
  def test_it_starts_for_four_players(self):
    self.server.start_game([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])
    args = "%s %s %s %s %s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], self.clients[3]['name'])

    self.clients[0]['socket'].send.assert_has_calls(call(args))
    self.clients[0]['socket'].send.assert_has_calls(call("%s" % (Protocol.PLAY)))
    self.clients[1]['socket'].send.assert_called_once_with(args)
    self.clients[2]['socket'].send.assert_called_once_with(args)
    self.clients[3]['socket'].send.assert_called_once_with(args)
    assert self.clients[4]['socket'].send.call_count == 0

  def test_it_places_for_two_players(self):
    game = self.server.start_game([self.clients[0], self.clients[1]])
    game.balls_left = 1

    self.server.place(self.clients[0], '53', Protocol.RED)

    args = [call("%s %s %s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'])),
      call("%s %s %s" % (Protocol.PLACE, Protocol.RED, '53')),
      call("%s %s" % (Protocol.GAME_OVER, self.clients[0]['name']))]

    args.insert(1, call(Protocol.PLAY))
    self.clients[0]['socket'].send.assert_has_calls(args)

    args.pop(1)
    self.clients[1]['socket'].send.assert_has_calls(args)
    assert self.clients[2]['socket'].send.call_count == 0

  def test_it_places_for_three_players(self):
    game = self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
    game.balls_left = 2

    self.server.place(self.clients[0], '53', Protocol.RED)
    self.server.place(self.clients[1], '52', Protocol.YELLOW)

    args = [call("%s %s %s %s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'])),
      call("%s %s %s" % (Protocol.PLACE, Protocol.RED, '53')),
      call("%s %s %s" % (Protocol.PLACE, Protocol.YELLOW, '52')),
      call("%s %s" % (Protocol.GAME_OVER, self.clients[1]['name']))]
    
    args.insert(1, call(Protocol.PLAY))
    self.clients[0]['socket'].send.assert_has_calls(args)

    args.pop(1)
    args.insert(2, call(Protocol.PLAY))
    self.clients[1]['socket'].send.assert_has_calls(args)

    args.pop(2)
    self.clients[2]['socket'].send.assert_has_calls(args)
    assert self.clients[3]['socket'].send.call_count == 0

  def test_it_places_for_four_players(self):
    game = self.server.start_game([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])
    game.balls_left = 3

    self.server.place(self.clients[0], '53', Protocol.RED)
    self.server.place(self.clients[1], '52', Protocol.YELLOW)
    self.server.place(self.clients[2], '54', Protocol.BLUE)

    args = [call("%s %s %s %s %s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], self.clients[3]['name'])),
      call("%s %s %s" % (Protocol.PLACE, Protocol.RED, '53')),
      call("%s %s %s" % (Protocol.PLACE, Protocol.YELLOW, '52')),
      call("%s %s %s" % (Protocol.PLACE, Protocol.BLUE, '54')),
      call("%s %s" % (Protocol.GAME_OVER, self.clients[1]['name']))]

    args.insert(1, call(Protocol.PLAY))
    self.clients[0]['socket'].send.assert_has_calls(args)

    args.pop(1)
    args.insert(2, call(Protocol.PLAY))
    self.clients[1]['socket'].send.assert_has_calls(args)

    args.pop(2)
    args.insert(3, call(Protocol.PLAY))
    self.clients[2]['socket'].send.assert_has_calls(args)

    args.pop(3)
    self.clients[3]['socket'].send.assert_has_calls(args)
    assert self.clients[4]['socket'].send.call_count == 0
