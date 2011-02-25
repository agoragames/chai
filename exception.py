'''
Exceptions for Chai
'''

class ChaiException(RuntimeError):
  '''
  Base class for an actual error in chai.
  '''

class UnsupportedStub(ChaiException):
  '''
  Can't stub the requested object or attribute.
  '''



class ChaiAssertion(AssertionError):
  '''
  Base class for all assertion errors.
  '''
