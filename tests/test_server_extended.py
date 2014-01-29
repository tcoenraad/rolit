import pytest
from mock import Mock, call, patch

from rolit.server import *
from test_server import TestServer

@patch.object(random, 'shuffle', Mock())
class TestServerExtended(TestServer):

    def test_send_games(self):
        self.server.send_games(self.clients[0])
        args = call("%s %s%s" % (ProtocolExtended.GAMES, Protocol.UNDEFINED, Protocol.EOL))
        self.clients[0]['socket'].sendall.assert_has_calls(args)

        game = self.start_game_with_two_players()
        self.server.send_games(self.clients[0])

        args = call("%s %s%s" % (ProtocolExtended.GAMES, id(game), Protocol.EOL))
        self.clients[0]['socket'].sendall.assert_has_calls(args)

    def test_send_game_players(self):
        game = self.start_game_with_two_players()
        self.server.send_game_players(self.clients[0], 'Inter-Actief')
        self.server.send_game_players(self.clients[0], id(game))

        args = [call("%s %s %s%s" % (ProtocolExtended.GAME_PLAYERS, 'Inter-Actief', Protocol.UNDEFINED, Protocol.EOL)),
                call("%s %s %s %s%s" % (ProtocolExtended.GAME_PLAYERS, id(game), self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL))]

        self.clients[0]['socket'].sendall.assert_has_calls(args)

    def test_send_game_board(self):
        game = self.start_game_with_two_players()
        self.server.send_game_board(self.clients[0], 'Inter-Actief')
        self.server.send_game_board(self.clients[0], id(game))

        args = [call("%s %s %s%s" % (ProtocolExtended.GAME_BOARD, 'Inter-Actief', Protocol.UNDEFINED, Protocol.EOL)),
                call("%s %s %s%s" % (ProtocolExtended.GAME_BOARD, id(game), game.board.encode(), Protocol.EOL))]
        self.clients[0]['socket'].sendall.assert_has_calls(args)
