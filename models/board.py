# -*- coding: utf-8 -*-

from models.ball import Ball

class Board:
  DIM = 8

  def __init__(self):
    self.board = [[Ball() for col in range(Board.DIM)] for row in range(Board.DIM)]

  def winning_colors(self):
    colors = {
      Ball.RED    : 0,
      Ball.YELLOW : 0,
      Ball.BLUE   : 0,
      Ball.GREEN  : 0
    }

    for row in self.board:
      for field in row:
        if field == Ball(Ball.RED):
          colors[Ball.RED] += 1
        elif field == Ball(Ball.YELLOW):
          colors[Ball.YELLOW] += 1
        elif field == Ball(Ball.BLUE):
          colors[Ball.BLUE] += 1
        elif field == Ball(Ball.GREEN):
          colors[Ball.GREEN] += 1

    highest = max(colors.values())

    return sorted([color for color, v in colors.items() if v == highest])

  def field(self, x, y):
    if x >= Board.DIM or x < 0 or y >= Board.DIM or y < 0:
      return False
    return self.board[x][y]

  def direct_adjacent_fields(self, x, y):
    return [self.field(x + offset_x, y + offset_y) for offset_x in range(-1, 2) for offset_y in range(-1, 2)]

  def direct_adjacent_colors(self, x, y):
    return filter((lambda x: x != Ball(Ball.EMPTY)), self.direct_adjacent_fields(x, y))

  def any_forced_moves_left(self, color):
    for x in range(Board.DIM):
      for y in range(Board.DIM):
        if len(self.direct_adjacent_colors(x, y)) == 0:
          continue
        elif len(self.filtered_adjacent_fields(x, y, color)) > 0:
          return True

    return False

  def filtered_adjacent_fields(self, x, y, color):
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

          field = self.field(x_coord, y_coord)

          if not field:
            break

          # stop walking a direction if field is:
            # your own color (then return all results till than)
            # or empty (then clear the found fields as you did not find your own color)
          if field == Ball(color):
            break
          elif field == Ball(Ball.EMPTY):
            fields = []
            break
          else:
            fields.append(field)

        filtered_fields += fields

    return filtered_fields

  def place(self, x, y, color):
    if not self.field(x, y) == Ball(Ball.EMPTY):
      raise AlreadyOccupiedError('Field is already occupied')

    if len(self.direct_adjacent_colors(x, y)) == 0:
      raise NotAdjacentError('Field is not directly adjacent to any field')

    filtered_adjacent_fields = self.filtered_adjacent_fields(x, y, color)

    if len(filtered_adjacent_fields) == 0 and self.any_forced_moves_left(color):
      raise ForcedMoveError('This move is not forced and there are forced moves left')

    for field in filtered_adjacent_fields:
      field.recolor(color)
    self.board[x][y].recolor(color)

  def __str__(self):
    string = '\n'
    for y in range(Board.DIM):
      string += str(y) + '|'
      for x in range(Board.DIM):
        field = self.field(x, y)
        string += ' '
        string += str(field)
      string += '\n' # one new line per column

    string += '   '
    for col in range(Board.DIM):
      string += '– '
    string += '\n   '
    for col in range(Board.DIM):
      string += str(col) + ' '

    return string

class AlreadyOccupiedError(Exception): pass

class NotAdjacentError(Exception): pass

class ForcedMoveError(Exception): pass