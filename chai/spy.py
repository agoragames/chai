# -*- coding: utf-8 -*-
'''
Copyright (c) 2011-2013, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''

from .exception import UnsupportedModifier
from .expectation import Expectation


class Spy(Expectation):

    def __init__(self, *args, **kwargs):
        super(Spy, self).__init__(*args, **kwargs)
        self._side_effect = self._call_spy

        # To support side effects within spies
        self._spy_side_effect = False
        self._spy_side_effect_args = None
        self._spy_side_effect_kwargs = None
        self._spy_return = False

    def _call_spy(self, *args, **kwargs):
      '''
      Wrapper to call the spied-on function. Operates similar to
      Expectation.test.
      '''
      if self._spy_side_effect:
          if self._spy_side_effect_args or self._spy_side_effect_kwargs:
              self._spy_side_effect(
                  *self._spy_side_effect_args,
                  **self._spy_side_effect_kwargs)
          else:
              self._spy_side_effect(*args, **kwargs)

      return_value = self._stub.call_orig(*args, **kwargs)
      if self._spy_return:
          self._spy_return(return_value)

      return return_value

    def side_effect(self, func, *args, **kwargs):
        '''
        Wrap side effects for spies.
        '''
        self._spy_side_effect = func
        self._spy_side_effect_args = args
        self._spy_side_effect_kwargs = kwargs
        return self

    def spy_return(self, func):
        '''
        Allow spies to react to return values.
        '''
        self._spy_return = func
        return self

    def returns(self, *args):
        '''
        Disable returns for spies.
        '''
        raise UnsupportedModifier("Can't use returns on spies")

    def raises(self, *args):
        '''
        Disable raises for spies.
        '''
        raise UnsupportedModifier("Can't use raises on spies")
