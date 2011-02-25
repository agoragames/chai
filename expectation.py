'''
Expectations that can set on a stub.
'''

class ExpecationRule(object):
  def __init__(self, *args, **kwargs):
    self._passed = False

  def validate(self, *args, **kwargs):
    raise NotImplementedError("Must be implmeneted by subclasses")
  
  @property
  def passed(self):
    return self._passed

class ArgumentsExpecationRule(ExpecationRule):
  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs
  
  def validate(self, *args, **kwargs):
    if self.args == args and self.kwargs == kwargs:
      self._passed = False
    
    return self._passed

class Expectation(object):
  '''
  Encapsulate an expectation.
  '''

  def __init__(self, stub):
    self._met = False
    self._stub = stub
    self._rule_set = []
  
  def args(self, *args, **kwargs):
    self._rule_set.append(ArgumentsExpecationRule(*args, **kwargs))
    return self
  
  def returns(self, value):
    self._returns = value
  
    return self
  
  @property  
  def rules(self):
    return self._rule_set

  @property
  def return_value(self):
    return self._returns

  @property
  def is_met(self):
    '''
    Return whether this expectation has been met.
    '''
    # raise error if is set
    return self._met
  

  def call(self, *args, **kwargs):
    if not self._met:
      for rule in self._rule_set:
        if rule.validate(*args, **kwargs): # What data do we need to be sure it has been met
          self._met = True
    return self
    

