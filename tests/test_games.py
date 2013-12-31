from models.games import *
from models.game import *
from models.board import *
from models.ball import Ball

import pytest

class TestGame():

    def test_it_restricts_colors_per_player(self):
        two_player_game = TwoPlayerGame()

        two_player_game.place(5, 3, Ball.RED)

        with pytest.raises(NotAllowedColorError):
            two_player_game.place(5, 2, Ball.BLUE)
            two_player_game.place(2, 2, Ball.YELLOW)

        two_player_game.place(2, 2, Ball.GREEN)

        with pytest.raises(NotAllowedColorError):
            two_player_game.place(4, 2, Ball.GREEN)
        
    def test_it_gives_right_winners_for_two_player_games(self):
        two_player_game = TwoPlayerGame()
        two_player_game.balls_left = 6

        assert two_player_game.winning_players() == [0, 1]

        two_player_game.place(5, 3, Ball.RED)
        assert two_player_game.winning_players() == [0]

        two_player_game.place(4, 2, Ball.GREEN)
        two_player_game.place(5, 5, Ball.RED)
        two_player_game.place(2, 5, Ball.GREEN)
        assert two_player_game.winning_players() == [0, 1]

        two_player_game.place(2, 4, Ball.RED)
        with pytest.raises(GameOverError):
            two_player_game.place(2, 3, Ball.GREEN)
        assert two_player_game.winning_players() == [1]

    def test_it_gives_right_winners_for_three_player_games(self):
        three_player_game = ThreePlayerGame()
        three_player_game.balls_left = 5

        assert three_player_game.winning_players() == [0, 1, 2]

        three_player_game.place(3, 5, Ball.RED)
        assert three_player_game.winning_players() == [0]
        
        three_player_game.place(2, 3, Ball.BLUE)
        three_player_game.place(2, 6, Ball.GREEN)
        three_player_game.place(5, 5, Ball.RED)

        with pytest.raises(GameOverError):
            three_player_game.place(5, 3, Ball.BLUE)
        assert three_player_game.winning_players() == [1]

    def test_it_gives_right_winners_for_four_player_games(self):
        four_player_game = FourPlayerGame()
        four_player_game.balls_left = 4

        assert four_player_game.winning_players() == [0, 1, 2, 3]

        four_player_game.place(3, 5, Ball.RED)
        four_player_game.place(2, 3, Ball.BLUE)
        assert four_player_game.winning_players() == [0]

        four_player_game.place(2, 6, Ball.GREEN)
        assert four_player_game.winning_players() == [2]

        with pytest.raises(GameOverError):
                four_player_game.place(2, 5, Ball.YELLOW)
        assert four_player_game.winning_players() == [2, 3]
