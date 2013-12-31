from termcolor import colored

from models.protocol import Protocol
from models.protocol_extended import ProtocolExtended

class Ball(object):

    EMPTY  = 0
    RED    = 1
    YELLOW = 2
    BLUE   = 3
    GREEN  = 4

    def __init__(self, color = EMPTY):
        self.color = color

    def recolor(self, color):
        self.color = color

    def encode(self):
        if self == Ball(Ball.RED):
            return Protocol.RED
        elif self == Ball(Ball.BLUE):
            return Protocol.BLUE
        elif self == Ball(Ball.YELLOW):
            return Protocol.YELLOW
        elif self == Ball(Ball.GREEN):
            return Protocol.GREEN
        else:
            return ProtocolExtended.EMPTY

    @staticmethod
    def decode(color):
        if color == Protocol.RED:
            return Ball(Ball.RED)
        elif color == Protocol.BLUE:
            return Ball(Ball.BLUE)
        elif color == Protocol.YELLOW:
            return Ball(Ball.YELLOW)
        elif color == Protocol.GREEN:
            return Ball(Ball.GREEN)
        else:
            return Ball(Ball.EMPTY)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.color == other.color

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self == Ball(Ball.RED):
            return colored(Ball.RED, 'red')
        elif self == Ball(Ball.BLUE):
            return colored(Ball.BLUE, 'blue')
        elif self == Ball(Ball.YELLOW):
            return colored(Ball.YELLOW, 'yellow')
        elif self == Ball(Ball.GREEN):
            return colored(Ball.GREEN, 'green')
        else:
            return str(Ball.EMPTY)
