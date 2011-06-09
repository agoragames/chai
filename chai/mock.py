'''
An open mocking object.
'''
from types import MethodType
from stub import stub, Stub
from exception import UnexpectedCall


class Mock(object):
  '''
  A class where all calls are stubbed.
  '''

  def __init__(self, **kwargs):
    for name, value in kwargs.iteritems():
      setattr(self, name, value)

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
    
    # FIXME: this need to be formated.
    raise UnexpectedCall("on %s : %s : %s" % (self._name, args, kwargs))

  def __getattr__(self,name):
    rval = self.__dict__.get(name)

    if not rval or not isinstance(rval,(Stub,Mock)):
      rval = Mock()
      rval._name = name
      setattr(self, name, rval)

    return rval
