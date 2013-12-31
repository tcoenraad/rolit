import pytest, time
from mock import Mock, call, patch

from models.server import *

@patch.object(random, 'shuffle', Mock())
class TestServer():

    def setup_method(self, method):
        self.server = Server()

        self.mocked_clients = [{ 'socket' : Mock(), 'name' : "Met_TOM_op_de_koffie!", 'chat' : Protocol.TRUE,  'challenge' : Protocol.TRUE },
                               { 'socket' : Mock(), 'name' : "Yorinf",                'chat' : Protocol.TRUE,  'challenge' : Protocol.TRUE },
                               { 'socket' : Mock(), 'name' : "Tegel_14",              'chat' : Protocol.TRUE,  'challenge' : Protocol.FALSE },
                               { 'socket' : Mock(), 'name' : "Lalala_geld",           'chat' : Protocol.FALSE, 'challenge' : Protocol.FALSE },
                               { 'socket' : Mock(), 'name' : "IEOEDMB",               'chat' : Protocol.FALSE, 'challenge' : Protocol.TRUE }]

        self.clients = []
        for client in self.mocked_clients:
            self.clients.append(self.server.connect(client['socket'], client['name'], client['chat'], client['challenge']))

    def test_send_games(self):
        game = self.server.start_game([self.clients[0], self.clients[1]])
        self.server.send_games(self.clients[0])

        args = "%s %s%s" % (ProtocolExtended.GAMES, id(game), Protocol.EOL)
        self.clients[0]['socket'].send.assert_has_calls(call(args))

    def test_send_game_players(self):
        game = self.server.start_game([self.clients[0], self.clients[1]])
        self.server.send_game_players(self.clients[0], id(game))

        args = "%s %s %s%s" % (ProtocolExtended.GAME_PLAYERS, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)
        self.clients[0]['socket'].send.assert_has_calls(call(args))

    def test_send_game_players(self):
        game = self.server.start_game([self.clients[0], self.clients[1]])
        self.server.send_game_players(self.clients[0], id(game))

        args = "%s %s %s%s" % (ProtocolExtended.GAME_PLAYERS, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)
        self.clients[0]['socket'].send.assert_has_calls(call(args))

    def test_send_game_board(self):
        game = self.server.start_game([self.clients[0], self.clients[1]])
        self.server.send_game_board(self.clients[0], id(game))

        args = "%s %s%s" % (ProtocolExtended.GAME_BOARD, game.board.encode(), Protocol.EOL)
        self.clients[0]['socket'].send.assert_has_calls(call(args))
