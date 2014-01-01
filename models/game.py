import abc

from models.board import Board
from models.ball import Ball

class Game(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, player_amount):
        self.board = Board()

        self.board.board[Board.DIM/2 - 1][Board.DIM/2 - 1] = Ball(Ball.RED)
        self.board.board[Board.DIM/2 - 1][Board.DIM/2]     = Ball(Ball.BLUE)

        self.balls_left = Board.DIM * Board.DIM - player_amount
        self.player_amount = player_amount

        self.current_player = 0

    @abc.abstractmethod
    def players(self):
        return

    def winning_players(self):
        stats = self.board.stats()

        player_stats = dict((color, amount) for color, amount in stats.items() if color in self.players().values())
        player_max = max(player_stats.values())

        return [player for (player, color) in self.players().items() if stats[color] == player_max]

    def place(self, x, y):
        color = self.players()[self.current_player]

        self.board.place(x, y, color)
        self.current_player = (self.current_player + 1) % self.player_amount

        self.balls_left -= 1
        if self.balls_left == 0:
            raise GameOverError('Game is over and won by %s' % self.winning_players())

class GameOverError(Exception): pass
