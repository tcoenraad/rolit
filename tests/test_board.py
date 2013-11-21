from models.board import Board
from models.ball import Ball

import pytest

def test_it_setups():
  board = Board()
  assert board.field(3, 3) == 1
  assert board.field(3, 4) == 2
  assert board.field(4, 3) == 3
  assert board.field(4, 4) == 4

def test_it_takes_no_double_placements():
  board = Board()

  with pytest.raises(RuntimeError):
    board.place(3, 3, Ball.RED)

  board.place(2, 3, Ball.RED)

def test_it_only_allows_adjacent_placements():
  board = Board()

  with pytest.raises(RuntimeError):
    board.place(2, 2, Ball.RED)

  board.place(2, 3, Ball.RED)
