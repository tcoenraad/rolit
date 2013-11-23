# -*- coding: utf-8 -*-

from models.ball import Ball
from termcolor import colored

class Board:
  DIM = 8

  def __init__(self):
    self.board = [[Ball() for col in range(Board.DIM)] for row in range(Board.DIM)]

    self.board[Board.DIM/2 - 1][Board.DIM/2 - 1] = Ball(Ball.BLUE)
    self.board[Board.DIM/2 - 1][Board.DIM/2]     = Ball(Ball.RED)
    self.board[Board.DIM/2][Board.DIM/2 - 1]     = Ball(Ball.YELLOW)
    self.board[Board.DIM/2][Board.DIM/2]         = Ball(Ball.GREEN)

  def field(self, x, y):
    return self.board[x][y]

  def direct_adjacent_fields(self, x, y):
    return [[self.field(x + diff_x, y + diff_y) for diff_x in range(-1, 2)] for diff_y in range(-1, 2)]

  def filtered_adjacent_fields(self, x, y, ball):
    filtered_fields = []
  
    for orientation in ['horizontal', 'vertical', 'diagonal-up', 'diagonal-down']:
      for dir in [-1, 1]:
        fields = []

        for shift in range(1, Board.DIM):
          x_coord = x
          y_coord = y

          if orientation == 'horizontal':
            x_coord += dir * shift
          elif orientation == 'vertical':
            y_coord += dir * shift
          elif orientation == 'diagonal-up':
            x_coord += dir * shift
            y_coord += dir * shift
          elif orientation == 'diagonal-down':
            x_coord -= dir * shift
            y_coord += dir * shift

          if x_coord >= Board.DIM or x_coord < 0 or y_coord >= Board.DIM or y_coord < 0:
            break

          field = self.field(x_coord, y_coord)

          # stop if field is:
            # your own color
            # or empty
              # and clear the found fields as you did not find your own color
          if field == Ball(ball):
            break
          elif field == Ball(Ball.EMPTY):
            fields = []
            break
          else:
            fields.append(field)

        filtered_fields += fields

    return filtered_fields

  def place(self, x, y, ball):
    if not self.field(x, y) == Ball(Ball.EMPTY):
      raise RuntimeError('Field is already occupied')

    if len(self.direct_adjacent_fields(x, y)) == 0:
      raise RuntimeError('Field is not directly adjacent to any field')

    filtered_adjacent_fields = self.filtered_adjacent_fields(x, y, ball)
    if len(filtered_adjacent_fields) == 0:
      raise RuntimeError('Field does not have a filtered adjacent field')

    for field in filtered_adjacent_fields:
      field.recolor(ball)
    self.board[x][y].recolor(ball)

  def __str__(self):
    string = '\n'
    for y in range(Board.DIM):
      string += str(y) + '|'
      for x in range(Board.DIM):
        field = self.field(x, y)
        string += ' '
        if field == Ball(Ball.BLUE):
          string += colored(Ball.BLUE, 'blue')
        elif field == Ball(Ball.RED):
          string += colored(Ball.RED, 'red')
        elif field == Ball(Ball.YELLOW):
          string += colored(Ball.YELLOW, 'yellow')
        elif field == Ball(Ball.GREEN):
          string += colored(Ball.GREEN, 'green')
        else:
          string += str(Ball.EMPTY)
      string += '\n' # one new line per column

    string += '   '
    for col in range(Board.DIM):
      string += '– '
    string += '\n   '
    for col in range(Board.DIM):
      string += str(col) + ' '

    return string