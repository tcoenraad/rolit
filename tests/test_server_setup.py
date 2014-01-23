import pytest, time
from mock import Mock, call, patch

from rolit.server import *
from test_server import TestServer

@patch.object(random, 'shuffle', Mock())
class TestServerSetup(TestServer):

    def test_it_connects(self):
        socket = Mock()
        self.server.create_game(self.clients[0])
        self.server.connect(socket, "Bestuur_35", Protocol.CHAT_AND_CHALLENGE)

        args = [call("%s %s%s" % (Protocol.HANDSHAKE, Protocol.CHAT_AND_CHALLENGE, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.NOT_STARTED, 1, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, self.clients[0]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, self.clients[1]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, self.clients[2]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, self.clients[3]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, self.clients[4]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, self.clients[5]['name'], Protocol.TRUE, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, "Bestuur_35", Protocol.TRUE, Protocol.EOL))]
        socket.send.assert_has_calls(args)

    def test_it_disconnects(self):
        self.server.lobbies = { self.clients[0]['name'] : [self.clients[0], self.clients[1], self.clients[2]] }
        self.server.join_game(self.clients[3], self.clients[0]['name'])
        self.server.disconnect(self.clients[1])
        self.server.join_game(self.clients[4], self.clients[0]['name'])
        with pytest.raises(ClientError):
            self.server.join_game(self.clients[5], self.clients[0]['name'])

        self.server.disconnect(self.clients[0])
        args = [call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.NOT_STARTED, 4, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.NOT_STARTED, 3, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.ONLINE, self.clients[1]['name'], Protocol.FALSE, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.NOT_STARTED, 4, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, self.clients[0]['name'], Protocol.UNDEFINED, 4, Protocol.EOL))]
        self.clients[5]['socket'].send.assert_has_calls(args)
        assert self.clients[5]['socket'].send.call_count == 17

    def test_it_validates_name_is_unique(self):
        with pytest.raises(ServerError):
            self.server.connect(Mock(), "Met_TOM_op_de_koffie!")

        self.server.disconnect(self.clients[0])
        self.server.connect(Mock(), "Met_TOM_op_de_koffie!")
