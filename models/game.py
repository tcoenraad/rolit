from models.board import Board
from models.ball import Ball

class Game(object):
  def __init__(self, player_amount):
    self.board = Board()

    self.board.board[Board.DIM/2 - 1][Board.DIM/2 - 1] = Ball(Ball.RED)
    self.board.board[Board.DIM/2 - 1][Board.DIM/2]     = Ball(Ball.YELLOW)

    self.balls_left = Board.DIM * Board.DIM - player_amount
    self.player_amount = player_amount

    self.current_player = 0

  def winning_players(self):
    stats = self.board.stats()

    player_stats = dict((color, amount) for color, amount in stats.items() if color in self.players().values())
    player_max = max(player_stats.values())

    return [player for (player, color) in self.players().items() if stats[color] == player_max]

  def place(self, x, y, color):
    if color != self.players()[self.current_player]:
      raise NotAllowedColorError('This is not your color, pal!')

    self.board.place(x, y, color)
    self.current_player = (self.current_player + 1) % self.player_amount

    self.balls_left -= 1
    if self.balls_left == 0:
      raise GameOverError('Game is over and won by %s' % self.winning_players())

class NotAllowedColorError(Exception): pass
class GameOverError(Exception): pass
