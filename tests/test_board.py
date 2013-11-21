from models.board import Board
from models.ball import Ball

import pytest

class TestBoard():
  def setup_method(self, method):
    self.board = Board()

  def test_it_setups(self):
    assert self.board.field(3, 3) == 1
    assert self.board.field(3, 4) == 2
    assert self.board.field(4, 3) == 3
    assert self.board.field(4, 4) == 4

  def test_it_places_fields(self):
    assert self.board.field(2, 3) == 0
    self.board.place(2, 3, Ball.RED)
    assert self.board.field(2, 3) == 2

  def test_it_takes_no_double_placements(self):
    with pytest.raises(RuntimeError):
      self.board.place(3, 3, Ball.RED)

    self.board.place(2, 3, Ball.RED)

  def test_it_only_allows_adjacent_placements(self):
    with pytest.raises(RuntimeError):
      self.board.place(2, 2, Ball.RED)

    self.board.place(2, 3, Ball.RED)
