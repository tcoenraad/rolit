import pytest, time
from mock import Mock, call, patch

from models.server import *

@patch.object(random, 'shuffle', Mock())
class TestServer():

  def setup_method(self, method):
    self.server = Server()

    self.mocked_clients = [{ 'socket' : Mock(), 'name' : "Met TOM op de koffie!"},
                           { 'socket' : Mock(), 'name' : "Yorinf"},
                           { 'socket' : Mock(), 'name' : "Tegel 14"},
                           { 'socket' : Mock(), 'name' : "Lalala geld"},
                           { 'socket' : Mock(), 'name' : "IEOEDMB"}]

    self.clients = []
    for client in self.mocked_clients:
      self.clients.append(self.server.connect(client['socket'], client['name']))

  def test_it_overwrite_joins(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], '2')
    self.server.join(self.clients[0], '2')
    self.server.join(self.clients[1], '2')

    self.server.start_game.assert_called_once_with([self.clients[0], self.clients[1]])

  def test_it_validates_name_is_unique(self):
    with pytest.raises(ServerError):
      self.server.connect(Mock(), "Met TOM op de koffie!")

    self.server.disconnect(self.clients[0])
    self.server.connect(Mock(), "Met TOM op de koffie!")

  def test_it_validates_requested_number_of_player(self):
    with pytest.raises(ClientError):
      self.server.join(self.clients[0], '1')
    with pytest.raises(ClientError):
      self.server.join(self.clients[0], '5')

  def test_it_validates_number_is_a_number(self):
    with pytest.raises(ClientError):
      self.server.join(self.clients[0], 'vijfendertig')

  def test_it_validates_dimension_of_board(self):
    self.server.start_game([self.clients[0], self.clients[1]])
    with pytest.raises(ClientError):
      self.server.place(self.clients[0], '-1', Protocol.RED)
    with pytest.raises(ClientError):
      self.server.place(self.clients[0], '88', Protocol.RED)

  def test_it_validates_colors_on_placement(self):
    self.server.start_game([self.clients[0], self.clients[1]])
    with pytest.raises(ClientError):
      self.server.place(self.clients[0], '53', 'Inter-/Actief/-blauw')

  def test_it_validates_client_is_in_game(self):
    with pytest.raises(ClientError):
      self.server.place(self.clients[0], '53', Protocol.RED)

    game = self.server.start_game([self.clients[0], self.clients[1]])
    game.balls_left = 1

    self.server.place(self.clients[0], '53', Protocol.RED)
    with pytest.raises(ClientError):
      self.server.place(self.clients[0], '53', Protocol.RED)

  def test_it_validates_it_is_clients_turn(self):
    self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
    with pytest.raises(ClientError):
      self.server.place(self.clients[1], '52', Protocol.YELLOW)

  def test_game_goes_game_overs_on_disconnect(self):
    self.server.start_game([self.clients[0], self.clients[1]])
    self.server.disconnect(self.clients[1])

    args = "%s %s %s%s" % (Protocol.GAME_OVER, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)
    self.clients[0]['socket'].send.assert_has_calls(call(args))

  def test_it_joins_for_two_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], '2')
    self.server.join(self.clients[1], '2')
    self.server.join(self.clients[2], '2')
    self.server.start_game.assert_called_with([self.clients[0], self.clients[1]])

    self.server.join(self.clients[3], '2')
    self.server.start_game.assert_called_with([self.clients[2], self.clients[3]])

  def test_it_joins_for_three_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], '3')
    self.server.join(self.clients[1], '3')
    self.server.join(self.clients[2], '3')
    self.server.join(self.clients[3], '3')

    self.server.start_game.assert_called_once_with([self.clients[0], self.clients[1], self.clients[2]])

  def test_it_joins_for_four_players(self):
    self.server.start_game = Mock()

    self.server.join(self.clients[0], '4')
    self.server.join(self.clients[1], '4')
    self.server.join(self.clients[2], '4')
    self.server.join(self.clients[3], '4')
    self.server.join(self.clients[4], '4')

    self.server.start_game.assert_called_once_with([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])

  def test_it_starts_for_two_players(self):
    self.server.start_game([self.clients[0], self.clients[1]])

    args = "%s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)
    self.clients[0]['socket'].send.assert_has_calls(call(args))
    self.clients[0]['socket'].send.assert_has_calls(call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[1]['socket'].send.assert_called_once_with(args)
    assert self.clients[2]['socket'].send.call_count == 0

  def test_it_starts_for_three_players(self):
    self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
    
    args = "%s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], Protocol.EOL)
    self.clients[0]['socket'].send.assert_has_calls(call(args))
    self.clients[0]['socket'].send.assert_has_calls(call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[1]['socket'].send.assert_called_once_with(args)
    self.clients[2]['socket'].send.assert_called_once_with(args)
    assert self.clients[3]['socket'].send.call_count == 0
  
  def test_it_starts_for_four_players(self):
    self.server.start_game([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])

    args = "%s %s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], self.clients[3]['name'], Protocol.EOL)
    self.clients[0]['socket'].send.assert_has_calls(call(args))
    self.clients[0]['socket'].send.assert_has_calls(call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[1]['socket'].send.assert_called_once_with(args)
    self.clients[2]['socket'].send.assert_called_once_with(args)
    self.clients[3]['socket'].send.assert_called_once_with(args)
    assert self.clients[4]['socket'].send.call_count == 0

  def test_it_places_for_two_players(self):
    game = self.server.start_game([self.clients[0], self.clients[1]])
    game.balls_left = 1

    self.server.place(self.clients[0], '53', Protocol.RED)

    args = [call("%s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)),
      call("%s %s %s%s" % (Protocol.PLACE, Protocol.RED, '53', Protocol.EOL)),
      call("%s %s%s" % (Protocol.GAME_OVER, self.clients[0]['name'], Protocol.EOL))]

    args.insert(1, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[0]['socket'].send.assert_has_calls(args)

    args.pop(1)
    self.clients[1]['socket'].send.assert_has_calls(args)
    assert self.clients[2]['socket'].send.call_count == 0

  def test_it_places_for_three_players(self):
    game = self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
    game.balls_left = 2

    self.server.place(self.clients[0], '53', Protocol.RED)
    self.server.place(self.clients[1], '52', Protocol.YELLOW)

    args = [call("%s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], Protocol.EOL)),
      call("%s %s %s%s" % (Protocol.PLACE, Protocol.RED, '53', Protocol.EOL)),
      call("%s %s %s%s" % (Protocol.PLACE, Protocol.YELLOW, '52', Protocol.EOL)),
      call("%s %s%s" % (Protocol.GAME_OVER, self.clients[1]['name'], Protocol.EOL))]
    
    args.insert(1, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[0]['socket'].send.assert_has_calls(args)

    args.pop(1)
    args.insert(2, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
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

    args = [call("%s %s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], self.clients[3]['name'], Protocol.EOL)),
      call("%s %s %s%s" % (Protocol.PLACE, Protocol.RED, '53', Protocol.EOL)),
      call("%s %s %s%s" % (Protocol.PLACE, Protocol.YELLOW, '52', Protocol.EOL)),
      call("%s %s %s%s" % (Protocol.PLACE, Protocol.BLUE, '54', Protocol.EOL)),
      call("%s %s%s" % (Protocol.GAME_OVER, self.clients[1]['name'], Protocol.EOL))]

    args.insert(1, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[0]['socket'].send.assert_has_calls(args)

    args.pop(1)
    args.insert(2, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[1]['socket'].send.assert_has_calls(args)

    args.pop(2)
    args.insert(3, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
    self.clients[2]['socket'].send.assert_has_calls(args)

    args.pop(3)
    self.clients[3]['socket'].send.assert_has_calls(args)
    assert self.clients[4]['socket'].send.call_count == 0

  def test_it_gives_the_right_date_stats(self):
    game = self.server.start_game([self.clients[0], self.clients[1]])
    self.server.place(self.clients[0], '53', Protocol.RED)
    self.server.game_over(self.server.network_games[id(game)])

    self.server.stats(self.clients[0], Protocol.STAT_DATE, time.time())

    args = "%s %s %s%s" % (Protocol.STAT, self.clients[0]['name'], '1', Protocol.EOL)
    self.clients[0]['socket'].send.assert_has_calls(call(args))

  def test_it_gives_the_right_player_stats(self):
    game = self.server.start_game([self.clients[0], self.clients[1]])
    self.server.place(self.clients[0], '53', Protocol.RED)
    self.server.game_over(self.server.network_games[id(game)])

    self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[0]['name'])
    self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[1]['name'])

    args = [call("%s %s %s%s" % (Protocol.STAT, self.clients[0]['name'], '1', Protocol.EOL)),
            call("%s %s %s%s" % (Protocol.STAT, self.clients[1]['name'], '0', Protocol.EOL))]
    self.clients[0]['socket'].send.assert_has_calls(args)
