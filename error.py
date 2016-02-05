import json
from logger import logger
import glob
import utils
import re

ERRORS_LOC = 'db/errors/'

def load_errors():
    all_errors = []

    errors_json = glob.glob('%s*.json' % ERRORS_LOC)
    for f in errors_json:
        logger.debug('loading error json: %s' % f)
        error = Error()
        error.load(f)
        all_errors.append(error)

    return all_errors

class Error:
    '''Class that holds all infomation about compiler errors and resolve data'''
    def __init__(self):
        # simple name of the error
        self.name = ''

        # error or warning
        self.type = ''

        # linker/syntax/sematic, etc
        self.catagories = []

        # regex pattern matching capture format for the error
        self.regex = ''

        # steps to resolving the error: questions
        self.resolve = []

        # info on why the error occured
        self.info = ''

        self.pattern = None

    def replace_resolve(self, resolve, var, to):
        #TODO: parse all levels of the resolve dict list and replace the var -> to
        return resolve

    def make_match(self, raw):
        '''factory mathod for creating a new dict of an error from a match of a raw error
            will return None if failed to match'''

        # error location data
        line = -1
        col = -1
        filename = 'NOFILE'

        # the compiler message from the error
        message_part = ''
        parsed_resolve = self.resolve

        # split the error into it's parts
        groups = utils.capture_matches(utils.CLANG_ERROR_WARN_PATTERN, raw)
        logger.debug(groups)

        if len(groups) == 3:
            #make sure (message) groups[2] matches regex
            if not utils.matches(self.pattern, groups[2]):
                return None

            #get f:l:c
            locations = utils.capture_matches(utils.LOCATION_PATTERN, groups[0])
            if len(locations) == 3:
                filename = locations[0]
                line = locations[1]
                col = locations[2]

            #check error type
            if groups[1] != self.type:
                logger.error('type check: %s not same as expected %s' % (groups[1], self.type))

            # set the message_part for later use
            message_part = groups[2]

        else:
            logger.error('incorrect error group regex matches count')
            return None

        #perform regex on msg
        var = 0
        for group in utils.capture_matches(self.pattern, message_part):
            var += 1
            parsed_resolve = self.replace_resolve(parsed_resolve, '$%d' % var, group)

        # return a constructed dict
        return  {   'name': self.name,
                    'type': self.type,
                    'catagory': self.catagories,
                    'resolve': parsed_resolve,
                    'info': self.info,
                    'file_name': filename,
                    'line': line,
                    'col': col,
                    'raw': raw    }


    def load(self, file_name):
        '''reads a json like error dict into the class'''
        jdict = {}
        with open(file_name, 'r') as f:
            jdict = json.load(f)

        # set the all params from the file
        if 'name' in jdict:
            self.name = jdict['name']
        else:
            logger.error('no "name" key in json %s' % file_name)

        if 'type' in jdict:
            self.type = jdict['type']
        else:
            logger.error('no "type" key in json %s' % file_name)

        if 'catagories' in jdict:
            self.catagory = jdict['catagories']
        else:
            logger.error('no "catagories" key in json %s' % file_name)

        if 'regex' in jdict:
            self.regex = jdict['regex']
            # pre compile the regex because it will be used many times
            self.pattern = re.compile(self.regex)
        else:
            logger.error('no "regex" key in json %s' % file_name)

        if 'resolve' in jdict:
            self.resolve = jdict['resolve']
        else:
            logger.error('no "reslove" key in json %s' % file_name)

        if 'info' in jdict:
            self.info = jdict['info']
        else:
            logger.error('no "info" key in json %s' % file_name)

        #filename/line/col etc. will be filled in by the compiler
