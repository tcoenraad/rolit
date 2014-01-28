from termcolor import colored

from rolit.protocol_extended import ProtocolExtended

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
            return ProtocolExtended.RED
        elif self == Ball(Ball.BLUE):
            return ProtocolExtended.BLUE
        elif self == Ball(Ball.YELLOW):
            return ProtocolExtended.YELLOW
        elif self == Ball(Ball.GREEN):
            return ProtocolExtended.GREEN
        else:
            return ProtocolExtended.EMPTY

    @staticmethod
    def decode(color):
        if color == ProtocolExtended.RED:
            return Ball(Ball.RED)
        elif color == ProtocolExtended.BLUE:
            return Ball(Ball.BLUE)
        elif color == ProtocolExtended.YELLOW:
            return Ball(Ball.YELLOW)
        elif color == ProtocolExtended.GREEN:
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
