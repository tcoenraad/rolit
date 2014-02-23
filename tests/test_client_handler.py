import pytest
from mock import Mock, call
from socket import socket

from bin.server import ClientHandler
from rolit.server import Server
from rolit.protocol import Protocol

class TestClientHandler(object):

    def test_it_handles_eol_correctly(self):
        sock = Mock()
        return_values = ["%s " % Protocol.HANDSHAKE,
                         "Tw",
                         "an",
                         " %s 35" % Protocol.CHAT_AND_CHALLENGE,
                         "%s%s" % (Protocol.EOL, Protocol.CREATE_GAME),
                         "%s" % Protocol.EOL,
                         "%s Dit is "
                         "een test! %s" % (Protocol.CHAT, Protocol.EOL)]
        sock.recv.side_effect = lambda(self): return_values.pop(0) if len(return_values) > 0 else ""
        clienthandler = ClientHandler(Server(), sock, "mocked_client_handler")

        clienthandler.run()

        args = [call("%s %s %s%s" % (Protocol.HANDSHAKE, Server.SUPPORTS, Server.VERSION, Protocol.EOL)),
                call("%s %s %s %s%s" % (Protocol.GAME, "Twan", 0, 1, Protocol.EOL)),
                call("%s %s %s%s" % (Protocol.CHAT, "Twan", "Dit is een test!", Protocol.EOL))]
        sock.sendall.assert_has_calls(args, True)
