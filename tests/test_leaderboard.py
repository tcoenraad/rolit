import pytest
import datetime

from rolit.leaderboard import *
from rolit.protocol import Protocol

class TestLeaderboard(object):
    def setup_method(self, method):
        self.leaderboard = Leaderboard()

    def test_it_gives_high_score(self):
        with pytest.raises(NoHighScoresError):
            self.leaderboard.high_scores()

        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 1)
        self.leaderboard.add_score('Eva', datetime.datetime(2013, 9, 3), 1)
        assert sorted(self.leaderboard.high_scores().keys()) == ['Eva', 'Twan']

        self.leaderboard.add_score('Eva', datetime.datetime(2013, 9, 3), 1)
        assert sorted(self.leaderboard.high_scores().keys()) == ['Eva']

        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 1)
        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 1)
        assert sorted(self.leaderboard.high_scores().keys()) == ['Twan']

    def test_it_gives_best_score_of_player(self):
        with pytest.raises(NoHighScoresError):
            self.leaderboard.best_score_of_player('Twan')

        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 1)
        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 3)
        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 2)
        self.leaderboard.add_score('Eva', datetime.datetime(2013, 9, 3), 2)
        self.leaderboard.add_score('Eva', datetime.datetime(2013, 9, 3), 1)
        assert self.leaderboard.best_score_of_player('Twan').score == 3
        assert self.leaderboard.best_score_of_player('Eva').score == 2

    def test_it_gives_best_score_of_date(self):
        with pytest.raises(NoHighScoresError):
            self.leaderboard.best_score_of_date(datetime.datetime(2013, 9, 2))

        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 1)
        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 3), 3)
        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 4), 2)
        self.leaderboard.add_score('Twan', datetime.datetime(2013, 9, 4), 4)
        assert self.leaderboard.best_score_of_date(datetime.datetime(2013, 9, 3)).score == 3

        self.leaderboard.add_score('Eva', datetime.datetime(2013, 9, 3), 5)
        self.leaderboard.add_score('Eva', datetime.datetime(2013, 9, 4), 1)
        assert self.leaderboard.best_score_of_date(datetime.datetime(2013, 9, 3)).score == 5
        assert self.leaderboard.best_score_of_date(datetime.datetime(2013, 9, 4)).score == 4
