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
    self.validate_args = args
    self.validate_kwargs = kwargs

    if self.args == args and self.kwargs == kwargs:
      self._passed = True
    return self._passed

  def __str__(self):
    return "ArgumentsExpecationRule: passed: %s, args: %s, expected args: %s, kwargs: %s, expected kwargs: %s" % \
      (self.passed, self.args, self.validate_args, self.kwargs, self.validate_kwargs)

class AtLeastExpecationRule(ExpecationRule):
  def __init__(self, *args, **kwargs):
    pass
  
  def validate(self, *args, **kwargs):
    pass

  def __str__(self):
    pass

class AtMostExpecationRule(ExpecationRule):
  def __init__(self, *args, **kwargs):
    pass
  
  def validate(self, *args, **kwargs):
    pass

  def __str__(self):
    pass

class Expectation(object):
  '''
  Encapsulate an expectation.
  '''

  def __init__(self, stub):
    self._met = False
    self._stub = stub
    self._rule_set = []

  @property  
  def rules(self):
    return self._rule_set

  @property
  def is_met(self):
    '''
    Return whether this expectation has been met.
    '''
    return self._met

  def args(self, *args, **kwargs):
    """
    Creates a ArgumentsExpecationRule and adds it to the exception
    """
    self._rule_set.append(ArgumentsExpecationRule(*args, **kwargs))
    return self

  def returns(self, value):
    """
    What this expectation should return
    """
    self._returns = value
    return self

  def raises(self, exception):
    """
    Adds a raises to the expectation, this will be raised when the expectation is met.
    
    This can be either the exception class or instance of a exception
    """
    self._raises = exception

  def return_value(self):
    """
    Returns the value for this expectation or raises the proper exception.
    """
    if hasattr(self, '_raises'):
      if isinstance(type, type(self._raises)): # Check if it is a class.
        raise self._raises()
      else:
        raise self._raises
    else:
      return getattr(self, '_returns', None)
      
  def test(self, *args, **kwargs):
    """
    Validate all the rules with in this expectation to see if this expectation has been met.
    """
    if not self._met:
      for rule in self._rule_set:
        if rule.validate(*args, **kwargs): # What data do we need to be sure it has been met
          self._met = True
        else:
          self._met = False
    return self
