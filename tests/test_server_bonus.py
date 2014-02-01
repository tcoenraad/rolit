import pytest
from mock import Mock, call, patch

from rolit.server import *
from test_server import TestServer

@patch.object(random, 'shuffle', Mock())
class TestServerBonus(TestServer):

    def test_chat_when_enabled_and_in_lobby(self):
        self.server.chat(self.clients[0], "This is a test message")

        args = call("%s %s %s%s" % (Protocol.CHAT, self.clients[0]['name'], "This is a test message", Protocol.EOL))
        self.clients[0]['socket'].sendall.assert_has_calls(args)
        self.clients[1]['socket'].sendall.assert_has_calls(args)
        self.clients[2]['socket'].sendall.assert_has_calls(args)
        assert self.clients[3]['socket'].sendall.call_count == 7

    def test_chat_when_enabled_and_in_game(self):
        self.start_game_with_two_players()

        self.server.chat(self.clients[0], "This is a test message and it is my turn")
        self.server.chat(self.clients[1], "This is a test message and it is not my turn")
        self.server.chat(self.clients[2], "This is a test message and I am not in game")

        args = [call("%s %s %s%s" % (Protocol.CHAT, self.clients[0]['name'], "This is a test message and it is my turn", Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHAT, self.clients[1]['name'], "This is a test message and it is not my turn", Protocol.EOL))]
        self.clients[0]['socket'].sendall.assert_has_calls(args)
        self.clients[1]['socket'].sendall.assert_has_calls(args)

        args = call("%s %s %s%s" % (Protocol.CHAT, self.clients[2]['name'], "This is a test message and I am not in game", Protocol.EOL))
        self.clients[2]['socket'].sendall.assert_has_calls(args)

    def test_chat_with_disabled_clients(self):
        self.server.chat(self.clients[1], "This is a test message and I am not in game")

        assert self.clients[3]['socket'].sendall.call_count == 7

    def test_chat_when_disabled(self):
        with pytest.raises(ClientError):
            self.server.chat(self.clients[3], "This is a test message")

    def test_challenge_client_itself(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], "%s" % (self.clients[0]['name']))

    def test_challenge_with_too_many_people(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], "a", "b", "c", "d")

    def test_challenge_when_challengee_disabled_challenges(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], self.clients[2]['name'])

    def test_challenge_when_challenger_disabled_challenges(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[2], self.clients[0]['name'])

    def test_challenge_someone_that_does_not_exist(self):
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[0], "W.A. van Buren")

    def test_create_when_already_in_challenge(self):
        self.server.challenge(self.clients[0], self.clients[1]['name'])
        with pytest.raises(ClientError):
            self.server.create_game(self.clients[0])

    def test_challenge_someone_that_is_already_challenged(self):
        self.server.challenge(self.clients[0], self.clients[1]['name'])
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[4], self.clients[1]['name'])

    def test_challenge_someone_that_is_already_in_a_not_started_game(self):
        self.server.create_game(self.clients[0])
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[1], self.clients[0]['name'])

    def test_challenge_someone_that_is_already_in_a_started_game(self):
        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.challenge(self.clients[4], self.clients[1]['name'])

    def test_challenge_requests(self):
        self.server.challenge(self.clients[0], self.clients[1]['name'], self.clients[4]['name'])

        args = call("%s %s %s %s%s" % (Protocol.CHALLENGE, self.clients[0]['name'], self.clients[1]['name'], self.clients[4]['name'], Protocol.EOL))
        self.clients[1]['socket'].sendall.assert_has_calls(args)
        self.clients[4]['socket'].sendall.assert_has_calls(args)
        assert self.clients[3]['socket'].sendall.call_count == 7

    def test_challenge_response_when_not_challenged(self):
        with pytest.raises(ClientError):
            self.server.challenge_response(self.clients[1], Protocol.TRUE)

    def test_challenge_availability(self):
        self.server.challenge(self.clients[0], self.clients[1]['name'])
        self.server.disconnect(self.clients[1])

        args = [call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[0]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[1]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[4]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[5]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[0]['name'], Protocol.FALSE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[1]['name'], Protocol.FALSE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[0]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[1]['name'], Protocol.FALSE, Protocol.EOL))]
        self.clients[5]['socket'].sendall.assert_has_calls(args)

    def test_availability_on_connect(self):
        self.server.challenge(self.clients[0], self.clients[1]['name'])

        sock = Mock()
        self.server.connect(sock, "Bestuur_35", Protocol.CHAT_AND_CHALLENGE)
        args = [call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[0]['name'], Protocol.FALSE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[1]['name'], Protocol.FALSE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[4]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, self.clients[5]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGABLE, "Bestuur_35", Protocol.TRUE, Protocol.EOL))]
        sock.sendall.assert_has_calls(args)

    def test_challenge_request_accepted(self):
        self.server.initiate_game = Mock(wraps=self.server.initiate_game)

        self.server.challenge(self.clients[0], self.clients[1]['name'], self.clients[4]['name'])
        self.server.challenge_response(self.clients[1], Protocol.TRUE)

        with pytest.raises(ClientError):
            self.server.start_game(self.clients[0])

        self.server.challenge_response(self.clients[4], Protocol.TRUE)
        self.server.start_game(self.clients[0])
        assert sorted(self.server.initiate_game.call_args[0][0]) == sorted([self.clients[0], self.clients[1], self.clients[4]])

    def test_challenge_request_rejected(self):
        self.server.challenge(self.clients[0], self.clients[1]['name'], self.clients[4]['name'])
        self.server.challenge_response(self.clients[1], Protocol.TRUE)
        self.server.challenge_response(self.clients[4], Protocol.FALSE)

        with pytest.raises(ClientError):
            self.server.start_game(self.clients[0])

        args = [call("%s %s %s%s" % (Protocol.CHALLENGE_RESPONSE, self.clients[1]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHALLENGE_RESPONSE, self.clients[4]['name'], Protocol.FALSE, Protocol.EOL))]
        self.clients[0]['socket'].sendall.assert_has_calls(args)
        self.clients[1]['socket'].sendall.assert_has_calls(args)
        self.clients[4]['socket'].sendall.assert_has_calls(args)
        assert self.clients[3]['socket'].sendall.call_count == 7
