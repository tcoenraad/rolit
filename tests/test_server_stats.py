import pytest, time
from mock import Mock, call, patch

from rolit.server import *
from test_server import TestServer

@patch.object(random, 'shuffle', Mock())
class TestServerStats(TestServer):

    def test_it_validates_timestamp_for_date_stats(self):
        with pytest.raises(ClientError):
            self.server.stats(self.clients[0], Protocol.STAT_DATE, 'Inter-Actief')

    def test_it_validates_requested_stat(self):
        with pytest.raises(ClientError):
            self.server.stats(self.clients[0], Protocol.STAT_PLAYER + '...', self.clients[0]['name'])

    def test_it_gives_the_right_date_stats(self):
        self.clients[0]['verified'] = True
        game = self.start_game_with_two_players()

        self.server.move(self.clients[0], '5', '3')
        self.server.game_over(self.server.network_games[id(game)])

        self.server.stats(self.clients[0], Protocol.STAT_DATE, str(time.strftime("%Y-%m-%d")))
        self.server.stats(self.clients[0], Protocol.STAT_DATE, "2013-09-03")

        args = [call("%s %s %s %s %s%s" % (Protocol.STATS, Protocol.STAT_DATE, str(time.strftime("%Y-%m-%d")), self.clients[0]['name'], '1', Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.STATS, Protocol.STAT_DATE, "2013-09-03", Protocol.UNDEFINED, Protocol.EOL))]
        self.clients[0]['socket'].sendall.assert_has_calls(args)

        with pytest.raises(ClientError):
            self.server.stats(self.clients[0], Protocol.STAT_DATE, "35")
        with pytest.raises(ClientError):
            self.server.stats(self.clients[0], Protocol.STAT_DATE, "03-09-2014")

    def test_it_gives_the_right_player_stats(self):
        self.clients[0]['verified'] = True
        game = self.start_game_with_two_players()

        self.server.move(self.clients[0], '5', '3')
        self.server.game_over(self.server.network_games[id(game)])

        self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[0]['name'])
        self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[1]['name'])
        self.server.stats(self.clients[0], Protocol.STAT_PLAYER, self.clients[2]['name'])

        args = [call("%s %s %s %s%s" % (Protocol.STATS, Protocol.STAT_PLAYER, self.clients[0]['name'], '1', Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.STATS, Protocol.STAT_PLAYER, self.clients[1]['name'], '0', Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.STATS, Protocol.STAT_PLAYER, self.clients[2]['name'], Protocol.UNDEFINED, Protocol.EOL))]
        self.clients[0]['socket'].sendall.assert_has_calls(args)
