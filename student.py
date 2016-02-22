import os
import json
import glob
import utils
import problem
from logger import logger

STUDENTS_LOC = 'db/students/'

def list_all():
    '''list all the students who have a record'''
    students = []
    for f in glob.glob('%s*' % STUDENTS_LOC):
        # remove the path and extension
        students.append(os.path.basename(f)[0:-5])
    print students
    return students

class Student:
    '''class to manipulate a student model dictionary'''
    def __init__(self, id):
        self.id = id
        self.dict = {}

        # if not created, creat new one
        if not utils.fexists(self.fpath()):
            self.create()

        # load the previous or newly created
        self.load()

    def process_error_hashes(self, errors, total_edit_dist):
        ''' add unique hashes of the errors for use with scoring the users next inputs. '''
        for error in errors:
            h = utils.encode_error(error, total_edit_dist)
            print 'hash ' + str(h)

            # we don't want to add hashes the user has entered before. so they can't cheat
            if h not in self.dict['hashes']:
                self.dict['hashes'].append(h)

    def create_action_build(self, problem_key, files, errors):
        ''' create an build action for this user'''
        total_edit_dist = 0

        # get the original files for the selected problem
        p = problem.find(problem.PROBLEMS, problem_key)
        if p is not None:
            # loop through both sources of files simultaneously
            # get edit dist and total_edit_dist across all files for this build
            for edited, original in zip(files, p['files']):
                ed = utils.edit_dist(original['body'], edited['body'])
                total_edit_dist += ed
                edited['edit_dist'] = ed
        else:
            logger.error('could not find problem: %s' % problem_key)

        self.process_error_hashes(errors, total_edit_dist)

        self.dict['actions'].append({
            'action': 'build',
            'timestamp': utils.timestamp(),
            'problem_id': problem_key,
            'total_edit_dist': total_edit_dist,
            'files': files,
            'errors': errors
        })

    def create_action_login(self):
        self.dict['actions'].append({
            'action': 'login',
            'timestamp': utils.timestamp()
            })

    def create_action_logout(self):
        self.dict['actions'].append({
            'action': 'logout',
            'timestamp': utils.timestamp()
            })

    def create_action_refresh_problems(self):
        self.dict['actions'].append({
            'action': 'refresh_problems',
            'timestamp': utils.timestamp()
            })

    def create_action_question(self, question):
        self.dict['actions'].append({
            'action': 'changed_question',
            'timestamp': utils.timestamp(),
            'to': question
        })

    def fpath(self):
        return '%s%s.json' % (STUDENTS_LOC, self.id)

    def load(self):
        with open(self.fpath(), 'r') as f:
            self.dict = json.load(f)

    def sync(self):
        with open(self.fpath(), 'w') as f:
            json.dump(self.dict, f)

    def create(self):
        '''create a new empty student file'''
        student = {
            'id': self.id,
            'created': utils.timestamp(),
            'actions': [],
            'hashes': []
            }

        with open(self.fpath(), 'w') as f:
            json.dump(student, f)
