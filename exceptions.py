'''
Exceptions for Chai
'''

class ChaiException(RuntimeError):
  '''
  Base class for an actual error in chai.
  '''

class ChaiAssertion(AssertionError):
  '''
  Base class for all assertion errors.
  '''
