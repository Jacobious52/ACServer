import glob
import os

def load(directory):
    ''' load one problem. uses short directory names'''
    files = []
    for name in glob.glob('db/problems/%s/*' % directory):
        file_object = {'name': os.path.basename(name)}
        with open(name, 'r') as f:
            file_object['body'] = f.read()
        files.append(file_object)
    # always make main.cpp the first item.
    files.insert(0, files.pop([f['name'] for f in files].index('main.cpp')))
    prob = {'name': directory, 'files': files}
    return prob

def load_all():
    '''load all problems from problems folder'''
    problems = []
    probs_dirs = [x[0] for x in os.walk('db/problems') if x[0] is not 'db/problems']

    for d in probs_dirs:
        files = []
        for name in glob.glob('%s/*' % d):
            file_object = {'name': os.path.basename(name)}
            with open(name, 'r') as f:
                file_object['body'] = f.read()
            files.append(file_object)
        # always make main.cpp the first item.
        files.insert(0, files.pop([f['name'] for f in files].index('main.cpp')))
        prob = {'name': os.path.basename(d), 'files': files}
        problems.append(prob)
    return problems

def find(problems, key):
    ''' find a problem by key '''
    for p in problems:
        if p['name'] == key:
            return p
    return None

PROBLEMS = sorted(load_all(), key=lambda k: k['name'])
'''pre loaded and sorted problems instead of loading every call'''
