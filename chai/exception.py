'''
Copyright (c) 2011-2017, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''
from __future__ import absolute_import

import sys
import traceback

from ._termcolor import colored

# Refactored from ArgumentsExpectationRule


def pretty_format_args(*args, **kwargs):
    """
    Take the args, and kwargs that are passed them and format in a
    prototype style.
    """
    args = list([repr(a) for a in args])
    for key, value in kwargs.items():
        args.append("%s=%s" % (key, repr(value)))
    return "(%s)" % ", ".join([a for a in args])


class ChaiException(RuntimeError):
    '''
    Base class for an actual error in chai.
    '''

class UnsupportedStub(ChaiException):
    '''
    Can't stub the requested object or attribute.
    '''

class UnsupportedModifier(ChaiException):
    '''
    Can't use the requested modifier.
    '''

class ChaiAssertion(AssertionError):
    '''
    Base class for all assertion errors.
    '''


class UnexpectedCall(BaseException):
    '''
    Raised when a unexpected call occurs to a stub.
    '''

    def __init__(self, msg=None, prefix=None, suffix=None, call=None,
                 args=None, kwargs=None, expected_args=None,
                 expected_kwargs=None):
        if msg:
            msg = colored('\n\n' + msg.strip(), 'red')
        else:
            msg = ''

        if prefix:
            msg = '\n\n' + prefix.strip() + msg

        if call:
            msg += colored('\n\nNo expectation in place for\n',
                           'white', attrs=['bold'])
            msg += colored(call, 'red')
            if args or kwargs:
                msg += colored(pretty_format_args(*(args or ()),
                                                  **(kwargs or {})), 'red')
            if expected_args or expected_kwargs:
                msg += colored('\n\nExpected\n', 'white', attrs=['bold'])
                msg += colored(call, 'red')
                msg += colored(pretty_format_args(
                               *(expected_args or ()),
                               **(expected_kwargs or {})), 'red')

        # If handling an exception, add printing of it here.
        if sys.exc_info()[0]:
            msg += colored('\n\nWhile handling\n', 'white', attrs=['bold'])
            msg += colored(''.join(
                           traceback.format_exception(*sys.exc_info())),
                           'red')

        if suffix:
            msg = msg + '\n\n' + suffix.strip()

        super(UnexpectedCall, self).__init__(msg)


class ExpectationNotSatisfied(ChaiAssertion):

    '''
    Raised when all expectations are not met
    '''

    def __init__(self, *expectations):
        self._expectations = expectations

    def __str__(self):
        return str("\n".join([str(e) for e in self._expectations]))
