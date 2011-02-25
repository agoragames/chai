import inspect
'''
Expectations that can set on a stub.
'''

class ExpectationRule(object):
  def __init__(self, *args, **kwargs):
    self._passed = False

  def validate(self, *args, **kwargs):
    raise NotImplementedError("Must be implmeneted by subclasses")
  
class ArgumentsExpectationRule(ExpectationRule):
  def __init__(self, *args, **kwargs):
    super(ArgumentsExpectationRule, self).__init__(*args, **kwargs)
    self.args = args
    self.kwargs = kwargs
  
  def set_args(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs
  
  def validate(self, *args, **kwargs):
    self.in_args = args
    self.in_kwargs = kwargs

    if self.args == args and self.kwargs == kwargs:
      self._passed = True
    else:
      self._passed = False
    return self._passed

  def __str__(self):
    if hasattr(self, 'in_args') and hasattr(self, 'in_kwargs'):
      return "ArgumentsExpectationRule: passed: %s, args: %s, expected args: %s, kwargs: %s, expected kwargs: %s" % \
        (self._passed, self.args, self.in_args, self.kwargs, self.in_kwargs)
        
    return "ArgumentsExpectationRule: passed: %s, args: %s, kwargs: %s, " % \
      (self._passed, self.args, self.kwargs)

class Expectation(object):
  '''
  Encapsulate an expectation.
  '''

  def __init__(self, stub):
    self._met = False
    self._stub = stub
    self._arguments_rule = ArgumentsExpectationRule()
    self._raises = None
    self._returns = None
    self._max_count = self._min_count = 1
    self._run_count = 0 
    
  def args(self, *args, **kwargs):
    """
    Creates a ArgumentsExpectationRule and adds it to the expectation
    """
    self._arguments_rule.set_args(*args, **kwargs)
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
  
  def at_least(self, min_count):
    self._min_count = min_count
    self._max_count = None
  
  def at_least_once(self):
    self.at_least(1)
  
  def at_most(self, max_count):
    self._max_count = max_count
    return self
  
  def at_most_once(self):
    self.at_most(1)
    return self
  
  def once(self):
    self._min_count = 1
    self._max_count = 1
  
  def return_value(self):
    """
    Returns the value for this expectation or raises the proper exception.
    """
    if self._raises:
      # Handle exceptions
      if inspect.isclass(self._raises):
        raise self._raises()
      else:
        raise self._raises
    else:
      return self._returns

  def close(self, *args, **kwargs):
    self._met = True
    
  def closed(self, with_counts=False):
    rval = self._met
    if with_counts:
      rval = rval or self._run_count >= self._min_count and not (self._max_count and not self._max_count == self._run_count)
    return rval
  
  def match(self, *args, **kwargs):
    """
    Check the if these args match this expectation.
    """
    return self._arguments_rule.validate(*args, **kwargs)

  def test(self, *args, **kwargs):
    """
    Validate all the rules with in this expectation to see if this expectation has been met.
    """
    if not self._met:
      self._run_count += 1
      if self._arguments_rule.validate(*args, **kwargs): # What data do we need to be sure it has been met
        if not self._max_count == None and self._run_count == self._max_count:
          self._met = True
      else:
        self._met = False

    return self.return_value()
  
  def __str__(self):
    runs_string = "Ran: %s, expect_min: %s, expect_max: %s" % (self._run_count, self._min_count, self._max_count)
    return_string = "Raises: %s" % self._raises if self._raises else "Returns: %s" % self._returns
    return "\n\t%s\n\t%s\n\t%s" % (self._arguments_rule, return_string, runs_string)
