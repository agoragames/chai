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

class UnexpectedCall(ChaiAssertion):
  '''
  Raised when a unexpected call occurs to a stub.
  '''

class ExpectationNotSatisfied(ChaiAssertion):
  '''
  Raised when all expectations are not met
  '''
  
  def __init__(self, *expectations):
    self._expections = expectations
  
  def __str__(self):
    return str("\n".join([ str(e) for e in self._expections]))
