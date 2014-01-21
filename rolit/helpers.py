from termcolor import colored
from rolit.protocol import Protocol
import time

class Helpers(object):

    @staticmethod
    def log(message):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), message))

    @staticmethod
    def notice(notification):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), colored(notification, 'blue')))

    @staticmethod
    def warning(notification):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), colored(notification, 'yellow')))
 
    @staticmethod
    def error(notification):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), colored(notification, 'red')))

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
