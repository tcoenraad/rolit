from termcolor import colored
from rolit.protocol import Protocol

class Helpers(object):

    @staticmethod
    def log(message):
        print("[log] %s" % message)

    @staticmethod
    def notice(notification):
        print(colored(notification, 'blue'))

    @staticmethod
    def warning(notification):
        print(colored(notification, 'yellow'))
 
    @staticmethod
    def error(notification):
        print(colored(notification, 'red'))

    @staticmethod
    def sign_data(data):

        from Crypto.PublicKey import RSA
        from Crypto.Signature import PKCS1_v1_5
        from Crypto.Hash import SHA
        from base64 import b64encode, b64decode

        private_key = open("./private_key", "r").read()
        rsa_key = RSA.importKey(private_key)
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA.new()

        digest.update(b64decode(data))
        sign = signer.sign(digest)
        return b64encode(sign)

    @staticmethod
    def verify_sign(player_name, signature, data):
        from Crypto.PublicKey import RSA
        from Crypto.Signature import PKCS1_v1_5
        from Crypto.Hash import SHA
        from base64 import b64encode, b64decode
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect(('ss-security.student.utwente.nl', 2013))
        sock.send("%s %s%s" % ("PUBLICKEY", player_name, Protocol.EOL))
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
