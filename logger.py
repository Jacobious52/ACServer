import pprint

#TODO: do something better with this

pp = pprint.PrettyPrinter(indent=4)

level = 0

class logger:
    @staticmethod
    def debug(string):
        if level <= 0:
            pp.pprint('DEBUG: %s' % string)

    @staticmethod
    def info(string):
        if level <= 1:
            pp.pprint('INFO: %s' % string)

    @staticmethod
    def warn(string):
        if level <= 2:
            pp.pprint('WARN: %s' % string)

    @staticmethod
    def error(string):
        if level <= 3:
            pp.pprint('ERROR: %s' % string)
