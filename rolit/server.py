import random, datetime
import hashlib

from rolit.helpers import Helpers

from rolit.games import TwoPlayerGame, ThreePlayerGame, FourPlayerGame
from rolit.game import GameOverError
from rolit.board import Board, BoardError
from rolit.protocol import Protocol
from rolit.protocol_extended import ProtocolExtended
from rolit.leaderboard import Leaderboard, NoHighScoresError

class Server(object):

    routes = {
        Protocol.AUTH : { 'method' : 'auth' },
        Protocol.CREATE_GAME : { 'method' : 'create_game' },
        Protocol.START_GAME : { 'method' : 'start_game' },
        Protocol.JOIN_GAME : { 'method' : 'join_game' },
        Protocol.MOVE : { 'method' : 'move' },
        Protocol.CHAT : { 'method' : 'chat' },
        Protocol.CHALLENGE : { 'method' : 'challenge' },
        Protocol.CHALLENGE_RESPONSE : { 'method' : 'challenge_response' },
        Protocol.STATS : { 'method' : 'stats' },
        ProtocolExtended.GAMES : { 'method' : 'send_games' },
        ProtocolExtended.GAME_PLAYERS : { 'method' : 'send_game_players' },
        ProtocolExtended.GAME_BOARD : { 'method' : 'send_game_board' }
    }

    def __init__(self):
        self.leaderboard = Leaderboard()
        self.clients = []
        self.network_games = {}
        self.lobbies = {}
        self.challenge_list = {}

    def get_client(self, name):
        for client in self.clients:
            if client['name'] == name:
                return client
        return False

    def get_clients_in_lobbies(self):
        return [item for sublist in self.lobbies.values() for item in sublist]

    def get_clients_in_challenges(self):
        return [item for sublist in self.challenge_list.values() for item in sublist]

    def connect(self, socket, name, supported = Protocol.BAREBONE):
        if self.get_client(name):
            raise ServerError("Given name is already in use")

        client = { 'socket' : socket,
                   'name' : name,
                   'chat' : supported == Protocol.CHAT or supported == Protocol.CHAT_AND_CHALLENGE,
                   'challenge' : supported == Protocol.CHALLENGE or supported == Protocol.CHAT_AND_CHALLENGE }

        # authenticate
        if name.startswith(Protocol.AUTH_PREFIX):
            client['nonce'] = hashlib.sha512(str(random.random())).hexdigest()
            client['socket'].send("%s %s %s%s" % (Protocol.HANDSHAKE, Protocol.CHAT_AND_CHALLENGE, client['nonce'], Protocol.EOL))
        else:
            client['socket'].send("%s %s%s" % (Protocol.HANDSHAKE, Protocol.CHAT_AND_CHALLENGE, Protocol.EOL))

        for (lobby, clients) in self.lobbies.items():
            client['socket'].send("%s %s %s %s%s" % (Protocol.GAME, lobby, Protocol.NOT_STARTED, len(clients), Protocol.EOL))

        # push online clients
        for c in self.clients:
            client['socket'].send("%s %s %s%s" % (Protocol.ONLINE, c['name'], Protocol.TRUE, Protocol.EOL))
        self.broadcast("%s %s %s%s" % (Protocol.ONLINE, name, Protocol.TRUE, Protocol.EOL))
        client['socket'].send("%s %s %s%s" % (Protocol.ONLINE, name, Protocol.TRUE, Protocol.EOL))

        # push challengable clients
        if client['challenge']:
            challengees = self.get_clients_in_challenges()
            for c in self.clients:
                if c['challenge']:
                    client['socket'].send("%s %s %s%s" % (Protocol.CHALLENGE_AVAILABLE, c['name'], Protocol.FALSE if c['name'] in challengees else Protocol.TRUE, Protocol.EOL))
            self.broadcast("%s %s %s%s" % (Protocol.CHALLENGE_AVAILABLE, name, Protocol.TRUE, Protocol.EOL), 'challenge')
            client['socket'].send("%s %s %s%s" % (Protocol.CHALLENGE_AVAILABLE, name, Protocol.TRUE, Protocol.EOL))

        self.clients.append(client)
        return client

    def disconnect(self, client):
        self.clients.remove(client)

        for (lobby, clients) in self.lobbies.items():
            if lobby == client['name']:
                del(self.lobbies[lobby])
                self.broadcast("%s %s %s %s%s" % (Protocol.GAME, lobby, Protocol.UNDEFINED, len(clients), Protocol.EOL))
            elif client in clients:
                clients.remove(client)
                self.broadcast("%s %s %s %s%s" % (Protocol.GAME, lobby, Protocol.NOT_STARTED, len(clients), Protocol.EOL))

        if client['challenge']:
            try:
                self.challenge_response(client, Protocol.FALSE)
                self.broadcast("%s %s %s%s" % (Protocol.CHALLENGE_AVAILABLE, client['name'], Protocol.FALSE, Protocol.EOL), 'challenge')
            except ClientError:
                pass

        self.broadcast("%s %s %s%s" % (Protocol.ONLINE, client['name'], Protocol.FALSE, Protocol.EOL))
        if 'game_id' in client:
            self.game_over(self.network_games[client['game_id']])

    def auth(self, client, signature):
        if 'nonce' not in client:
            raise ClientError("You cannot authenticate yourself without a nonce")
        if Helpers.verify_sign(client['name'], signature, client['nonce']):
            client['verified'] = True
            client['socket'].send("%s%s" % (Protocol.AUTH_OK, Protocol.EOL))
        else:
            raise ClientError("Given signature is not correct")

    def broadcast(self, msg, supported=""):
        for client in self.clients:
            if supported == "" or client[supported]:
                client['socket'].send(msg)

    def create_game(self, client):
        if client['name'] in self.lobbies:
            raise ClientError("You have already created a game")
        if client in self.get_clients_in_lobbies():
            raise ClientError("You have already joined a game")
        if client['name'] in self.get_clients_in_challenges():
            raise ClientError("You are already in challenge")

        clients = self.lobbies[client['name']] = [ client ]
        self.broadcast("%s %s %s %s%s" % (Protocol.GAME, client['name'], Protocol.NOT_STARTED, len(clients), Protocol.EOL))

    def join_game(self, client, creator):
        try:
            clients = self.lobbies[creator]
        except KeyError:
            raise ClientError("Given client has not created a game")

        if client in clients:
            raise ClientError("You have already joined a game")

        if len(clients) == 4:
            raise ClientError("Given name points to a full game lobby")

        clients.append(client)

        self.broadcast("%s %s %s %s%s" % (Protocol.GAME, creator, Protocol.NOT_STARTED, len(clients), Protocol.EOL))

    def start_game(self, creator):
        try:
            clients = self.lobbies[creator['name']]
            if len(clients) == 1:
                raise ClientError("You cannot start a game with only one player")

            self.broadcast("%s %s %s %s%s" % (Protocol.GAME, creator['name'], Protocol.STARTED, len(clients), Protocol.EOL))
            del(self.lobbies[creator['name']])

        except KeyError:
            try:
                challengees = self.challenge_list[creator['name']]
                if not all(challengees.values()):
                    raise ClientError("You cannot start a game until everyone accepts the challenge")
                clients = [self.get_client(client_name) for client_name in challengees]
            except KeyError:
                raise ClientError("You have not created a game")

        return self.initiate_game(clients)

    def initiate_game(self, clients):
        if len(clients) == 2:
            game = TwoPlayerGame()
        elif len(clients) == 3:
            game = ThreePlayerGame()
        elif len(clients) == 4:
            game = FourPlayerGame()

        game_id = id(game)
        random.shuffle(clients)
        self.network_games[game_id] = { 'clients' : clients, 'game' : game }

        for client in clients:
            client['game_id'] = game_id
            client['socket'].send("%s %s%s" % (Protocol.START, ' '.join(c['name'] for c in clients), Protocol.EOL))

        clients[0]['socket'].send("%s%s" % (Protocol.MOVE, Protocol.EOL))

        return game

    def move(self, client, x, y):
        try:
            network_game = self.network_games[client['game_id']]
        except KeyError:
            raise ClientError("Client is not in-game, refer to protocol")

        try:
            try:
                x = int(x)
                y = int(y)
            except ValueError:
                raise ClientError("Given coordinate `(%s, %s)` is not an integer, refer to protocol" % (x, y))

            if x < 0 or x >= Board.DIM or y < 0 or y >= Board.DIM:
                raise ClientError("Given coordinate `(%s, %s)` does not exist on board, refer to protocol" % (x, y))

            if network_game['game'].current_player != network_game['clients'].index(client):
                raise ClientError("Client is not current player of game, refer to protocol")

            for client in network_game['clients']:
                client['socket'].send("%s %s %s%s" % (Protocol.MOVED, x, y, Protocol.EOL))
            try:
                network_game['game'].place(x, y)
            except BoardError:
                raise ClientError("Given coordinate `%s` is not a valid move on the current board")

            network_game['clients'][network_game['game'].current_player]['socket'].send("%s%s" % (Protocol.MOVE, Protocol.EOL))
        except (ClientError, GameOverError) as e:
            self.game_over(network_game)
            if isinstance(e, ClientError):
                raise e

    def game_over(self, network_game):
        for client in network_game['clients']:
            if client in self.clients:
                winning_players = network_game['game'].winning_players()
                winning_clients = [network_game['clients'][p] for p in winning_players]

                client['socket'].send("%s %s%s" % (Protocol.GAME_OVER, ' '.join(client['name'] for client in winning_clients), Protocol.EOL))

                if client in winning_clients and 'verified' in client:
                    self.leaderboard.add_score(client['name'], datetime.datetime.now(), 1)
                else:
                    self.leaderboard.add_score(client['name'], datetime.datetime.now(), 0)
                del(client['game_id'])
        del self.network_games[id(network_game['game'])]

    def chat(self, sender, *message):
        if not sender['chat']:
            raise ClientError("You said you did not support chat, so you cannot send a chat message")

        if 'game_id' in sender:
            clients = self.network_games[sender['game_id']]['clients']
        else:
            clients = [client for client in self.clients if 'game_id' not in client]
        chat_clients = [client for client in clients if client['chat']]

        for chat_client in chat_clients:
            chat_client['socket'].send("%s %s %s%s" % (Protocol.CHAT, sender['name'], " ".join(message), Protocol.EOL))

    def challenge(self, challenger, *challenged_names):
        if not challenger['challenge']:
            raise ClientError("You said you did not support challenges, so you cannot send a challenge request")

        if len(challenged_names) > 3:
            raise ClientError("You challenged more than 3 players, refer to the protocol")

        challenged_clients = [self.get_client(challengee) for challengee in challenged_names]
        if challenger in challenged_clients:
            raise ClientError("You challenged yourself, what do you think?")

        if False in challenged_clients:
            raise ClientError("You challenged someone who does not exist")

        if False in [challenged_client['challenge'] for challenged_client in challenged_clients]:
            raise ClientError("You challenged someone who does not support challenges")

        if True in [challenged_client in self.get_clients_in_lobbies() for challenged_client in challenged_clients]:
            raise ClientError("You challenged someone who already is in a not started game")

        if True in ['game_id' in challenged_client for challenged_client in challenged_clients]:
            raise ClientError("You challenged someone who already is in started game")

        all_challengees = [item for sublist in self.challenge_list.values() for item in sublist]
        if len(list(set(all_challengees) & set(challenged_names))) > 0:
            raise ClientError("You challenged someone who already is in challenge")

        self.challenge_list[challenger['name']] = { challenger['name'] : True }
        self.broadcast("%s %s %s%s" % (Protocol.CHALLENGE_AVAILABLE, challenger['name'], Protocol.FALSE, Protocol.EOL), 'challenge')
        for challenged_client in challenged_clients:
            self.challenge_list[challenger['name']][challenged_client['name']] = False
            challenged_client['socket'].send("%s %s %s%s" % (Protocol.CHALLENGE, challenger['name'], Protocol.SEPARATOR.join(challenged_names), Protocol.EOL))
            self.broadcast("%s %s %s%s" % (Protocol.CHALLENGE_AVAILABLE, challenged_client['name'], Protocol.FALSE, Protocol.EOL), 'challenge')

    def challenge_response(self, challenger, response):
        challenge_accepted = response == Protocol.TRUE
        for (challenge, challengees) in self.challenge_list.iteritems():
            if challenger['name'] in challengees:
                for challengee in challengees:
                    if self.get_client(challengee):
                        self.get_client(challengee)['socket'].send("%s %s %s%s" % (Protocol.CHALLENGE_RESPONSE, challenger['name'], response, Protocol.EOL))

                if response == Protocol.TRUE:
                    challengees[challenger['name']] = True
                else:
                    self.remove_challenge(challenge)
                return
        raise ClientError("You responded while you were not challenged")

    def remove_challenge(self, challenger):
        for challengee in self.challenge_list[challenger]:
            if self.get_client(challengee):
                self.broadcast("%s %s %s%s" % (Protocol.CHALLENGE_AVAILABLE, challengee, Protocol.TRUE, Protocol.EOL), 'challenge')
        del(self.challenge_list[challenger])

    def stats(self, client, stat, query):
        try:
            if stat == Protocol.STAT_DATE:
                try:
                    date = query.split("-")
                    if not len(date) == 3:
                        raise ClientError("Given argument `%s` is malformed, refer to protocol" % date)
                    date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
                except ValueError:
                    raise ClientError("Given argument `%s` cannot be converted to a valid date" % query)

                score = self.leaderboard.best_score_of_date(date)
                client['socket'].send("%s %s %s %s %s%s" % (Protocol.STATS, stat, query, score.name, score.score, Protocol.EOL))
            elif stat == Protocol.STAT_PLAYER:
                score = self.leaderboard.best_score_of_player(query)
                client['socket'].send("%s %s %s %s%s" % (Protocol.STATS, stat, query, score.score, Protocol.EOL))
            else:
                raise ClientError("Given stat `%s` is not recognized, refer to protocol" % stat)
        except NoHighScoresError:
            client['socket'].send("%s %s %s %s%s" % (Protocol.STATS, stat, query, Protocol.UNDEFINED, Protocol.EOL))

    def send_games(self, client):
        game_ids = [str(game) for game in self.network_games.keys()]
        if not game_ids:
            game_ids = [Protocol.UNDEFINED]
        client['socket'].send("%s %s%s" % (ProtocolExtended.GAMES, Protocol.SEPARATOR.join(game_ids), Protocol.EOL))

    def send_game_players(self, client, game_id):
        try:
            game_players = [player['name'] for player in self.network_games[int(game_id)]['clients']]
            client['socket'].send("%s %s %s%s" % (ProtocolExtended.GAME_PLAYERS, game_id, Protocol.SEPARATOR.join(game_players), Protocol.EOL))
        except (ValueError, KeyError):
            client['socket'].send("%s %s %s%s" % (ProtocolExtended.GAME_PLAYERS, game_id, Protocol.UNDEFINED, Protocol.EOL))

    def send_game_board(self, client, game_id):
        try:
            board = self.network_games[int(game_id)]['game'].board
            client['socket'].send("%s %s %s%s" % (ProtocolExtended.GAME_BOARD, game_id, board.encode(), Protocol.EOL))
        except (ValueError, KeyError):
            client['socket'].send("%s %s %s%s" % (ProtocolExtended.GAME_BOARD, game_id, Protocol.UNDEFINED, Protocol.EOL))

class ServerError(Exception): pass
class ClientError(Exception): pass
