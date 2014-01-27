from threading import Timer
import time
import socket
import sys

import ConfigParser

from termcolor import colored
from rolit.protocol import Protocol

class Helpers(object):

    class WhatsApp(object):

        __shared_state = {}
        def __init__(self):
            self.__dict__ = self.__shared_state

            if not hasattr(self, 'whatsapp'):
                config = ConfigParser.ConfigParser()
                config.read('config')
                if not config.has_option('whatsapp', 'phone'):
                    self.whatsapp = None
                    return

                self.config = config

                sys.path.append('./lib/python_whatsapp')
                import whatsappy
                from base64 import b64decode

                self.whatsapp = whatsappy.Client(number=config.get('whatsapp', 'phone'), secret=b64decode(config.get('whatsapp', 'secret')))
                self.whatsapp.login()

                self.timer = Timer(self.whatsapp.PING_INTERVAL, self._ping, ())
                self.timer.daemon = True
                self.timer.start()

                Helpers.error_and_whatsapp("WhatsApp connection established for `%s`" % socket.gethostname())

        def _ping(self):
            try:
                self.whatsapp._ping()
                self.whatsapp.last_ping = time.time()
            except IOError:
                del self.whatsapp
                self.timer.cancel()
                Helpers.error_and_whatsapp("Connection lost to WhatsApp while pinging!")

        def send(self, message):
            if self.whatsapp:
                try:
                    self.whatsapp.group_message(self.config.get('whatsapp', 'group_id'), message)
                except IOError:
                    del self.whatsapp
                    self.timer.cancel()
                    Helpers.error_and_whatsapp("Connection lost to WhatsApp while sending `%s`!" % message)

    def whatsapp(func):
        def inner(*args, **kwargs):
            Helpers.WhatsApp().send(args[0])
            return func(*args, **kwargs)
        return inner

    @staticmethod
    def log(message):
        message = "[%s] %s" % (time.strftime("%H:%M:%S"), message)
        print(message)

    @staticmethod
    @whatsapp
    def log_and_whatsapp(message):
        Helpers.log(message)

    @staticmethod
    def notice(message):
        print(colored(message, 'blue'))

    @staticmethod
    @whatsapp
    def notice_and_whatsapp(message):
        Helpers.notice(message)

    @staticmethod
    def warning(message):
        print(colored(message, 'yellow'))

    @staticmethod
    @whatsapp
    def warning_and_whatsapp(message):
        Helpers.log(message)

    @staticmethod
    def error(message):
        print(colored(message, 'red'))

    @staticmethod
    @whatsapp
    def error_and_whatsapp(message):
        Helpers.log(message)

    @staticmethod
    def sign_data(private_key, data):

        from Crypto.PublicKey import RSA
        from Crypto.Signature import PKCS1_v1_5
        from Crypto.Hash import SHA
        from base64 import b64encode, b64decode

        try:
            rsa_key = RSA.importKey(private_key)
        except ValueError as e:
            Helpers.error(e)
            return
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA.new()

        digest.update(b64decode(data))
        try:
            sign = signer.sign(digest)
        except TypeError as e:
            Helpers.error(e)
            return
        return b64encode(sign)

    @staticmethod
    def verify_sign(player_name, signature, data):
        from Crypto.PublicKey import RSA
        from Crypto.Signature import PKCS1_v1_5
        from Crypto.Hash import SHA
        from base64 import b64decode
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect(('ss-security.student.utwente.nl', 2013))
        sock.send("%s %s%s" % ("PUBLICKEY", player_name, Protocol.EOL))
        # assert 0
        response = sock.recv(4096)

        if not response:
            return False

        response = response.strip().split(" ")
        if response[0] == "ERROR":
            return False

        pub_key  = "-----BEGIN PUBLIC KEY-----\n"
        pub_key += response[1]
        pub_key += "\n-----END PUBLIC KEY-----\n"
        rsa_key = RSA.importKey(pub_key)
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA.new()

        digest.update(b64decode(data))
        if signer.verify(digest, b64decode(signature)):
            return True
        return False
