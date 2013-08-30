'''
Copyright (c) 2011-2013, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''
from types import MethodType
from .stub import Stub
from .exception import UnexpectedCall
from .expectation import ArgumentsExpectationRule

class Mock(object):
  '''
  A class where all calls are stubbed.
  '''

  def __init__(self, **kwargs):
    for name, value in kwargs.items():
      setattr(self, name, value)
    self._name = 'mock'

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
    
    raise UnexpectedCall(call=self._name, args=args, kwargs=kwargs)

  def __getattr__(self,name):
    rval = self.__dict__.get(name)

    if not rval or not isinstance(rval,(Stub,Mock)):
      rval = Mock()
      rval._name = '%s.%s'%(self._name,name)
      setattr(self, name, rval)

    return rval

  ###
  ### Define nonzero so that basic "if <mock>:" stanzas will work.
  ###
  def __nonzero__(self):
    if isinstance(getattr(self,'__nonzero__'), Stub):
      return getattr(self,'__nonzero__')()
    return True

  ###
  ### Emulate container types, the 99% of cases where we want to mock the
  ### special methods. They all raise UnexpectedCall unless they're mocked out
  ### http://docs.python.org/reference/datamodel.html#emulating-container-types
  ###
  # HACK: it would be nice to abstract this lookup-stub behavior in a decorator
  # but that gets in the way of stubbing. Would like to figure that out @AW
  def __len__(self):
    if isinstance(getattr(self,'__len__'), Stub):
      return getattr(self,'__len__')()
    raise UnexpectedCall(call=self._name+'.__len__')
    
  def __getitem__(self, key):
    if isinstance(getattr(self,'__getitem__'), Stub):
      return getattr(self,'__getitem__')(key)
    raise UnexpectedCall(call=self._name+'.__getitem__', args=(key,))

  def __setitem__(self, key, value):
    if isinstance(getattr(self,'__setitem__'), Stub):
      return getattr(self,'__setitem__')(key, value)
    raise UnexpectedCall(call=self._name+'.__setitem__', args=(key,value))

  def __delitem__(self, key):
    if isinstance(getattr(self,'__delitem__'), Stub):
      return getattr(self,'__delitem__')(key)
    raise UnexpectedCall(call=self._name+'.__delitem__', args=(key,))

  def __iter__(self):
    if isinstance(getattr(self,'__iter__'), Stub):
      return getattr(self,'__iter__')()
    raise UnexpectedCall(call=self._name+'.__iter__')

  def __reversed__(self):
    if isinstance(getattr(self,'__reversed__'), Stub):
      return getattr(self,'__reversed__')()
    raise UnexpectedCall(call=self._name+'.__reversed__')

  def __contains__(self, item):
    if isinstance(getattr(self,'__contains__'), Stub):
      return getattr(self,'__contains__')(item)
    raise UnexpectedCall(call=self._name+'.__contains__', args=(item,))

  ###
  ### Emulate context managers
  ### http://docs.python.org/reference/datamodel.html#with-statement-context-managers
  ###
  def __enter__(self):
    if isinstance(getattr(self,'__enter__'), Stub):
      return getattr(self,'__enter__')()
    raise UnexpectedCall(call=self._name+'.__enter__')
  
  def __exit__(self, exc_type, exc_value, traceback):
    if isinstance(getattr(self,'__exit__'), Stub):
      return getattr(self,'__exit__')(exc_type, exc_value, traceback)
    raise UnexpectedCall(call=self._name+'.__exit__', args=(exc_type,exc_value,traceback))
