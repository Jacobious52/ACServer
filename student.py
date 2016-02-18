import json
import utils
import problem
from logger import logger

STUDENTS_LOC = 'db/students/'

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

    def create_action_build(self, problem_key, files, errors):
        total_edit_dist = 0

        p = problem.find(problem.PROBLEMS, problem_key)
        if p is not None:
            # loop through both sources of files and get edit dist
            for edited, original in zip(files, p['files']):
                ed = utils.edit_dist(original['body'], edited['body'])
                total_edit_dist += ed
                edited['edit_dist'] = ed
        else:
            logger.error('could not find problem: %s' % problem_key)

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
            'actions': []
            }

        with open(self.fpath(), 'w') as f:
            json.dump(student, f)
