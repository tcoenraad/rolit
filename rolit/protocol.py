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

    STATS        = 'stats'
    STAT_DATE    = 'stat_date'
    STAT_PLAYER  = 'stat_player'

    SEPARATOR    = ' '
    EOL          = "\r\n"
    TRUE         = '1'
    FALSE        = '0'
    UNDEFINED    = '-1'
    ERROR        = 'error'

    @staticmethod
    def coord_str(coord):
        coord_str = str(coord)
        x = int(coord_str[0])
        y = int(coord_str[1])
        return (x, y)
