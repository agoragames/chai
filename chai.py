'''
The chai test class.
'''

try:
  import unittest2
  unittest = unittest2
except ImportError:
  import unittest

class Chai(unittest.TestCase):
  '''
  Base class for all tests
  '''

  # mox uses a metaclass for wrapping setUp and tearDown, would be nice to
  # try and simplify if possible

  def setUp(self):
    super(Chai,self).setUp()

    # Setup stub tracking

  def tearDown(self):
    super(Chai,self).tearDown()

    # Docs insist that this will be called no matter what happens in runTest(),
    # so this should be a safe spot to unstub everything
