from models.ball import Ball

class Protocol:
  
  GREET      = 'greet'
  JOIN       = 'join'
  START      = 'start'
  PLAY       = 'play'
  PLACE      = 'place'
  GAME_OVER  = 'gameover'

  RED        = 'red'
  YELLOW     = 'yellow'
  BLUE       = 'blue'
  GREEN      = 'green'

  SEPARATOR  = ' '

  COLORS  = {
    RED    : Ball.RED,
    YELLOW : Ball.YELLOW,
    BLUE   : Ball.BLUE,
    GREEN  : Ball.GREEN
  }