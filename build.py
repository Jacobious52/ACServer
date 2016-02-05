import subprocess
import utils
import re
from logger import logger
import os
import glob

WRITE_LOC = 'builds/'

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

    #delete old files
    old_files = glob.glob('%s*' % WRITE_LOC)
    for f in old_files:
        os.remove(f)

    # write new files
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
    args.append('-o %stemp.o' % WRITE_LOC)

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
        p = re.compile(LINKER_PATTERN, raw_errors)
        it = p.finditer(raw_errors)
        for match in it:
            msg = match.group(0)
            errors.append('NOFILE:-1:-1: error: linker: Undefined symbols for architecture x86_64: %s' % msg)

    return errors


def strip_and_split(raw_errors):
    '''Split the block text of errors into single lines without other mess'''
    lines = raw_errors.split('\n')
    errors = []

    # collect all standard sytax errors
    # remove anything that's not an error for warning
    for line in lines:
        if utils.matches(utils.CLANG_ERROR_WARN_PATTERN, line):
            if line.startswith(WRITE_LOC):
                line = line.replace(WRITE_LOC, '')
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
