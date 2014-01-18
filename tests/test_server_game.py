import pytest
from mock import Mock, call, patch

from rolit.server import *
from test_server import TestServer

@patch.object(random, 'shuffle', Mock())
class TestServerGame(TestServer):

    def test_it_ensures_that_a_game_goes_game_over_once(self):
        self.server.game_over = Mock(wraps=self.server.game_over)

        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '0', '0')
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '0', '0')
        assert self.server.game_over.call_count == 1

    def test_it_validates_given_number_represents_a_field_on_board(self):
        self.server.game_over = Mock(wraps=self.server.game_over)

        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '-', '1')

        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '8', '8')

        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], 'a', 'b')

        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '0', '000')

        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '3', '3')
        assert self.server.game_over.call_count == 5

    def test_it_validates_client_is_in_game(self):
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '5', '3')

        game = self.start_game_with_two_players()
        game.balls_left = 1

        self.server.move(self.clients[0], '5', '3')
        with pytest.raises(ClientError):
            self.server.move(self.clients[0], '5', '3')

    def test_it_validates_it_is_clients_turn(self):
        self.start_game_with_two_players()
        with pytest.raises(ClientError):
            self.server.move(self.clients[1], '5', '2')

    def test_it_cannot_create_a_game_twice(self):
        self.server.create_game(self.clients[0])

        with pytest.raises(ClientError):
            self.server.create_game(self.clients[0])

    def test_it_cannot_create_a_game_after_joining(self):
        self.server.create_game(self.clients[0])
        self.server.join_game(self.clients[1], self.clients[0]['name'])

        with pytest.raises(ClientError):
            self.server.create_game(self.clients[1])

    def test_it_cannot_join_twice(self):
        self.server.create_game(self.clients[0])
        self.server.join_game(self.clients[1], self.clients[0]['name'])

        with pytest.raises(ClientError):
            self.server.join_game(self.clients[1], self.clients[0]['name'])

    def test_it_cannot_join_after_creating_a_game(self):
        self.server.create_game(self.clients[0])

        with pytest.raises(ClientError):
            self.server.join_game(self.clients[0], self.clients[0]['name'])

    def test_it_cannot_join_before_game_is_created(self):
        with pytest.raises(ClientError):
            self.server.join_game(self.clients[1], self.clients[0]['name'])
        self.server.create_game(self.clients[0])
        self.server.join_game(self.clients[1], self.clients[0]['name'])

    def test_it_validates_max_number_of_players(self):
        self.server.create_game(self.clients[0])
        self.server.join_game(self.clients[1], self.clients[0]['name'])
        self.server.join_game(self.clients[2], self.clients[0]['name'])
        self.server.join_game(self.clients[3], self.clients[0]['name'])

        with pytest.raises(ClientError):
            self.server.join_game(self.clients[4], self.clients[0]['name'])

    def test_it_validates_starts(self):
        with pytest.raises(ClientError):
            self.server.start_game(self.clients[0])

        self.server.create_game(self.clients[0])
        with pytest.raises(ClientError):
            self.server.start_game(self.clients[0])

    def test_game_goes_game_over_on_disconnect(self):
        self.start_game_with_two_players()
        self.server.disconnect(self.clients[1])

        args = "%s %s %s%s" % (Protocol.GAME_OVER, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)
        self.clients[0]['socket'].send.assert_has_calls(call(args))

    def test_it_starts_for_two_players(self):
        self.server.create_game(self.clients[0])
        self.server.join_game(self.clients[1], self.clients[0]['name'])
        self.server.start_game(self.clients[0])

        args = [call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 1, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 2, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.TRUE, 2, Protocol.EOL))]
        self.clients[2]['socket'].send.assert_has_calls(args)

    def test_it_starts_for_three_players(self):
        self.server.create_game(self.clients[0])
        self.server.join_game(self.clients[1], self.clients[0]['name'])
        self.server.join_game(self.clients[2], self.clients[0]['name'])
        self.server.start_game(self.clients[0])

        args = [call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 1, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 2, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 3, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.TRUE, 3, Protocol.EOL))]
        self.clients[3]['socket'].send.assert_has_calls(args)

    def test_it_starts_for_four_players(self):
        self.server.create_game(self.clients[0])
        self.server.join_game(self.clients[1], self.clients[0]['name'])
        self.server.join_game(self.clients[2], self.clients[0]['name'])
        self.server.join_game(self.clients[3], self.clients[0]['name'])
        self.server.start_game(self.clients[0])

        args = [call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 1, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 2, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 3, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.FALSE, 4, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.TRUE, 4, Protocol.EOL))]
        self.clients[4]['socket'].send.assert_has_calls(args)

    def test_it_moves_for_two_players(self):
        game = self.start_game_with_two_players()
        game.balls_left = 1

        self.server.move(self.clients[0], '5', '3')

        args = [call("%s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], Protocol.EOL)),
            call("%s %s %s%s" % (Protocol.MOVED, '5', '3', Protocol.EOL)),
            call("%s %s%s" % (Protocol.GAME_OVER, self.clients[0]['name'], Protocol.EOL))]

        args.insert(1, call("%s%s" % (Protocol.MOVE, Protocol.EOL)))
        self.clients[0]['socket'].send.assert_has_calls(args)

        args.pop(1)
        self.clients[1]['socket'].send.assert_has_calls(args)
        assert self.clients[2]['socket'].send.call_count == 6

    def test_it_moves_for_three_players(self):
        game = self.start_game_with_three_players()
        game.balls_left = 2

        self.server.move(self.clients[0], '5', '3')
        self.server.move(self.clients[1], '5', '2')

        args = [call("%s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], Protocol.EOL)),
            call("%s %s %s%s" % (Protocol.MOVED, '5', '3', Protocol.EOL)),
            call("%s %s %s%s" % (Protocol.MOVED, '5', '2', Protocol.EOL)),
            call("%s %s%s" % (Protocol.GAME_OVER, self.clients[1]['name'], Protocol.EOL))]
        
        args.insert(1, call("%s%s" % (Protocol.MOVE, Protocol.EOL)))
        self.clients[0]['socket'].send.assert_has_calls(args)

        args.pop(1)
        args.insert(2, call("%s%s" % (Protocol.MOVE, Protocol.EOL)))
        self.clients[1]['socket'].send.assert_has_calls(args)

        args.pop(2)
        self.clients[2]['socket'].send.assert_has_calls(args)
        assert self.clients[3]['socket'].send.call_count == 5

    def test_it_moves_for_four_players(self):
        game = self.start_game_with_four_players()
        game.balls_left = 3

        self.server.move(self.clients[0], '5', '3')
        self.server.move(self.clients[1], '5', '2')
        self.server.move(self.clients[2], '2', '4')

        args = [call("%s %s %s %s %s%s" % (Protocol.START, self.clients[0]['name'], self.clients[1]['name'], self.clients[2]['name'], self.clients[3]['name'], Protocol.EOL)),
            call("%s %s %s%s" % (Protocol.MOVED, '5', '3', Protocol.EOL)),
            call("%s %s %s%s" % (Protocol.MOVED, '5', '2', Protocol.EOL)),
            call("%s %s %s%s" % (Protocol.MOVED, '2', '4', Protocol.EOL)),
            call("%s %s%s" % (Protocol.GAME_OVER, self.clients[2]['name'], Protocol.EOL))]

        args.insert(1, call("%s%s" % (Protocol.MOVE, Protocol.EOL)))
        self.clients[0]['socket'].send.assert_has_calls(args)

        args.pop(1)
        args.insert(2, call("%s%s" % (Protocol.MOVE, Protocol.EOL)))
        self.clients[1]['socket'].send.assert_has_calls(args)

        args.pop(2)
        args.insert(3, call("%s%s" % (Protocol.MOVE, Protocol.EOL)))
        self.clients[2]['socket'].send.assert_has_calls(args)

        args.pop(3)
        self.clients[3]['socket'].send.assert_has_calls(args)
        assert self.clients[4]['socket'].send.call_count == 5
