from termcolor import colored

class Helpers(object):

    @staticmethod
    def log(message):
        print("[log] %s" % message)

    @staticmethod
    def notice(notification):
        print(colored(notification, 'blue'))

    @staticmethod
    def warning(notification):
        print(colored(notification, 'yellow'))
 
    @staticmethod
    def error(notification):
        print(colored(notification, 'red'))
