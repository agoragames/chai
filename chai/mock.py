'''
An open mocking object.
'''
from types import MethodType
from stub import stub, Stub


class Mock(object):
  '''
  A class where all calls are stubbed.
  '''
  # For whatever reason, new-style objects require this method defined before
  # any instance is created. Defining it through __getattr__ is not enough. This
  # appears to be a bug/feature in new classes where special members, or at least
  # __call__, have to defined when the instance is created. Also, if it's already
  # defined on the instance, getattr() will return the stub but the original
  # method will always be called. Anyway, it's all crazy, but that's why the 
  # implementation of __call__ is so weird.
  def __call__(self, *args, **kwargs):
    if isinstance(getattr(self,'__call__'), Stub):
      return getattr(self,'__call__')(*args, **kwargs)

  def __getattr__(self,name):
    rval = self.__dict__.get(name)

    if not rval or not isinstance(rval,Stub):
      def noop(*args, **kwargs): pass
      noop.func_name = name

      rval = MethodType(noop, self, Mock)
      setattr(self, name, rval)

    return rval
