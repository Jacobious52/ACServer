import json
import utils

STUDENTS_LOC = 'db/students/'

class Student:
    '''class to manipulate a student model'''
    def __init__(self, id):
        self.id = id
        self.dict = {}

        # if not created, creat new one
        if not utils.fexists(self.fpath()):
            self.create()

        # load the previous or newly created
        self.load()

    def fpath(self):
        return '%s%s.json' % (STUDENTS_LOC, self.id)

    def load(self):
        with open(self.fpath(), 'r') as f:
            self.dict = json.load(f)

    def sync(self):
        pass

    def create(self):
        '''create a new empty student file'''
        student = {
            'id': self.id,
            'created': utils.timestamp(),
            'actions': []
            }

        with open(self.fpath(), 'w') as f:
            json.dump(student, f)
