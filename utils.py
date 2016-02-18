import re
import time
import os.path

def print_table(table):
    '''prints a 2d array in matri format'''
    for row in table:
        print row
    print ''

def edit_dist(s1, s2):
    '''calc the minimum edit distance between s1 and s2'''
    l1 = len(s1)
    l2 = len(s2)

    # if one string is empty it's distance is the length of the other
    if l1 == 0:
        return l2
    if l2 == 0:
        return l1

    # create the table l1xl2
    table = [[0 for j in xrange(l2)] for i in range(l1)]

    replace_cost = lambda w1, w2, i1, i2: int(not w1[i1] == w2[i2])

    # edit dist of last character
    table[l1-1][l2-1] = replace_cost(s1, s2, l1-1, l2-1)

    # loop backwards along the rest of s2
    for j in xrange(l2-2, -1, -1):
        table[l1-1][j] = 1 + table[l1-1][j+1]

    # loop backwards along the rest of s1
    for i in xrange(l1-2, -1, -1):
        table[i][l2-1] = 1 + table[i+1][l2-1]

    # dynamic recurrance
    for i in xrange(l1-2, -1, -1):
        for j in xrange(l2-2, -1, -1):
            replace = replace_cost(s1, s2, i, j) + table[i+1][j+1]
            delete = 1 + table[i+1][j]
            insert = 1 + table[i][j+1]
            table[i][j] = min(replace, delete, insert)

    return table[0][0]

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
