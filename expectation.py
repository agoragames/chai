'''
Expectations that can set on a stub.
'''

class Expectation(object):
  '''
  Encapsulate an expectation.
  '''

  def __init__(self):
    self._met = False

  def is_met(self):
    '''
    Return whether this expectation has been met.
    '''
    return self._met
