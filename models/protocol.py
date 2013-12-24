from models.ball import Ball

class Protocol(object):
  
  GREET       = 'greet'
  JOIN        = 'join'
  START       = 'start'
  PLAY        = 'play'
  PLACE       = 'place'
  GAME_OVER   = 'gameover'
 
  RED         = 'red'
  YELLOW      = 'yellow'
  BLUE        = 'blue'
  GREEN       = 'green'
 
  STAT        = 'stat'
  STAT_DATE   = 'date'
  STAT_PLAYER = 'player'
 
  SEPARATOR   = ' '
  EOL         = "\r\n"

  COLORS  = {
    RED    : Ball.RED,
    YELLOW : Ball.YELLOW,
    BLUE   : Ball.BLUE,
    GREEN  : Ball.GREEN
  }