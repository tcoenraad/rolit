from models.ball import Ball

class Protocol:
  
  JOIN       = 'join'
  START      = 'start'
  PLAY       = 'play'
  GAME_OVER  = 'gameover'

  RED        = 'red'
  YELLOW     = 'yellow'
  BLUE       = 'blue'
  GREEN      = 'green'

  COLORS  = {
    RED    : Ball.RED,
    YELLOW : Ball.YELLOW,
    BLUE   : Ball.BLUE,
    GREEN  : Ball.GREEN
  }