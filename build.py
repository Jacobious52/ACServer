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
    #TODO: create different directories for each build. because of threadedness

    # delete old files
    for f in glob.glob('%s*' % WRITE_LOC):
        os.remove(f)

    # write new files sent from the client so we can build them later
    for f in files:
        with open(WRITE_LOC + f[KNAME], 'w') as file:
            file.write(f[KBODY])

def build_args(files):
    '''Create the arg list for clang++ subprocess'''
    # compiler
    args = ['clang++']

    # source files
    for f in files:
        if f[KNAME].endswith('.cpp'):
            args.append(WRITE_LOC + f[KNAME])

    # clang flags
    args.extend(BUILD_FLAGS)
    # out object file
    args.append('-o %smain.o' % WRITE_LOC)

    logger.debug('building: %s' % ' '.join(args))

    return args

def build(files):
    '''Call g++ process and build with flags'''
    process = subprocess.Popen(build_args(files), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    # we don't need stdout because all errors go through stderr
    return err.strip()

def parse_for_linker(raw_errors):
    '''Extract different formated linker errors from the compiler'''
    errors = []

    if 'error: linker command failed' in raw_errors:
        logger.debug('Linker errors found')
        it = utils.LINKER_PATTERN.finditer(raw_errors)
        for match in it:
            msg = match.group(0)
            errors.append('NOFILE:-1:-1: error: linker: Undefined symbols for architecture x86_64: %s' % msg)

    return errors


def strip_and_split(raw_errors):
    '''Split the block text of errors into single lines without other mess'''
    lines = raw_errors.split('\n')
    errors = []

    # collect all standard sytax errors
    # remove anything that's not an error or warning
    for line in lines:
        if utils.matches(utils.CLANG_ERROR_WARN_PATTERN, line):
            if line.startswith(WRITE_LOC):
                line = line.replace(WRITE_LOC, '')
            errors.append(line)

    # now extract linker errors.
    errors.extend(parse_for_linker(raw_errors))

    return errors

def compile_files(files):
    '''Compile files and return a json object of Errors to return to client'''
    write_files(files)
    raw_errors = build(files)
    single_errors = strip_and_split(raw_errors)
    return single_errors
