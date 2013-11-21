from models.ball import Ball

class Board:
  def __init__(self):
    self.board = [[Ball.EMPTY for col in range(8)] for row in range(8)]

    self.board[3][3] = Ball.BLUE
    self.board[3][4] = Ball.RED
    self.board[4][3] = Ball.YELLOW
    self.board[4][4] = Ball.GREEN

  def field(self, x, y):
    return self.board[x][y]

  def place(self, x, y, ball):
    if not self.field(x,y) == Ball.EMPTY:
      raise RuntimeError('Field is already placed')

    adjacent_fields = [[self.field(col +  x, row + y) for col in range(-1, 2)] for row in range(-1, 2)]

    if not any(ball in subl for subl in adjacent_fields):
      raise RuntimeError('Field is not adjacent')

    self.board[x][y] = ball