from rolit.board import *
from rolit.ball import Ball

import pytest

class TestBoard():

    def setup_method(self, method):
        self.board = Board()

    def test_it_setups(self):
        assert self.board.field(3, 3) == Ball(Ball.RED)
        assert self.board.field(3, 4) == Ball(Ball.BLUE)
        assert self.board.field(4, 3) == Ball(Ball.YELLOW)
        assert self.board.field(4, 4) == Ball(Ball.GREEN)

    def test_it_places_fields_vertically(self):
        assert self.board.field(3, 2) == Ball(Ball.EMPTY)
        with pytest.raises(ForcedMoveError):
            self.board.place(3, 2, Ball.RED)

        self.board.place(3, 2, Ball.BLUE)
        assert self.board.field(3, 2) == Ball(Ball.BLUE)
        assert self.board.field(3, 3) == Ball(Ball.BLUE)

    def test_it_places_fields_horizontally(self):
        assert self.board.field(5, 4) == Ball(Ball.EMPTY)
        with pytest.raises(ForcedMoveError):
            self.board.place(5, 4, Ball.RED)

        self.board.place(5, 4, Ball.BLUE)
        assert self.board.field(5, 4) == Ball(Ball.BLUE)
        assert self.board.field(4, 4) == Ball(Ball.BLUE)
    
    def test_it_places_fields_diagonally_up(self):
        assert self.board.field(5, 2) == Ball(Ball.EMPTY)
        with pytest.raises(ForcedMoveError):
            self.board.place(5, 2, Ball.RED)

        self.board.place(5, 2, Ball.BLUE)
        assert self.board.field(5, 2) == Ball(Ball.BLUE)
        assert self.board.field(4, 3) == Ball(Ball.BLUE)

        with pytest.raises(ForcedMoveError):
            self.board.place(2, 5, Ball.BLUE)

    def test_it_places_fields_diagonally_down(self):
        assert self.board.field(5, 5) == Ball(Ball.EMPTY)
        with pytest.raises(ForcedMoveError):
            self.board.place(5, 5, Ball.BLUE)
        
        self.board.place(5, 5, Ball.RED)
        assert self.board.field(5, 5) == Ball(Ball.RED)
        assert self.board.field(4, 4) == Ball(Ball.RED)

        with pytest.raises(ForcedMoveError):
            self.board.place(2, 2, Ball.RED)

    def test_it_takes_no_double_placements(self):
        self.board.place(3, 2, Ball.BLUE)

        with pytest.raises(AlreadyOccupiedError):
            self.board.place(3, 2, Ball.BLUE)

    def test_it_validates_given_coordinates_represent_a_field_on_board(self):
        with pytest.raises(AlreadyOccupiedError):
            self.board.place(-1, 0, Ball.RED)
        with pytest.raises(AlreadyOccupiedError):
            self.board.place(8, 8, Ball.RED)
        with pytest.raises(AlreadyOccupiedError):
            self.board.place('a', 'b', Ball.RED)

    def test_it_only_allows_adjacent_placements(self):
        with pytest.raises(NotAdjacentError):
            self.board.place(6, 2, Ball.GREEN)

        self.board.place(5, 3, Ball.RED)
        self.board.place(6, 2, Ball.GREEN)

        assert self.board.field(6, 2) == Ball(Ball.GREEN)
        assert self.board.field(5, 3) == Ball(Ball.GREEN)

    def test_it_allows_any_move_if_blocking_is_not_forced(self):
        with pytest.raises(ForcedMoveError):
            self.board.place(2, 2, Ball.YELLOW)

        self.board.place(5, 3, Ball.RED)
        self.board.place(2, 2, Ball.YELLOW)

    def test_an_edge_case(self):
        self.board.place(5, 5, Ball.RED)
        self.board.place(6, 6, Ball.GREEN)
        self.board.place(7, 7, Ball.RED)
        assert self.board.field(7, 7) == Ball(Ball.RED)

        self.board.place(7, 6, Ball.GREEN)
        assert self.board.field(7, 7) == Ball(Ball.RED)

    def test_an_edge_line(self):
        self.board.place(5, 5, Ball.RED)
        self.board.place(6, 6, Ball.GREEN)
        self.board.place(7, 7, Ball.RED)
        self.board.place(7, 6, Ball.GREEN)
        self.board.place(7, 5, Ball.RED)
        self.board.place(7, 4, Ball.GREEN)
        self.board.place(7, 3, Ball.RED)
        self.board.place(7, 2, Ball.GREEN)
        self.board.place(7, 1, Ball.RED)
        assert self.board.field(7, 7) == Ball(Ball.RED)

        self.board.place(7, 0, Ball.GREEN)
        assert self.board.field(7, 7) == Ball(Ball.RED)

        self.board.place(5, 3, Ball.RED)
        self.board.place(6, 0, Ball.GREEN)
        assert self.board.field(6, 0) == Ball(Ball.GREEN)

    def test_it_encodes(self):
        assert self.board.encode() == "empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty red yellow empty empty empty empty empty empty blue green empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty"

    def test_it_decode(self):
        board = Board.decode("empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty red yellow empty empty empty empty empty empty blue green empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty empty")
        assert board.field(3, 3) == Ball(Ball.RED)
        assert board.field(3, 4) == Ball(Ball.BLUE)
        assert board.field(4, 3) == Ball(Ball.YELLOW)
        assert board.field(4, 4) == Ball(Ball.GREEN)
