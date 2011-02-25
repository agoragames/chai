'''
An open mocking object.
'''
from types import MethodType
from stub import stub

class Mock(object):
  '''
  A class where all calls are stubbed.
  '''
  def __getattr__(self,name):
    rval = self.__dict__.get(name)

    if not rval:
      def noop(*args, **kwargs): pass
      noop.func_name = name

      setattr(self, name, MethodType(noop, self, Mock) ) 
      rval = stub( self, name )

    return rval
