from termcolor import colored

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

  def __str__(self):
    if self == Ball(Ball.RED):
      return colored(Ball.RED, 'red')
    elif self == Ball(Ball.YELLOW):
      return colored(Ball.YELLOW, 'yellow')
    elif self == Ball(Ball.BLUE):
      return colored(Ball.BLUE, 'blue')
    elif self == Ball(Ball.GREEN):
      return colored(Ball.GREEN, 'green')
    else:
      return str(Ball.EMPTY)
