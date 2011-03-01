import re

'''
All of the comparators that can be used for arguments.
'''

class Comparator(object):
  '''
  Base class of all comparators, used for type testing
  '''

class Equals(Comparator):
  '''
  Simplest comparator.
  '''
  def __init__(self, value):
    self._value = value

  def test(self, value):
    return self._value == value


class InstanceOf(Comparator):
  '''
  Test to see if a value is an instance of something. Arguments match
  isinstance
  '''
  def __init__(self, types):
    self._types = types

  def test(self, value):
    return isinstance(value, self._types)

class Is(Comparator):
  '''
  Checks for identity not equality
  '''
  def __init__(self, obj):
    self._obj = obj
    
  def test(self, value):
    return self._obj is value

class AlmostEqual(Comparator):
  '''
  Compare a float value to n number of palces
  '''
  
  def __init__(self, float_value, places=7):
    self._float_value = float_value
    self._places = places
  
  def test(self, value):
    return round(value - self._float_value, self._places) == 0

class Contains(Comparator):
  '''
  Checks to see if an argument contains a value
  '''
  
  def __init__(self, obj):  
    self._obj = obj
  
  def test(self, value):
    return self._obj in value

class Regex(Comparator):
  '''
  Checks to see if a string matches a regex
  '''
  
  def __init__(self, pattern, flags=0):
    self._regex = re.compile(pattern)
  
  def test(self, value):
    return self._regex.search(value) is not None

class Any(Comparator):
  '''
  Test to see if any comparator matches
  '''
  def __init__(self, *comparators):
    self._comparators = []
    for comp in comparators:
      if isinstance(comp,Comparator):
        self._comparators.append( comp )
      elif isinstance(comp,type):
        self._comparators.append( InstanceOf(comp) )
      else:
        self._comparators.append( Equals(comp) )

  def test(self, value):
    for comp in self._comparators:
      if comp.test(value): return True
    return False
  
class In(Comparator):
  '''
  Test if a key is in a list or dict
  '''
  def __init__(self, key):
    self._key = key

  def test(self, value):
    return self._key in value

class All(Comparator):
  '''
  Test to see if all comparators match
  '''
  def __init__(self, *comparators):
    self._comparators = []
    for comp in comparators:
      if isinstance(comp,Comparator):
        self._comparators.append( comp )
      elif isinstance(comp,type):
        self._comparators.append( InstanceOf(comp) )
      else:
        self._comparators.append( Equals(comp) )

  def test(self, value):
    for comp in self._comparators:
      if not comp.test(value): return False
    return True

class Not(Comparator):
  '''
  Return the opposite of a comparator
  '''
  def __init__(self, comparator):
    self._comparator = comparator

  def test(self, value):
    return not self._comparator.test(value)

class Function(Comparator):
  '''
  Call a func to compare the values
  '''
  def __init__(self, func):
    self._func = func

  def test(self, value):
    return self._func(value)

class Ignore(Comparator):
  '''
  Igore this argument
  '''
  def test(self, value):
    return True
