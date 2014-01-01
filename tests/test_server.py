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

    def test_it_connects(self):
        socket = Mock()
        self.server.connect(socket, "Bestuur_35", Protocol.TRUE, Protocol.FALSE)

        socket.send.assert_called_once_with("%s %s %s%s" % (Protocol.GREET, Protocol.TRUE, Protocol.TRUE, Protocol.EOL))

    def test_it_overwrite_joins(self):
        self.server.start_game = Mock()

        self.server.join(self.clients[0], '2')
        self.server.join(self.clients[0], '2')
        self.server.join(self.clients[1], '2')

        self.server.start_game.assert_called_once_with([self.clients[0], self.clients[1]])

    def test_it_validates_name_is_unique(self):
        with pytest.raises(ServerError):
            self.server.connect(Mock(), "Met_TOM_op_de_koffie!")

        self.server.disconnect(self.clients[0])
        self.server.connect(Mock(), "Met_TOM_op_de_koffie!")

    def test_it_validates_requested_number_of_player(self):
        with pytest.raises(ClientError):
            self.server.join(self.clients[0], '1')
        with pytest.raises(ClientError):
            self.server.join(self.clients[0], '5')

    def test_it_validates_number_is_a_number(self):
        with pytest.raises(ClientError):
            self.server.join(self.clients[0], 'vijfendertig')

    def test_it_validates_given_number_represents_a_dimension_on_board(self):
        self.server.game_over = Mock()

        self.server.start_game([self.clients[0], self.clients[1]])
        with pytest.raises(ClientError):
            self.server.place(self.clients[0], '-1')
        with pytest.raises(ClientError):
            self.server.place(self.clients[0], '88')
        with pytest.raises(ClientError):
            self.server.place(self.clients[0], 'ab')
        with pytest.raises(ClientError):
            self.server.place(self.clients[0], '0000')

        assert self.server.game_over.call_count == 4

    def test_it_validates_client_is_in_game(self):
        with pytest.raises(ClientError):
            self.server.place(self.clients[0], '53')

        game = self.server.start_game([self.clients[0], self.clients[1]])
        game.balls_left = 1

        self.server.place(self.clients[0], '53')
        with pytest.raises(ClientError):
            self.server.place(self.clients[0], '53')

    def test_it_validates_it_is_clients_turn(self):
        self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
        with pytest.raises(ClientError):
            self.server.place(self.clients[1], '52')

    def test_game_goes_game_overs_on_disconnect(self):
        self.server.start_game([self.clients[0], self.clients[1]])
        self.server.disconnect(self.clients[1])

        args = "%s %s %s%s" % (Protocol.GAME_OVER, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)
        self.clients[0]['socket'].send.assert_has_calls(call(args))

    def test_chat_when_enabled_and_in_lobby(self):
        self.server.chat(self.clients[0], "This is a test message")

        args = call("%s %s %s%s" % (Protocol.CHAT, self.clients[0]['name'], "This is a test message", Protocol.EOL))
        self.clients[0]['socket'].send.assert_has_calls(args)
        self.clients[1]['socket'].send.assert_has_calls(args)
        self.clients[2]['socket'].send.assert_has_calls(args)
        assert self.clients[3]['socket'].send.call_count == 1
        assert self.clients[4]['socket'].send.call_count == 1

    def test_chat_when_enabled_and_in_game(self):
        self.server.start_game([self.clients[0], self.clients[1]])
        self.server.chat(self.clients[0], "This is a test message")
        self.server.chat(self.clients[2], "This is a second test message")

        args = call("%s %s %s%s" % (Protocol.CHAT, self.clients[0]['name'], "This is a test message", Protocol.EOL))
        self.clients[0]['socket'].send.assert_has_calls(args)
        self.clients[1]['socket'].send.assert_has_calls(args)

        args = call("%s %s %s%s" % (Protocol.CHAT, self.clients[2]['name'], "This is a second test message", Protocol.EOL))
        self.clients[2]['socket'].send.assert_has_calls(args)
        assert self.clients[3]['socket'].send.call_count == 1
        assert self.clients[4]['socket'].send.call_count == 1

    def test_chat_when_disabled(self):
        with pytest.raises(ClientError):
            self.server.chat(self.clients[3], "This is a test message")

    def test_challenge_itself(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], "%s" % (self.clients[0]['name']))

    def test_challenge_with_to_many_people(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], "%s %s %s %s" % ("a", "b", "c", "d"))

    def test_challenge_when_challengee_disabled_challenges(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], "%s" % (self.clients[2]['name']))

    def test_challenge_when_challenger_disabled_challenges(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[2], "%s" % (self.clients[0]['name']))

    def test_challenge_someone_that_does_not_exist(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], "%s" % ("W.A. van Buren"))

    def test_challenge_someone_that_is_already_challenged(self):
        self.server.challenge(self.clients[0], "%s" % (self.clients[1]['name']))
        with pytest.raises(AlreadyChallengedError):
            self.server.challenge(self.clients[4], "%s" % (self.clients[1]['name']))

    def test_challenge_requests(self):
        self.server.challenge(self.clients[0], self.clients[1]['name'], self.clients[4]['name'])

        args = call("%s %s %s %s%s" % (Protocol.CHALLENGE, self.clients[0]['name'], self.clients[1]['name'], self.clients[4]['name'], Protocol.EOL))
        self.clients[1]['socket'].send.assert_has_calls(args)
        self.clients[4]['socket'].send.assert_has_calls(args)
        assert self.clients[2]['socket'].send.call_count == 1
        assert self.clients[3]['socket'].send.call_count == 1

        self.server.challenge(self.clients[0], self.clients[1]['name'])
        args = call("%s%s" % (Protocol.CHALLENGE_REJECTED, Protocol.EOL))
        self.clients[0]['socket'].send.assert_has_calls(args)
        self.clients[1]['socket'].send.assert_has_calls(args)
        self.clients[4]['socket'].send.assert_has_calls(args)

        args = call("%s %s %s%s" % (Protocol.CHALLENGE, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL))
        self.clients[1]['socket'].send.assert_has_calls(args)

    def test_challenge_request_accepted(self):
        self.server.start_game = Mock()

        self.server.challenge(self.clients[0], self.clients[1]['name'], self.clients[4]['name'])
        self.server.challenge_response(self.clients[1], Protocol.TRUE)
        assert self.server.start_game.call_count == 0

        self.server.challenge_response(self.clients[4], Protocol.TRUE)
        assert sorted(self.server.start_game.call_args[0][0]) == sorted([self.clients[0], self.clients[1], self.clients[4]])

    def test_challenge_request_rejected(self):
        self.server.start_game = Mock()

        self.server.challenge(self.clients[0], self.clients[1]['name'], self.clients[4]['name'])
        self.server.challenge_response(self.clients[1], Protocol.TRUE)
        assert self.server.start_game.call_count == 0

        self.server.challenge_response(self.clients[4], Protocol.FALSE)

        args = call("%s%s" % (Protocol.CHALLENGE_REJECTED, Protocol.EOL))
        self.clients[0]['socket'].send.assert_has_calls(args)
        self.clients[1]['socket'].send.assert_has_calls(args)
        self.clients[4]['socket'].send.assert_has_calls(args)
        assert self.clients[2]['socket'].send.call_count == 1
        assert self.clients[3]['socket'].send.call_count == 1

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

        args = call("%s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL))
        self.clients[0]['socket'].send.assert_has_calls(args)
        self.clients[0]['socket'].send.assert_has_calls(call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
        self.clients[1]['socket'].send.assert_has_calls(args)
        assert self.clients[2]['socket'].send.call_count == 1

    def test_it_starts_for_three_players(self):
        self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
        
        args = call("%s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], Protocol.EOL))
        self.clients[0]['socket'].send.assert_has_calls(args)
        self.clients[0]['socket'].send.assert_has_calls(call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
        self.clients[1]['socket'].send.assert_has_calls(args)
        self.clients[2]['socket'].send.assert_has_calls(args)
        assert self.clients[3]['socket'].send.call_count == 1
    
    def test_it_starts_for_four_players(self):
        self.server.start_game([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])

        args = call("%s %s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], self.clients[3]['name'], Protocol.EOL))
        self.clients[0]['socket'].send.assert_has_calls(args)
        self.clients[0]['socket'].send.assert_has_calls(call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
        self.clients[1]['socket'].send.assert_has_calls(args)
        self.clients[2]['socket'].send.assert_has_calls(args)
        self.clients[3]['socket'].send.assert_has_calls(args)
        assert self.clients[4]['socket'].send.call_count == 1

    def test_it_places_for_two_players(self):
        game = self.server.start_game([self.clients[0], self.clients[1]])
        game.balls_left = 1

        self.server.place(self.clients[0], '53')

        args = [call("%s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)),
            call("%s %s%s" % (Protocol.PLACE, '53', Protocol.EOL)),
            call("%s %s%s" % (Protocol.GAME_OVER, self.clients[0]['name'], Protocol.EOL))]

        args.insert(1, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
        self.clients[0]['socket'].send.assert_has_calls(args)

        args.pop(1)
        self.clients[1]['socket'].send.assert_has_calls(args)
        assert self.clients[2]['socket'].send.call_count == 1

    def test_it_places_for_three_players(self):
        game = self.server.start_game([self.clients[0], self.clients[1], self.clients[2]])
        game.balls_left = 2

        self.server.place(self.clients[0], '53')
        self.server.place(self.clients[1], '52')

        args = [call("%s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], Protocol.EOL)),
            call("%s %s%s" % (Protocol.PLACE, '53', Protocol.EOL)),
            call("%s %s%s" % (Protocol.PLACE, '52', Protocol.EOL)),
            call("%s %s%s" % (Protocol.GAME_OVER, self.clients[1]['name'], Protocol.EOL))]
        
        args.insert(1, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
        self.clients[0]['socket'].send.assert_has_calls(args)

        args.pop(1)
        args.insert(2, call("%s%s" % (Protocol.PLAY, Protocol.EOL)))
        self.clients[1]['socket'].send.assert_has_calls(args)

        args.pop(2)
        self.clients[2]['socket'].send.assert_has_calls(args)
        assert self.clients[3]['socket'].send.call_count == 1

    def test_it_places_for_four_players(self):
        game = self.server.start_game([self.clients[0], self.clients[1], self.clients[2], self.clients[3]])
        game.balls_left = 3

        self.server.place(self.clients[0], '53')
        self.server.place(self.clients[1], '52')
        self.server.place(self.clients[2], '24')

        args = [call("%s %s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], self.clients[3]['name'], Protocol.EOL)),
            call("%s %s%s" % (Protocol.PLACE, '53', Protocol.EOL)),
            call("%s %s%s" % (Protocol.PLACE, '52', Protocol.EOL)),
            call("%s %s%s" % (Protocol.PLACE, '24', Protocol.EOL)),
            call("%s %s%s" % (Protocol.GAME_OVER, self.clients[2]['name'], Protocol.EOL))]

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
        assert self.clients[4]['socket'].send.call_count == 1

    def test_it_gives_the_right_date_stats(self):
        game = self.server.start_game([self.clients[0], self.clients[1]])
        self.server.place(self.clients[0], '53')
        self.server.game_over(self.server.network_games[id(game)])

        self.server.stats(self.clients[0], Protocol.STAT_DATE, str(time.time()))
        self.server.stats(self.clients[0], Protocol.STAT_DATE, str(time.mktime(datetime.datetime(2013, 9, 3).timetuple())))

        args = [call("%s %s %s %s%s" % (Protocol.STAT, Protocol.STAT_DATE, time.time(), '1', Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.STAT, Protocol.STAT_DATE, time.mktime(datetime.datetime(2013, 9, 3).timetuple()), Protocol.UNDEFINED, Protocol.EOL))]
        self.clients[0]['socket'].send.assert_has_calls(args)

    def test_it_gives_the_right_player_stats(self):
        game = self.server.start_game([self.clients[0], self.clients[1]])
        self.server.place(self.clients[0], '53')
        self.server.game_over(self.server.network_games[id(game)])

        self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[0]['name'])
        self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[1]['name'])
        self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[2]['name'])

        args = [call("%s %s %s %s%s" % (Protocol.STAT, Protocol.STAT_PLAYER, self.clients[0]['name'], '1', Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.STAT, Protocol.STAT_PLAYER, self.clients[1]['name'], '0', Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.STAT, Protocol.STAT_PLAYER, self.clients[2]['name'], Protocol.UNDEFINED, Protocol.EOL))]
        self.clients[0]['socket'].send.assert_has_calls(args)
