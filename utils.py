import re
import time
import os.path

def fexists(path):
    return os.path.isfile(path)

def timestamp():
    return int(time.time())

'''pre compiled error/warning patterns'''
CLANG_ERROR_WARN_PATTERN = re.compile('(.*[\d:\d]):\s(error|warning):\s(.*)')
LOCATION_PATTERN = re.compile('(.*\..*):(\d+):(\d+)')
LINKER_PATTERN = re.compile('"(.*)",\sreferenced from:\s(.*)')


def capture_matches(pattern, string):
    '''matches against a pre compiled pattern'''
    m = []

    p = re.compile(pattern)
    it = p.finditer(string)
    for match in it:
        # match groups '0' index is the input string. we don't need that
        # e.g. match() is 1 index based
        if match.lastindex is not None:
            for i in xrange(0, match.lastindex):
                m.append(match.group(i+1))

    return m

def capture_matches(pattern, string):
    '''return a list of string matches from a regex capture match'''
    m = []

    it = pattern.finditer(string)
    for match in it:
        # match groups '0' index is the input string. we don't need that
        # e.g. match() is 1 index based
        if match.lastindex is not None:
            for i in xrange(0, match.lastindex):
                m.append(match.group(i+1))
    return m

def matches(pattern, string):
    '''simple regex test if string matches pattern'''
    p = re.compile(pattern)
    return p.match(string) is not None

def matches(pattern, string):
    '''simple matches against a pre compiled pattern'''
    return pattern.match(string) is not None
