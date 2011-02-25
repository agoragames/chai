'''
Expectations that can set on a stub.
'''

class Expectation(object):
  '''
  Encapsulate an expectation.
  '''

  def __init__(self, obj, attr):
    self._met = False
    self._obj = obj
    self._attr = attr
  
  def args(self, *args, **kwargs):
    self._args = args
    self._kwargs = kwargs
    
    return self
  
  def returns(self, value):
    self._returns = value
  
    return self

  def is_met(self):
    '''
    Return whether this expectation has been met.
    '''
    # raise error if is set
    return self._met

  def call(self, *args, **kwargs):
    if not self._met:
      if self._args == args and self._kwargs == kwargs:
        self._met = true
    
    return self._met
