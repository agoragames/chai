# -*- coding: utf-8 -*-
'''
Copyright (c) 2011-2013, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''

from .exception import UnsupportedModifier
from .expectation import Expectation

class Spy(Expectation):

    def __init__(self, *args, **kwargs):
        super(Spy,self).__init__(*args, **kwargs)
        self._side_effect = self._stub.call_orig

    def side_effect(self, *args, **kwargs):
        '''
        Disable side effects for spies.
        '''
        raise UnsupportedModifier("Can't use side effects on spies")

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
