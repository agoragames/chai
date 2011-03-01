import re

'''
All of the comparators that can be used for arguments.
'''

def build_comparators(*values_or_types):
  comparators = []
  for item in values_or_types:
    if isinstance(item,Comparator):
      comparators.append( item )
    elif isinstance(item,type):
      # If you are passing around a type you will have to build a Equals comparator
      comparators.append( InstanceOf(item) )
    else:
      comparators.append( Equals(item) )
  return comparators

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
    self._comparators = build_comparators(*comparators)

  def test(self, value):
    for comp in self._comparators:
      if comp.test(value): return True
    return False
  
class In(Comparator):
  '''
  Test if a key is in a list or dict
  '''
  def __init__(self, hay_stack):
    self._hay_stack = hay_stack

  def test(self, needle):
    return needle in self._hay_stack

class Contains(Comparator):
  '''
  Test if a key is in a list or dict
  '''
  def __init__(self, needle):
    self._needle = needle

  def test(self, hay_stack):
    return self._needle in hay_stack

class All(Comparator):
  '''
  Test to see if all comparators match
  '''
  def __init__(self, *comparators):
    self._comparators = build_comparators(*comparators)

  def test(self, value):
    for comp in self._comparators:
      if not comp.test(value): return False
    return True

class Not(Comparator):
  '''
  Return the opposite of a comparator
  '''
  def __init__(self, *comparators):
    self._comparators = build_comparators(*comparators)

  def test(self, value):
    return all([not c.test(value) for c in self._comparators])

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
