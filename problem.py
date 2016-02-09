import glob
import os

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
        prob = {'name': os.path.basename(d), 'files': files}
        problems.append(prob)
    return problems
