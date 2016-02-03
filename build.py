import subprocess
import utils
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
    args = ['g++', ' '.join([WRITE_LOC + f[KNAME] for f in files if not f[KNAME].endswith('.h')]), '-o temp.o']
    for flag in BUILD_FLAGS:
        args.append(flag)
    logger.debug('build args:' + str(args))
    return args

def build(files):
    '''Call g++ process and build with flags'''
    process = subprocess.Popen(build_args(files), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    # we don't need stdout because all errors go through stderr
    return err.strip()

def strip_and_split(raw_errors):
    '''Split the block text of errors into single lines without toolchain mess'''
    lines = raw_errors.split('\n')
    errors = []

    #remove anything that's not an error for warning
    for line in lines:
        if utils.matches_error(line):
            if line.startswith('/tmp/'):
                line = line.replace('/tmp/', '')
            logger.debug(line)
            errors.append(line)

    return errors

def compile_files(files):
    '''Compile files and return a json object of Erorrs to return to client'''
    write_files(files)
    raw_errors = build(files)
    return strip_and_split(raw_errors)
