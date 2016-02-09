import error
import pprint
import logger
import problem

test_errors = [
    "main.cpp:4:7: error: expected ';' at end of declaration",
    "main.cpp:6:10: error: expected ';' after return statement",
    "main.cpp:7:1: error: expected '}'",
    "main.cpp:5:23: error: use of undeclared identifier 'i'",
    "main.cpp:3:4: error: unmatchable error"
]

def main():
    logger.level = 1

    errors = error.load_errors()
    pp = pprint.PrettyPrinter(indent=4)
    '''
    for test in test_errors:
        pp.pprint('trying to match: %s' % test)
        for err in errors:
            e = err.make_match(test)
            if e is not None:
                pp.pprint('match found!')
                pp.pprint(e)

    print '\n'
    '''

    pp.pprint(problem.load_all())

if __name__ == '__main__':
    main()
