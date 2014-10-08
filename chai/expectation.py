# -*- coding: utf-8 -*-
'''
Copyright (c) 2011-2013, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''

import inspect

from .comparators import *
from .exception import *
from ._termcolor import colored


class ExpectationRule(object):

    def __init__(self, *args, **kwargs):
        self._passed = False

    def validate(self, *args, **kwargs):
        raise NotImplementedError("Must be implemented by subclasses")


class ArgumentsExpectationRule(ExpectationRule):

    def __init__(self, *args, **kwargs):
        super(ArgumentsExpectationRule, self).__init__(*args, **kwargs)
        self.set_args(*args, **kwargs)

    def set_args(self, *args, **kwargs):
        self.args = []
        self.kwargs = {}

        # Convert all of the arguments to comparators
        self.args = build_comparators(*args)
        self.kwargs = dict([(k, build_comparators(v)[0])
                            for k, v in kwargs.items()])

    def validate(self, *args, **kwargs):
        self.in_args = args[:]
        self.in_kwargs = kwargs.copy()

        # First just check that the number of arguments is the same or
        # different
        if len(args) != len(self.args) or len(kwargs) != len(self.kwargs):
            self._passed = False
            return False

        for x in range(len(self.args)):
            if not self.args[x].test(args[x]):
                self._passed = False
                return False

        for arg_name, arg_test in self.kwargs.items():
            try:
                value = kwargs.pop(arg_name)
            except KeyError:
                self._passed = False
                return False
            if not arg_test.test(value):
                self._passed = False
                return False

        # If there are arguments left over, is error
        if len(kwargs):
            self._passed = False
            return False

        self._passed = True
        return self._passed

    @classmethod
    def pretty_format_args(self, *args, **kwargs):
        """
        Take the args, and kwargs that are passed them and format in a
        prototype style.
        """
        args = list([repr(a) for a in args])
        for key, value in kwargs.items():
            args.append("%s=%s" % (key, repr(value)))

        return "(%s)" % ", ".join([a for a in args])

    def __str__(self):
        if hasattr(self, 'in_args') and hasattr(self, 'in_kwargs'):
            return "\tExpected: %s\n\t\t    Used: %s" % \
                (self.pretty_format_args(*self.args, **self.kwargs),
                 self.pretty_format_args(*self.in_args, **self.in_kwargs))

        return "\tExpected: %s" % \
            (self.pretty_format_args(*self.args, **self.kwargs))


class Expectation(object):

    '''
    Encapsulate an expectation.
    '''

    def __init__(self, stub):
        self._met = False
        self._stub = stub
        self._arguments_rule = ArgumentsExpectationRule()
        self._raises = None
        self._returns = None
        self._max_count = None
        self._min_count = 1
        self._counts_defined = False
        self._run_count = 0
        self._any_order = False
        self._side_effect = False
        self._side_effect_args = None
        self._side_effect_kwargs = None
        self._teardown = False
        self._any_args = True

        # If the last expectation has no counts defined yet, set it to the
        # run count if it's already been used, else set it to 1 just like
        # the original implementation. This makes iterative testing much
        # simpler without needing to know ahead of time exactly how many
        # times an expectation will be called.
        prev_expect = None if not stub.expectations else stub.expectations[-1]
        if prev_expect and not prev_expect._counts_defined:
            if prev_expect._run_count:
                # Close immediately
                prev_expect._met = True
                prev_expect._max_count = prev_expect._run_count
            else:
                prev_expect._max_count = prev_expect._min_count

    # Support expectations as context managers. See
    #   https://github.com/agoragames/chai/issues/1
    def __enter__(self):
        return self._returns

    def __exit__(*args):
        pass

    def args(self, *args, **kwargs):
        """
        Creates a ArgumentsExpectationRule and adds it to the expectation
        """
        self._any_args = False
        self._arguments_rule.set_args(*args, **kwargs)
        return self

    def any_args(self):
        '''
        Accept any arguments passed to this call.
        '''
        self._any_args = True
        return self

    def returns(self, value):
        """
        What this expectation should return
        """
        self._returns = value
        return self

    def raises(self, exception):
        """
        Adds a raises to the expectation, this will be raised when the
        expectation is met.

        This can be either the exception class or instance of a exception.
        """
        self._raises = exception
        return self

    def times(self, count):
        self._min_count = self._max_count = count
        self._counts_defined = True
        return self

    def at_least(self, min_count):
        self._min_count = min_count
        self._max_count = None
        self._counts_defined = True
        return self

    def at_least_once(self):
        self.at_least(1)
        self._counts_defined = True
        return self

    def at_most(self, max_count):
        self._max_count = max_count
        self._counts_defined = True
        return self

    def at_most_once(self):
        self.at_most(1)
        self._counts_defined = True
        return self

    def once(self):
        self._min_count = 1
        self._max_count = 1
        self._counts_defined = True
        return self

    def any_order(self):
        self._any_order = True
        return self

    def is_any_order(self):
        return self._any_order

    def side_effect(self, func, *args, **kwargs):
        self._side_effect = func
        self._side_effect_args = args
        self._side_effect_kwargs = kwargs
        return self

    def teardown(self):
        self._teardown = True

        # If counts have not been defined yet, then there's an implied use case
        # here where once the expectation has been run, it should be torn down,
        # i.e. max_count is same as min_count, i.e. 1
        if not self._counts_defined:
            self._max_count = self._min_count
        return self

    def return_value(self):
        """
        Returns the value for this expectation or raises the proper exception.
        """
        if self._raises:
            # Handle exceptions
            if inspect.isclass(self._raises):
                raise self._raises()
            else:
                raise self._raises
        else:
            if isinstance(self._returns, tuple):
                return tuple([x.value if isinstance(x, Variable)
                             else x for x in self._returns])
            return self._returns.value if isinstance(self._returns, Variable) \
                else self._returns

    def close(self, *args, **kwargs):
        '''
        Mark this expectation as closed. It will no longer be used for matches.
        '''
        # If any_order, then this effectively is never closed. The
        # Stub.__call__ will just bypass it when it doesn't match. If there
        # is a strict count it will also be bypassed, but if there's just a
        # min set up, then it'll effectively stay open and catch any matching
        # call no matter the order.
        if not self._any_order:
            self._met = True

    def closed(self, with_counts=False):
        rval = self._met
        if with_counts:
            rval = rval or self.counts_met()
        return rval

    def counts_met(self):
        return self._run_count >= self._min_count and not (
            self._max_count and not self._max_count == self._run_count)

    def match(self, *args, **kwargs):
        """
        Check the if these args match this expectation.
        """
        return self._any_args or \
            self._arguments_rule.validate(*args, **kwargs)

    def test(self, *args, **kwargs):
        """
        Validate all the rules with in this expectation to see if this
        expectation has been met.
        """
        side_effect_return = None
        if not self._met:
            if self.match(*args, **kwargs):
                self._run_count += 1
                if self._max_count is not None and \
                        self._run_count == self._max_count:
                    self._met = True
                if self._side_effect:
                    if self._side_effect_args or self._side_effect_kwargs:
                        side_effect_return = self._side_effect(
                            *self._side_effect_args,
                            **self._side_effect_kwargs)
                    else:
                        side_effect_return = self._side_effect(*args, **kwargs)
            else:
                self._met = False

            # If this is met and we're supposed to tear down, must do it now
            # so that this stub is not called again
            if self._met and self._teardown:
                self._stub.teardown()

        # return_value has priority to not break existing uses of side effects
        rval = self.return_value()
        if rval is None:
          rval = side_effect_return
        return rval

    def __str__(self):
        runs_string = "     Ran: %s, Min Runs: %s, Max Runs: %s" % (
            self._run_count, self._min_count,
            "∞" if self._max_count is None else self._max_count)
        return_string = "  Raises: %s" % (
            self._raises if self._raises else " Returns: %s" % repr(
                self._returns))
        return "\n\t%s\n\t%s\n\t\t%s\n\t\t%s" % (
            colored("%s - %s" % (
                self._stub.name,
                "Passed" if self._arguments_rule._passed else "Failed"),
                "green" if self._arguments_rule._passed else "red"),
            self._arguments_rule, return_string, runs_string)
