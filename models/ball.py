class Ball:

  EMPTY  = 0
  RED    = 1
  YELLOW = 2
  BLUE   = 3
  GREEN  = 4

  def __init__(self, color = EMPTY):
    self.color = color

  def recolor(self, color):
    self.color = color

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.color == other.color

  def __ne__(self, other):
    return not self.__eq__(other)
