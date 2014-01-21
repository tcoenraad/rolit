class Protocol(object):
    
    HANDSHAKE               = 'hello'
    GAME                    = 'game'
    CREATE_GAME             = 'createGame'
    JOIN_GAME               = 'joinGame'
    START_GAME              = 'startGame'
    START                   = 'start'
    MOVE                    = 'move'
    MOVED                   = 'moveDone'
    GAME_OVER               = 'gameOver'
    CHAT                    = 'message'
    ONLINE                  = 'online'
    CHALLENGE               = 'challenge'
    CHALLENGE_RESPONSE      = 'challengeResponse'
    CHALLENGE_AVAILABLE = 'canBeChallenged'

    RED          = 'red'
    YELLOW       = 'yellow'
    BLUE         = 'blue'
    GREEN        = 'green'

    STATS        = 'highscore'
    STAT_DATE    = 'date'
    STAT_PLAYER  = 'player'

    BAREBONE           = '0'
    CHAT_ENABLED       = '1'
    CHALLENGE_ENABLED  = '2'
    CHAT_AND_CHALLENGE = '3'

    AUTH_PREFIX = 'player_'
    AUTH = 'auth'
    AUTH_OK = 'authOk'

    SEPARATOR    = ' '
    EOL          = "\r\n"
    TRUE         = '1'
    FALSE        = '0'
    UNDEFINED    = '-1'
    ERROR        = 'error'
