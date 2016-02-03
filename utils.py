import re

'''pre compiled error/warning pattern'''
CLANG_ERROR_WARN_PATTERN = re.compile('(.*):\s(error|warning):\s(.*)')

def matches_error(string):
    '''return if string matches a clang warning or error format'''
    return CLANG_ERROR_WARN_PATTERN.match(string) is not None

def r_matches(pattern, string):
    '''simple regex test if string matches pattern'''
    p = re.compile(pattern)
    return p.match(string) is not None
