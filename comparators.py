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

