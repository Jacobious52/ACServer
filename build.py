import subprocess
import utils
import re
from logger import logger

WRITE_LOC = '/tmp/'

BUILD_FLAGS = ['-Wall', '-Wextra', '-pedantic', '-fno-caret-diagnostics', '-fno-diagnostics-fixit-info']

KNAME = 'name'
KBODY = 'body'

'''
Files format:
[{
    'name': '',
    'body': ''
},...]
'''

def write_files(files):
    '''Write files to temp location for compilation'''
    for f in files:
        with open(WRITE_LOC + f[KNAME], 'w') as file:
            file.write(f[KBODY])

def build_args(files):
    '''Create the arg list for g++ subprocess'''
    args = ['g++']

    for f in files:
        if f[KNAME].endswith('.cpp'):
            args.append(WRITE_LOC + f[KNAME])

    args.extend(BUILD_FLAGS)
    args.append('-o /tmp/temp.o')

    logger.debug('build args:' + str(args))

    return args

def build(files):
    '''Call g++ process and build with flags'''
    process = subprocess.Popen(build_args(files), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    # we don't need stdout because all errors go through stderr
    return err.strip()

def parse_for_linker(raw_errors):
    errors = []

    '''Extract different formated linker errors'''
    if 'error: linker command failed' in raw_errors:
        logger.debug('Linker: Errors found')
        p = re.compile('"(.*)",\sreferenced from:\s(.*)')
        it = p.finditer(raw_errors)
        for match in it:
            msg = match.group(0)
            errors.append('linker: error: Undefined symbols for architecture x86_64: %s' % msg)

    return errors


def strip_and_split(raw_errors):
    '''Split the block text of errors into single lines without other mess'''
    lines = raw_errors.split('\n')
    errors = []

    # collect all standard sytax errors
    #remove anything that's not an error for warning
    for line in lines:
        if utils.matches_error(line):
            if line.startswith('/tmp/'):
                line = line.replace('/tmp/', '')
            logger.debug(line)
            errors.append(line)

    # now extract linker errors.
    errors.extend(parse_for_linker(raw_errors))

    return errors

def compile_files(files):
    '''Compile files and return a json object of Erorrs to return to client'''
    write_files(files)
    raw_errors = build(files)
    logger.debug('build: %s' % raw_errors)
    return strip_and_split(raw_errors)
