import copy
import time
import datetime
import parsedatetime.parsedatetime as pdt

from rolit.game import GameOverError
from rolit.games import TwoPlayerGame, ThreePlayerGame, FourPlayerGame
from rolit.board import Board, BoardError

from rolit.helpers import Helpers
from rolit.protocol import Protocol
from rolit.protocol_extended import ProtocolExtended

class Client(object):

    class Router(object):

        routes = { Protocol.HANDSHAKE : { 'method' : 'HANDSHAKE' },
                   Protocol.START : { 'method' : 'start' },
                   Protocol.PLAY : { 'method' : 'play' },
                   Protocol.PLACE : { 'method' : 'place' },
                   Protocol.GAME_OVER : { 'method' : 'game_over' },
                   Protocol.CHAT : { 'method' : 'chat' },
                   Protocol.STATS : { 'method' : 'stats' },
                   ProtocolExtended.GAMES : { 'method' : 'games' },
                   ProtocolExtended.GAME_PLAYERS : { 'method' : 'game_players' },
                   ProtocolExtended.GAME_BOARD : { 'method' : 'game_board' } }

        def __init__(self, client):
            self.client = client

        @staticmethod
        def error(message):
            print("Oops, that is an error!")
            print("`%s`" % message)

        def play(self):
            if self.client.auto_fire:
                self.client.ai()
            else:
                print("You may now enter a coord!")
                print("x <xy> [autofire once with `a`, enable auto_fire with `xa`, disable with `xm`]")

        def place(self, coord):
            x, y = Protocol.coord_str(coord[0])
            print("A move is done at x=%s, y=%s" % (x, y))
            try:
                self.client.game.place(x, y)
            except GameOverError:
                pass
            except BoardError:
                print("An invalid move is made!")

            print(self.client.game.board)

        def game_over(self, players):
            print("Game is over, winners were:")
            print(players)

        def start(self, players):
            print("A game has started!")
            print("Players are: %s" % players)
            number_of_players = len(players)
            if number_of_players == 2:
                self.client.game = TwoPlayerGame()
            elif number_of_players == 3:
                self.client.game = ThreePlayerGame()
            elif number_of_players == 4:
                self.client.game = FourPlayerGame()
            print(self.client.game.board)

        @staticmethod
        def HANDSHAKE(options):
            print("Connected established")
            print("Chat = %s and challenge = %s" % (options[0] == Protocol.TRUE, options[1] == Protocol.TRUE))

        @staticmethod
        def games(games):
            print("The following game ids are running:")
            print(games)

        @staticmethod
        def game_players(players):
            print("The following players are in game `%s` active:" % players[0])
            print(players[1:])

        @staticmethod
        def game_board(board):
            print("The board for game `%s` looks like:" % board[0])
            print Board.decode(Protocol.SEPARATOR.join(board[1:]))

        @staticmethod
        def stats(options):
            if options[0] == Protocol.STAT_DATE:
                print("The following player was at date `%s` best player:" % datetime.datetime.fromtimestamp(int(options[1])).strftime("%c"))
                print(options[2:])
            
            elif options[0] == Protocol.STAT_PLAYER:
                print("The following score was best of player `%s` best player:" % options[1])
                print(options[2:])

    options = { '0' : { 'method': 'menu', 'args': 0, 'description': "Show this help menu" },
                '1' : { 'method': 'get_games', 'args': 0, 'description': "Get all running games" },
                '2' : { 'method': 'get_game_players', 'args': 1, 'description': "<id> Show game players" },
                '3' : { 'method': 'get_game_board', 'args': 1, 'description': "<id> Show game board" },
                '4' : { 'method': 'get_stat_date', 'args': 1, 'description': "<date> Show best player on that date" },
                '5' : { 'method': 'get_stat_player', 'args': 1, 'description': "<player> Show best score of that player" },
                '6' : { 'method': 'join', 'args': 1, 'description': "<2-4> Join a game with that many players" },
                'x' : { 'method': 'place', 'args': 1, 'hidden': True },
                'xa': { 'method': 'enable_ai', 'args': 0, 'hidden': True },
                'xm': { 'method': 'disable_ai', 'args': 0, 'hidden': True },
                'a' : { 'method': 'ai', 'args': 0, 'hidden': True }
               }

    def __init__(self, socket):
        self.socket = socket
        self.auto_fire = False
        self.router = Client.Router(self)

    @staticmethod
    def menu():
        Helpers.notice('-' * 16)
        for key in sorted(Client.options.keys()):
            value = Client.options[key]
            if 'hidden' in value.keys():
                continue
            print("%s|%s" % (key, value['description']))
        Helpers.notice('-' * 16)

    def get_games(self):
        self.socket.send("%s%s" % (ProtocolExtended.GAMES, Protocol.EOL))

    def get_game_players(self, game_id):
        self.socket.send("%s %s%s" % (ProtocolExtended.GAME_PLAYERS, game_id[0], Protocol.EOL))

    def get_game_board(self, game_id):
        self.socket.send("%s %s%s" % (ProtocolExtended.GAME_BOARD, game_id[0], Protocol.EOL))

    def get_stat_date(self, date_string):
        timestamp = long(time.mktime(pdt.Calendar().parse(date_string[0])[0]))
        self.socket.send("%s %s %s%s" % (Protocol.STATS, Protocol.STAT_DATE, str(timestamp), Protocol.EOL))

    def get_stat_player(self, player):
        self.socket.send("%s %s %s%s" % (Protocol.STATS, Protocol.STAT_PLAYER, player[0], Protocol.EOL))

    def join(self, number_of_players):
        if int(number_of_players[0]) < 2 or int(number_of_players[0]) > 4:
            return
        self.socket.send("%s %s%s" % (Protocol.JOIN, number_of_players[0], Protocol.EOL))
        print("Request sent for %s players, waiting for others to join..." % number_of_players[0])

    def place(self, coord):
        x, y = Protocol.coord_str(coord[0])
        game = copy.deepcopy(self.game)
        try:
            game.place(x, y)
        except GameOverError:
            pass
        except BoardError:
            print("The move you suggested is not valid, make another move please")
            return
        self.socket.send("%s %s%s" % (Protocol.PLACE, coord[0], Protocol.EOL))

    def enable_ai(self):
        self.auto_fire = True

    def disable_ai(self):
        self.auto_fire = False

    def ai(self):
        game = copy.deepcopy(self.game)
        for x in range(Board.DIM):
            for y in range(Board.DIM):
                try:
                    game.place(x, y)
                except GameOverError:
                    pass
                except BoardError:
                    continue
                self.socket.send("%s %s%s" % (Protocol.PLACE, "%s%s" % (x, y), Protocol.EOL))
                return
