class Protocol(object):
    
    HANDSHAKE          = 'hello'
    JOIN               = 'joinGame'
    START              = 'startGame'
    PLAY               = 'play'
    PLACE              = 'place'
    GAME_OVER          = 'game_over'
    CHAT               = 'chat'
    CHALLENGE          = 'challenge'
    CHALLENGE_RESPONSE = 'challengeResponse'
    CHALLENGE_REJECTED = 'challenge_rejected'

    RED          = 'red'
    YELLOW       = 'yellow'
    BLUE         = 'blue'
    GREEN        = 'green'

    STATS        = 'highscore'
    STAT_DATE    = 'date'
    STAT_PLAYER  = 'player'

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
