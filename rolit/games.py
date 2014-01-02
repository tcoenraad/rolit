from game import Game
from board import Board
from ball import Ball

class TwoPlayerGame(Game):

    def __init__(self):
        super(TwoPlayerGame, self).__init__(2)

    def players(self):
        return {
            0 : Ball.RED,
            1 : Ball.GREEN
        }

class ThreePlayerGame(Game):

    def __init__(self):
        super(ThreePlayerGame, self).__init__(3)
        self.board.board[Board.DIM/2][Board.DIM/2 - 1] = Ball(Ball.YELLOW)

    def players(self):
        return {
            0 : Ball.RED,
            1 : Ball.BLUE,
            2 : Ball.GREEN
        }

class FourPlayerGame(Game):

    def __init__(self):
        super(FourPlayerGame, self).__init__(4)
        self.board.board[Board.DIM/2][Board.DIM/2 - 1] = Ball(Ball.YELLOW)
        self.board.board[Board.DIM/2][Board.DIM/2]     = Ball(Ball.GREEN)

    def players(self):
        return {
            0 : Ball.RED,
            1 : Ball.BLUE,
            2 : Ball.GREEN,
            3 : Ball.YELLOW
        }