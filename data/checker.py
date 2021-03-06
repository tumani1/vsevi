'''
Class for fact cheking and information fixing
'''
class FactChecker(object):

    def __init__(self, target_type):

        self.target_type = target_type
        self.checkers = {}
        self.correctors = {}

    def add(self, message, corrector = None):
        '''
        Instance method can be used as 

        
        '''

        def wrapper(func):
            self.checkers[message] = func
            if not corrector is None:
                self.correctors[message] = corrector
        return wrapper

    def check(self, target):
        if not (type(target) is self.target_type):
            raise NameError("Wrong type of data. Expected {}, got {}".format(self.target_type, type(target)))
        else:
            failures = [name for name in self.checkers if not self.checkers[name](target)]
            return failures

    def check_and_correct(self, target):
        is_target_changed = True
        while is_target_changed:
            is_target_changed = False
            failures = self.check(target)
            for failure in failures:
                if failure in self.correctors:
                    self.correctors[failure](target)
        return failures


