import pytest
from mock import Mock, call, patch
import socket
from base64 import b64decode

from rolit.server import *
from test_server import TestServer

authentication_socket = Mock()
authentication_socket.recv = Mock(return_value="PUBKEY MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJoIhuZ1BIJp+VFCCpzFAf5HSNL1LBNjD4WIrmSgJFIkZ8c/Jcxr+KYda+H7/w5cNYtzwuTQOqokwev+ba/hcM8CAwEAAQ==")

@patch.object(random, 'shuffle', Mock())
@patch.object(random, 'random', Mock(return_value=35))
@patch.object(socket, 'socket', Mock(return_value=authentication_socket))
class TestServerAuth(TestServer):
    
    def test_it_connects_with_authentication(self):
        sock = Mock()
        self.server.connect(sock, "player_twan", Protocol.CHAT_AND_CHALLENGE)

        args = [call("%s %s %s %s%s" % (Protocol.HANDSHAKE, Protocol.CHAT_AND_CHALLENGE, Server.VERSION, "7a4f07ef7ac81ec31e04d55faffe33bdde93ec2398c338760e0d98adab7ba5acf2c39b2da1782f45e8a5a4d337dedcc647afebddd531782af42bafae98ce7ed5", Protocol.EOL))]
        sock.sendall.assert_has_calls(args)

    def test_a_client_authenticates_itself(self):
        sock = Mock()
        client = self.server.connect(sock, "player_twan", Protocol.CHAT_AND_CHALLENGE)

        self.server.auth(client, "TH+47t9LLgJh5GgcAMmqbOC0BYXptUltzGBzJ/TpVGM0QWfuMxAq+g68k+e/QPYrmWwk7TeX5LiPgeodRAwDsA==")

        args = [call("%s%s" % (Protocol.AUTH_OK, Protocol.EOL))]
        sock.sendall.assert_has_calls(args)

    def test_a_client_authenticates_itself_incorrectly(self):
        sock = Mock()
        client = self.server.connect(sock, "player_twan", Protocol.CHAT_AND_CHALLENGE)

        with pytest.raises(ClientError):
            self.server.auth(client, "MzU=")

    def test_a_client_without_keypair_authenticates_itself(self):
        sock = Mock()
        client = self.server.connect(sock, "twan", Protocol.CHAT_AND_CHALLENGE)

        with pytest.raises(ClientError):
            self.server.auth(client, "MzU=")
