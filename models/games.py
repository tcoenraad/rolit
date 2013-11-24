from game import Game
from board import Board
from ball import Ball

class TwoPlayerGame(Game):

  def __init__(self):
    super(TwoPlayerGame, self).__init__(2)

  def players(self):
    return {
      0 : Ball.RED,
      1 : Ball.YELLOW
    }

  def free_colors(self):
    return [Ball.BLUE, Ball.GREEN]

class ThreePlayerGame(Game):

  def __init__(self):
    super(ThreePlayerGame, self).__init__(3)
    self.board.board[Board.DIM/2][Board.DIM/2 - 1] = Ball(Ball.BLUE)

  def players(self):
    return {
      0 : Ball.RED,
      1 : Ball.YELLOW,
      2 : Ball.BLUE
    }

  def free_colors(self):
    return [Ball.GREEN]

class FourPlayerGame(Game):

  def __init__(self):
    super(FourPlayerGame, self).__init__(4)
    self.board.board[Board.DIM/2][Board.DIM/2 - 1] = Ball(Ball.BLUE)
    self.board.board[Board.DIM/2][Board.DIM/2]     = Ball(Ball.GREEN)

  def players(self):
    return {
      0 : Ball.RED,
      1 : Ball.YELLOW,
      2 : Ball.BLUE,
      3 : Ball.GREEN
    }

  def free_colors(self):
    return []
