from models.board import Board

from models.protocol import Protocol
from models.protocol_extended import ProtocolExtended
from models.helpers import Helpers

class Client(object):

    def __init__(self, socket):
        self.socket = socket
        self.options = { 1 : { 'method': 'get_games', 'args': 0, 'description': "Get all running games" },
                         2 : { 'method': 'get_game_players', 'args': 1, 'description': "<id> Show game players" },
                         3 : { 'method': 'get_game_board', 'args': 1, 'description': "<id> Show game board" },
                         4 : { 'method': 'menu', 'args': 0, 'description': "Show this help menu" } }

    def menu(self):
        Helpers.notice('-' * 16)
        for (key, value) in self.options.iteritems():
            print("%s %s" % (key, value['description']))
        Helpers.notice('-' * 16)

    def response(self):
        return self.socket.recv(4096)

    def print_response(self):
        response = self.response().strip().split(Protocol.SEPARATOR)
        response.pop(0)
        print(", ".join(response))

    def get_games(self):
        self.socket.send("%s%s" % (ProtocolExtended.GAMES, Protocol.EOL))
        print("The following game ids are running:")
        self.print_response()

    def get_game_players(self, game_id):
        self.socket.send("%s %s%s" % (ProtocolExtended.GAME_PLAYERS, game_id, Protocol.EOL))

        print("The following players are in game %s active:" % game_id)
        self.print_response()

    def get_game_board(self, game_id):
        self.socket.send("%s %s%s" % (ProtocolExtended.GAME_BOARD, game_id, Protocol.EOL))

        print("The board for game %s looks like:" % game_id)
        board = self.response().strip().split(Protocol.SEPARATOR)
        board.pop(0)
        print Board.decode(Protocol.SEPARATOR.join(board))
