from models.ball import Ball

class Protocol(object):
    
    GREET              = 'greet'
    JOIN               = 'join'
    START              = 'start'
    PLAY               = 'play'
    PLACE              = 'place'
    GAME_OVER          = 'game_over'
    CHAT               = 'chat'
    CHALLENGE          = 'challenge'
    CHALLENGE_RESPONSE = 'challenge_response'
    CHALLENGE_REJECTED = 'challenge_rejected'

    RED          = 'red'
    YELLOW       = 'yellow'
    BLUE         = 'blue'
    GREEN        = 'green'

    STAT_REQUEST = 'stat_request'
    STAT         = 'stat'
    STAT_DATE    = 'date'
    STAT_PLAYER  = 'player'

    SEPARATOR    = ' '
    EOL          = "\r\n"
    TRUE         = '1'
    FALSE        = '0'
    UNDEFINED    = '-1'

    COLORS  = {
    RED    : Ball.RED,
    YELLOW : Ball.YELLOW,
    BLUE   : Ball.BLUE,
    GREEN  : Ball.GREEN
    }