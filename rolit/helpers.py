from threading import Timer
import time
import socket
import sys

import ConfigParser

from termcolor import colored
from rolit.protocol import Protocol

class Helpers(object):

    @staticmethod
    def log(message):
        message = "[%s] %s" % (time.strftime("%H:%M:%S"), message)
        print(message)

    @staticmethod
    def notice(message):
        print(colored(message, 'blue'))

    @staticmethod
    def warning(message):
        print(colored(message, 'yellow'))

    @staticmethod
    def error(message):
        print(colored(message, 'red'))

    @staticmethod
    def readlines(sock):
        buffer = ''
        data = True
        while data:
            data = sock.recv(4096)
            buffer += data

            while not buffer.find(Protocol.EOL) == -1:
                line, buffer = buffer.split(Protocol.EOL, 1)
                yield line
        return

    @staticmethod
    def sign_data(private_key, data):

        from Crypto.PublicKey import RSA
        from Crypto.Signature import PKCS1_v1_5
        from Crypto.Hash import SHA

        try:
            rsa_key = RSA.importKey(private_key)
        except ValueError as e:
            Helpers.error(e)
            return
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA.new()

        digest.update(data)
        try:
            sign = signer.sign(digest)
        except TypeError as e:
            Helpers.error(e)
            return
        return sign

    @staticmethod
    def verify_sign(player_name, signature, data):

        from Crypto.PublicKey import RSA
        from Crypto.Signature import PKCS1_v1_5
        from Crypto.Hash import SHA

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

        digest.update(data)
        if signer.verify(digest, signature):
            return True
        return False
