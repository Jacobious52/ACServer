import subprocess
import utils
import re
from logger import logger
import os
import glob
import problem
from student import Student

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
        if utils.sanitize_fname(f[KNAME]):
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

def compile_files(files, id, problem_key):
    '''Compile files and return a json object of errors, edit dist and score to return to client'''
    write_files(files)
    raw_errors = build(files)
    errors = strip_and_split(raw_errors)

    # determine the edit distance (score) for each error
    # and check to see if the student has already had that error
    score = 0
    total_file_len = 0
    total_edit_dist = 0

    # get the original files for the selected problem
    p = problem.find(problem.PROBLEMS, problem_key)
    if p is not None:
        # loop through both sources of files simultaneously
        # add to the total_edit_dist across all files for this build
        for edited, original in zip(files, p['files']):
            ed = utils.edit_dist(original['body'], edited['body'])
            total_edit_dist += ed
            total_file_len = len(original['body'])
    else:
        logger.error('could not find problem: %s' % problem_key)

    # list for dictionary of errors. including if the error has already seen that error
    errors_dicts = []

    # compare these errors against students previous errors
    hashes = Student(id).dict['hashes']
    for error in errors:
        if not any([utils.compare_error_hash(utils.encode_error(error, total_edit_dist), h) for h in hashes]):
            score += max(0, total_file_len - total_edit_dist)
            errors_dicts.append({'body': error, 'seen': False})
        else:
            errors_dicts.append({'body': error, 'seen': True})

    s = Student(id)
    s.modify_score(score)
    s.sync()

    return (errors_dicts, total_edit_dist, score)
