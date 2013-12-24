class Leaderboard(object):
  def __init__(self):
    self.scores = []

  def add_score(self, name, date, score):
    self.scores.append(self.Score(name, date, score))

  def scores_per_player(self):
    if len(self.scores) == 0:
      raise NoHighScoresError("No high scores available")

    scores_per_player = {}
    for score in self.scores:
      if score.name not in scores_per_player:
        scores_per_player[score.name] = 0
      scores_per_player[score.name] += score.score
    return scores_per_player

  def high_scores(self):
    if len(self.scores) == 0:
      raise NoHighScoresError("No high scores available")

    scores_per_player = self.scores_per_player()
    max_score = max(scores_per_player.values())
    return dict((player, score) for player, score in scores_per_player.iteritems() if score == max_score)

  def best_score_of_date(self, date):
    scores = [score for score in self.scores if score.date == date]

    if len(scores) == 0:
      raise NoHighScoresError("No high scores on this date")
    return max(scores, key = lambda x: x.score)

  def best_score_of_player(self, name):
    scores = [score for score in self.scores if score.name == name]

    if len(scores) == 0:
      raise NoHighScoresError("No high scores for this player")
    return max(scores, key = lambda x: x.score)

  class Score(object):
    def __init__(self, name, date, score):
      self.name = name
      self.date = date
      self.score = score

class NoHighScoresError(Exception): pass
