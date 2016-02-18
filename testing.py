import error
import pprint
import logger
import problem
import utils
from student import Student

test_errors = [
    "main.cpp:4:7: error: expected ';' at end of declaration",
    "main.cpp:6:10: error: expected ';' after return statement",
    "main.cpp:7:1: error: expected '}'",
    "main.cpp:5:23: error: use of undeclared identifier 'i'",
    "main.cpp:3:4: error: unmatchable error"
]

def student(pp):
    s = Student('a1687803')
    pp.pprint(s.dict)

    s.create_action_build(problem.PROBLEMS[0]['name'], problem.PROBLEMS[0]['files'], test_errors)
    s.sync()

def problems(pp):
    pp.pprint(problem.load_all())
    pp.pprint(problem.load('question1'))

def errors(pp):
    errors = error.load_errors()
    for test in test_errors:
        pp.pprint('trying to match: %s' % test)
        for err in errors:
            e = err.make_match(test)
            if e is not None:
                pp.pprint('match found!')
                pp.pprint(e)

    print '\n'

def main():
    logger.level = 1
    pp = pprint.PrettyPrinter(indent=4)

    #student(pp)
    print utils.edit_dist('cat', 'cars')

if __name__ == '__main__':
    main()
