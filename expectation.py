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
    # raise error if is set
    return self._met

  def call():
    if not self._met:
      # check conditions
      # if not met, set error
      pass
