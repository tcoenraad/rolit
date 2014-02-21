import copy
from base64 import b64encode

from rolit.game import GameOverError
from rolit.games import TwoPlayerGame, ThreePlayerGame, FourPlayerGame
from rolit.board import Board, BoardError

from rolit.helpers import Helpers
from rolit.protocol import Protocol
from rolit.protocol_extended import ProtocolExtended
from rolit.server import Server

class NoPrivateKeyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Client(object):

    class Router(object):

        routes = { Protocol.ONLINE : { 'method' : 'online' },
                   Protocol.CHALLENGABLE : { 'method' : 'challengable'},
                   Protocol.HANDSHAKE : { 'method' : 'handshake' },
                   Protocol.AUTH_OK : { 'method' : 'auth' },
                   Protocol.GAME : { 'method' : 'game' },
                   Protocol.START : { 'method' : 'start' },
                   Protocol.MOVE : { 'method' : 'move' },
                   Protocol.MOVED : { 'method' : 'moved' },
                   Protocol.GAME_OVER : { 'method' : 'game_over' },
                   Protocol.STATS : { 'method' : 'stats' },
                   ProtocolExtended.GAMES : { 'method' : 'games' },
                   ProtocolExtended.GAME_PLAYERS : { 'method' : 'game_players' },
                   ProtocolExtended.GAME_BOARD : { 'method' : 'game_board' } }

        def __init__(self, client):
            self.client = client

        @staticmethod
        def online(name, status):
            Helpers.notice("[online] `%s`: %s" % (name, status == Protocol.TRUE))

        @staticmethod
        def challengable(name, status):
            Helpers.notice("[challengable] `%s`: %s" % (name, status == Protocol.TRUE))

        @staticmethod
        def error(message):
            print("Oops, that is an error: `%s`" % message)

        @staticmethod
        def game(name, status, number_of_players):
            Helpers.notice("[game_update] `%s`, with `%s` players has status: %s" % (name, number_of_players, status))

        def move(self):
            if self.client.auto_fire:
                self.client.ai()
            else:
                print("You may now enter a coord!")
                print("[x] <xy> (autofire once with [a], enable auto_fire with [xa], disable with [xm])")

        def moved(self, name, x, y):
            x = int(x)
            y = int(y)
            Helpers.notice("A move is done by %s at x=%s, y=%s" % (name, x, y))
            try:
                self.client.game.place(x, y)
            except GameOverError:
                pass
            except BoardError:
                print("An invalid move is made!")

            print(self.client.game.board)

        def game_over(self, score, *players):
            Helpers.notice("Game is over!")
            print("Score was: %s, for winners: %s" % (score, list(players)))

        def start(self, *players):
            Helpers.notice("A game has started!")
            print("Players are: %s" % list(players))
            number_of_players = len(players)
            if number_of_players == 2:
                self.client.game = TwoPlayerGame()
            elif number_of_players == 3:
                self.client.game = ThreePlayerGame()
            elif number_of_players == 4:
                self.client.game = FourPlayerGame()
            print(self.client.game.board)

        def handshake(self, *options):
            Helpers.notice("Connected established")
            Helpers.notice("Chat = %s and challenge = %s" % (options[0] == Protocol.CHAT_ENABLED or options[0] == Protocol.CHAT_AND_CHALLENGE, options[0] == Protocol.CHALLENGE_ENABLED or options[0] == Protocol.CHAT_AND_CHALLENGE))

            if len(options) >= 3:
                signature = b64encode(Helpers.sign_data(self.client.private_key, options[2]))
                self.client.socket.sendall("%s %s%s" % (Protocol.AUTH, signature, Protocol.EOL))

        @staticmethod
        def auth():
            Helpers.warning("Authentication was successful")

        @staticmethod
        def games(games):
            print("The following game ids are running:")
            print(games)

        @staticmethod
        def game_players(*players):
            print("The following players are in game `%s` active:" % players[0])
            print(players[1:])

        @staticmethod
        def game_board(game_id, *board):
            print("The board for game `%s` looks like:" % game_id)
            if not board[0] == Protocol.UNDEFINED:
                print(Board.decode(Protocol.SEPARATOR.join(board[0:])))

        @staticmethod
        def stats(stat, arg, *result):
            if stat == Protocol.STAT_DATE:
                print("The following player was at date `%s` best player:" % arg)
                print(result)
            
            elif stat == Protocol.STAT_PLAYER:
                print("The following score was best of player `%s` best player:" % arg)
                print(result)

    options = { 'h' : { 'method': 'menu', 'args': 0, 'description': "Show this help menu" },
                '1' : { 'method': 'create_game', 'args': 0, 'description': "Create a game" },
                '2' : { 'method': 'join_game', 'args': 1, 'description': "<player> Join a game of that player" },
                '3' : { 'method': 'get_games', 'args': 0, 'description': "Get all running games" },
                '4' : { 'method': 'get_game_players', 'args': 1, 'description': "<id> Show game players" },
                '5' : { 'method': 'get_game_board', 'args': 1, 'description': "<id> Show game board" },
                '6' : { 'method': 'get_stat_date', 'args': 1, 'description': "<YYYY-MM-DD> Show best player on that date" },
                '7' : { 'method': 'get_stat_player', 'args': 1, 'description': "<player> Show best score of that player" },
                's' : { 'method': 'start_game', 'args': 0, 'hidden': True },
                'x' : { 'method': 'place', 'args': 1, 'hidden': True },
                'xa': { 'method': 'enable_ai', 'args': 0, 'hidden': True },
                'xm': { 'method': 'disable_ai', 'args': 0, 'hidden': True },
                'a' : { 'method': 'ai', 'args': 0, 'hidden': True }
               }

    def __init__(self, socket, name, private_key=None):
        self.socket = socket
        self.auto_fire = False
        self.router = Client.Router(self)
        self.name = name
        self.private_key = private_key

    @staticmethod
    def menu():
        Helpers.notice('-' * 16)
        for key in sorted(Client.options.keys()):
            value = Client.options[key]
            if 'hidden' in value.keys():
                continue
            print("%s|%s" % (key, value['description']))
        Helpers.notice('-' * 16)

    def handshake(self):
        if self.name.startswith('player_') and not self.private_key:
            raise NoPrivateKeyError("When a playername with player_ is given, a private key is expected")

        self.socket.sendall("%s %s %s %s%s" % (Protocol.HANDSHAKE, self.name, Protocol.CHAT_AND_CHALLENGE, Server.VERSION, Protocol.EOL))

    def get_games(self):
        self.socket.sendall("%s%s" % (ProtocolExtended.GAMES, Protocol.EOL))

    def get_game_players(self, game_id):
        self.socket.sendall("%s %s%s" % (ProtocolExtended.GAME_PLAYERS, game_id[0], Protocol.EOL))

    def get_game_board(self, game_id):
        self.socket.sendall("%s %s%s" % (ProtocolExtended.GAME_BOARD, game_id[0], Protocol.EOL))

    def get_stat_date(self, date):
        self.socket.sendall("%s %s %s%s" % (Protocol.STATS, Protocol.STAT_DATE, date[0], Protocol.EOL))

    def get_stat_player(self, player):
        self.socket.sendall("%s %s %s%s" % (Protocol.STATS, Protocol.STAT_PLAYER, player[0], Protocol.EOL))

    def create_game(self):
        self.socket.sendall("%s%s" % (Protocol.CREATE_GAME, Protocol.EOL))
        print("Game created, wait for others to join")
        print("Start this game with [s]")

    def join_game(self, player):
        self.socket.sendall("%s %s%s" % (Protocol.JOIN_GAME, player[0], Protocol.EOL))
        print("Joined game `%s`, waiting for other to join and creator to start" % player)

    def start_game(self):
        self.socket.sendall("%s%s" % (Protocol.START_GAME, Protocol.EOL))

    def place(self, coord):
        try:
            x = int(coord[0][0])
            y = int(coord[0][1])
        except ValueError:
            return

        game = copy.deepcopy(self.game)
        try:
            game.place(x, y)
        except GameOverError:
            pass
        except BoardError:
            print("The move you suggested is not valid, make another move please")
            return
        self.socket.sendall("%s %s %s%s" % (Protocol.MOVE, x, y, Protocol.EOL))

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
                self.socket.sendall("%s %s %s%s" % (Protocol.MOVE, x, y, Protocol.EOL))
                return
