import random, datetime

from models.games import *
from models.game import *
from models.protocol import Protocol
from models.protocol_extended import ProtocolExtended

from models.leaderboard import *

COLORS  = {
    Protocol.RED    : Ball.RED,
    Protocol.YELLOW : Ball.YELLOW,
    Protocol.BLUE   : Ball.BLUE,
    Protocol.GREEN  : Ball.GREEN
}

class Server(object):
    def __init__(self):
        self.leaderboard = Leaderboard()
        self.clients = []
        self.network_games = {}
        self.join_list = { 2 : [], 3 : [], 4 : [] }
        self.challenge_list = {}

    def connect(self, socket, name, chat = Protocol.FALSE, challenge = Protocol.FALSE):
        if self.get_client(name):
            raise ServerError("Given name is already in use")

        client = { 'socket' : socket,
                   'name' : name,
                   'chat' : chat == Protocol.TRUE,
                   'challenge' : challenge == Protocol.TRUE }
        self.clients.append(client)
        client['socket'].send("%s %s %s%s" % (Protocol.GREET, Protocol.TRUE, Protocol.TRUE, Protocol.EOL))

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

    def chat(self, sender, message):
        if not sender['chat']:
            raise ClientError("You said you did not support chat, so you cannot send a chat message")

        if 'game_id' in sender:
            clients = self.network_games[sender['game_id']]['clients']
        else:
            clients = [client for client in self.clients if 'game_id' not in client]
        chat_clients = [client for client in clients if client['chat']]

        for chat_client in chat_clients:
            chat_client['socket'].send("%s %s %s%s" % (Protocol.CHAT, sender['name'], message, Protocol.EOL))

    def challenge(self, challenger, challengees):
        if not challenger['challenge']:
            raise ClientError("You said you did not support challenges, so you cannot send a challenge request")

        if challenger['name'] in self.challenge_list:
            self.remove_challenge(challenger['name'])

        challenged_names = challengees.split(' ')
        challenged_clients = [self.get_client(challengee) for challengee in challenged_names]
        if challenger in challenged_clients:
            raise ClientError("You challenged yourself, what do you think?")

        if len(challenged_clients) > 3:
            raise ClientError("You challenged more than 3 players, refer to the protocol")

        if False in challenged_clients:
            raise ClientError("You challenged someone who does not exist")

        if False in [challenged_client['challenge'] for challenged_client in challenged_clients]:
            raise ClientError("You challenged someone who does not support challenges")

        all_challengees = [item for sublist in [challenge.keys() for challenge in self.challenge_list.values()] for item in sublist]
        if len(list(set(all_challengees) & set(challenged_names))) > 0:
            raise AlreadyChallengedError("You challenged someone who already is in challenge")

        self.challenge_list[challenger['name']] = { challenger['name'] : True }
        for challenged_client in challenged_clients:
            self.challenge_list[challenger['name']][challenged_client['name']] = False
            challenged_client['socket'].send("%s %s %s%s" % (Protocol.CHALLENGE, challenger['name'], challengees, Protocol.EOL))


    def challenge_response(self, challengee, response):
        for challenge, challengees in self.challenge_list.iteritems():
            if challengee['name'] in challengees:
                if response == Protocol.TRUE:
                    challengees[challengee['name']] = True
                    if all(challengees.values()):
                        self.start_game([self.get_client(client_name) for client_name in challengees])
                elif response == Protocol.FALSE:
                    self.remove_challenge(challenge)
                return
        raise ClientError("You responded while you were not challenged")

    def remove_challenge(self, challenger):
        for challengee in self.challenge_list[challenger]:
            self.get_client(challengee)['socket'].send("%s%s" % (Protocol.CHALLENGE_REJECTED, Protocol.EOL))
        del(self.challenge_list[challenger])

    def join(self, client, number_of_players):
        try:
            number_of_players = int(number_of_players)
        except ValueError:
            raise ClientError("Given number is not a number")

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
        if color not in COLORS:
            raise ClientError("Given color `%s` is not valid, refer to protocol" % color)

        try:
            x = int(coord[0])
            y = int(coord[1])
        except ValueError:
            raise ClientError("Given coordinate `%s` is not an integer, refer to protocol" % coord)

        if x < 0 or x >= Board.DIM or y < 0 or y >= Board.DIM:
            raise ClientError("Given coordinate `%s` does not exist on board, refer to protocol" % coord)

        if 'game_id' not in client:
            raise ClientError("Client is not in-game, refer to protocol")

        network_game = self.network_games[client['game_id']]
        if network_game['game'].current_player != network_game['clients'].index(client):
            raise ClientError("Client is not current player of game, refer to protocol")

        for client in network_game['clients']:
            client['socket'].send("%s %s %s%s" % (Protocol.PLACE, coord, color, Protocol.EOL))

        try:
            network_game['game'].place(x, y, COLORS[color])
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
        try:
            if stat == Protocol.STAT_DATE:
                try:
                    arg = float(arg)
                except ValueError:
                    raise ClientError("Given argument `%s` cannot be converted to a floating point" % arg)

                score = self.leaderboard.best_score_of_date(datetime.datetime.fromtimestamp(arg))
                client['socket'].send("%s %s %s %s%s" % (Protocol.STAT, stat, arg, score.score, Protocol.EOL))
            elif stat == Protocol.STAT_PLAYER:
                score = self.leaderboard.best_score_of_player(arg)
                client['socket'].send("%s %s %s %s%s" % (Protocol.STAT, stat, arg, score.score, Protocol.EOL))
            else:
                raise ClientError("Given stat `%s` is not recognized, refer to protocol" % stat)
        except NoHighScoresError:
            client['socket'].send("%s %s %s %s%s" % (Protocol.STAT, stat, arg, Protocol.UNDEFINED, Protocol.EOL))

    def send_games(self, client):
        game_ids = [str(game) for game in self.network_games.keys()]
        client['socket'].send("%s %s%s" % (ProtocolExtended.GAMES, Protocol.SEPARATOR.join(game_ids), Protocol.EOL))

    def send_game_players(self, client, game_id):
        try:
            game_players = [player['name'] for player in self.network_games[int(game_id)]['clients']]
            client['socket'].send("%s %s%s" % (ProtocolExtended.GAME_PLAYERS, Protocol.SEPARATOR.join(game_players), Protocol.EOL))
        except (ValueError, KeyError):
            client['socket'].send("%s %s%s" % (ProtocolExtended.GAME_PLAYERS, Protocol.UNDEFINED, Protocol.EOL))

    def send_game_board(self, client, game_id):
        try:
            board = self.network_games[int(game_id)]['game'].board
            client['socket'].send("%s %s%s" % (ProtocolExtended.GAME_BOARD, board.encode(), Protocol.EOL))
        except (ValueError, KeyError):
            client['socket'].send("%s %s%s" % (ProtocolExtended.GAME_BOARD, Protocol.UNDEFINED, Protocol.EOL))

class ServerError(Exception): pass
class ClientError(Exception): pass
class AlreadyChallengedError(ClientError): pass
