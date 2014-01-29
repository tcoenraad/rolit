# -*- coding: utf-8 -*-

from rolit.ball import Ball
from rolit.protocol import Protocol

class Board(object):
    DIM = 8

    def __init__(self):
        self.board = [[Ball() for __ in range(Board.DIM)] for __ in range(Board.DIM)]
        self.board[Board.DIM/2 - 1][Board.DIM/2 - 1] = Ball(Ball.RED)
        self.board[Board.DIM/2 - 1][Board.DIM/2]     = Ball(Ball.BLUE)
        self.board[Board.DIM/2][Board.DIM/2 - 1]     = Ball(Ball.YELLOW)
        self.board[Board.DIM/2][Board.DIM/2]         = Ball(Ball.GREEN)

    def stats(self):
        stats = {
            Ball.RED    : 0,
            Ball.BLUE   : 0,
            Ball.YELLOW : 0,
            Ball.GREEN  : 0
        }

        for row in self.board:
            for field in row:
                if field == Ball(Ball.RED):
                    stats[Ball.RED] += 1
                elif field == Ball(Ball.BLUE):
                    stats[Ball.BLUE] += 1
                elif field == Ball(Ball.YELLOW):
                    stats[Ball.YELLOW] += 1
                elif field == Ball(Ball.GREEN):
                    stats[Ball.GREEN] += 1

        return stats

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
            for direction in [-1, 1]:
                fields = []

                for shift in range(1, Board.DIM):
                    x_coord = x
                    y_coord = y

                    if orientation == 'horizontal':
                        x_coord += direction * shift
                    elif orientation == 'vertical':
                        y_coord += direction * shift
                    elif orientation == 'diagonal-up':
                        x_coord += direction * shift
                        y_coord += direction * shift
                    elif orientation == 'diagonal-down':
                        x_coord -= direction * shift
                        y_coord += direction * shift

                    field = self.field(x_coord, y_coord)

                    # stop walking a direction if field is:
                        # your own color (then return all results till than)
                        # or empty (then clear the found fields as you did not find your own color)
                    if not field or field == Ball(Ball.EMPTY):
                        fields = []
                        break
                    elif field == Ball(color):
                        break
                    else:
                        fields.append(field)

                filtered_fields += fields
        return filtered_fields

    def place(self, x, y, color):
        if not self.field(x, y) == Ball(Ball.EMPTY):
            raise AlreadyOccupiedError('Field is already occupied or not on this board')

        if len(self.direct_adjacent_colors(x, y)) == 0:
            raise NotAdjacentError('Field is not directly adjacent to any field')

        filtered_adjacent_fields = self.filtered_adjacent_fields(x, y, color)
        if len(filtered_adjacent_fields) == 0 and self.any_forced_moves_left(color):
            raise ForcedMoveError('This move is not forced, while forced moves are left')

        for field in filtered_adjacent_fields:
            field.recolor(color)

        self.field(x, y).recolor(color)

    def encode(self):
        string = ""
        for y in range(Board.DIM):
            for x in range(Board.DIM):
                field = self.field(x, y)
                string += Protocol.SEPARATOR
                string += field.encode()

        return string.strip()

    @staticmethod
    def decode(board_string):
        board_fields = board_string.split(Protocol.SEPARATOR)
        board = Board()
 
        for y in range(Board.DIM):
            for x in range(Board.DIM):
                board.board[x][y] = Ball.decode(board_fields[y * Board.DIM + x])
        return board

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

class BoardError(Exception): pass
class AlreadyOccupiedError(BoardError): pass
class NotAdjacentError(BoardError): pass
class ForcedMoveError(BoardError): pass
