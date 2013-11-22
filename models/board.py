from models.ball import Ball
from termcolor import colored

class Board:
  DIM = 8

  def __init__(self):
    self.board = [[Ball.EMPTY for col in range(Board.DIM)] for row in range(Board.DIM)]

    self.board[Board.DIM/2 - 1][Board.DIM/2 - 1] = Ball.BLUE
    self.board[Board.DIM/2 - 1][Board.DIM/2]     = Ball.RED
    self.board[Board.DIM/2][Board.DIM/2 - 1]     = Ball.YELLOW
    self.board[Board.DIM/2][Board.DIM/2]         = Ball.GREEN

  def field(self, x, y):
    return self.board[x][y]

  def adjacent_fields(self, x, y):
    return [[self.field(col +  x, row + y) for col in range(-1, 2)] for row in range(-1, 2)]

  def place(self, x, y, ball):
    if not self.field(x, y) == Ball.EMPTY:
      raise RuntimeError('Field is already occupied')

    if not any(ball in subl for subl in self.adjacent_fields(x, y)):
      raise RuntimeError('Field is not adjacent to friendly field')

    self.board[x][y] = ball

  def __str__(self):
    for col in self.board:
      for row in col:
        if row == Ball.BLUE:
          print colored(Ball.BLUE, 'blue'),
        elif row == Ball.RED:
          print colored(Ball.RED, 'red'),
        elif row == Ball.YELLOW:
          print colored(Ball.YELLOW, 'yellow'),
        elif row == Ball.GREEN:
          print colored(Ball.GREEN, 'green'),
        else:
          print Ball.EMPTY,
      print