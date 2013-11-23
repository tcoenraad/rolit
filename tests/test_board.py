from models.board import Board
from models.ball import Ball

import pytest

class TestBoard():
  def setup_method(self, method):
    self.board = Board()

  def test_it_setups(self):
    assert self.board.field(3, 3) == Ball(Ball.BLUE)
    assert self.board.field(3, 4) == Ball(Ball.RED)
    assert self.board.field(4, 3) == Ball(Ball.YELLOW)
    assert self.board.field(4, 4) == Ball(Ball.GREEN)

  def test_it_places_fields_vertically(self):
    assert self.board.field(3, 2) == Ball(Ball.EMPTY)
    with pytest.raises(RuntimeError):
      self.board.place(3, 2, Ball.BLUE)

    self.board.place(3, 2, Ball.RED)

    assert self.board.field(3, 2) == Ball(Ball.RED)
    assert self.board.field(3, 3) == Ball(Ball.RED)

  def test_it_places_fields_horizontally(self):
    assert self.board.field(5, 4) == Ball(Ball.EMPTY)
    with pytest.raises(RuntimeError):
      self.board.place(5, 4, Ball.BLUE)

    self.board.place(5, 4, Ball.RED)

    assert self.board.field(5, 4) == Ball(Ball.RED)
    assert self.board.field(4, 4) == Ball(Ball.RED)
  
  def test_it_places_fields_diagonally_up(self):
    assert self.board.field(5, 2) == Ball(Ball.EMPTY)
    with pytest.raises(RuntimeError):
      self.board.place(5, 2, Ball.BLUE)

    self.board.place(5, 2, Ball.RED)

    assert self.board.field(5, 2) == Ball(Ball.RED)
    assert self.board.field(4, 3) == Ball(Ball.RED)

  def test_it_places_fields_diagonally_down(self):
    assert self.board.field(5, 5) == Ball(Ball.EMPTY)
    with pytest.raises(RuntimeError):
      self.board.place(5, 5, Ball.RED)
    
    self.board.place(5, 5, Ball.BLUE)

    assert self.board.field(5, 5) == Ball(Ball.BLUE)
    assert self.board.field(4, 4) == Ball(Ball.BLUE)

  def test_it_takes_no_double_placements(self):
    self.board.place(3, 2, Ball.RED)

    with pytest.raises(RuntimeError):
      self.board.place(3, 2, Ball.RED)

  def test_it_only_allows_adjacent_placements(self):
    with pytest.raises(RuntimeError):
      self.board.place(6, 2, Ball.GREEN)

    self.board.place(5, 3, Ball.BLUE)
    self.board.place(6, 2, Ball.GREEN)

    assert self.board.field(5, 3) == Ball(Ball.GREEN)