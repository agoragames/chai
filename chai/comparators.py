'''
Copyright (c) 2011-2017, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''
import re


def build_comparators(*values_or_types):
    '''
    All of the comparators that can be used for arguments.
    '''
    comparators = []
    for item in values_or_types:
        if isinstance(item, Comparator):
            comparators.append(item)
        elif isinstance(item, type):
            # If you are passing around a type you will have to build a Equals
            # comparator
            comparators.append(Any(IsA(item), Is(item)))
        else:
            comparators.append(Equals(item))
    return comparators


class Comparator(object):

    '''
    Base class of all comparators, used for type testing
    '''

    def __eq__(self, value):
        return self.test(value)


class Equals(Comparator):

    '''
    Simplest comparator.
    '''

    def __init__(self, value):
        self._value = value

    def test(self, value):
        return self._value == value

    def __repr__(self):
        return repr(self._value)
    __str__ = __repr__


class Length(Comparator):

    '''
    Compare the length of the argument.
    '''

    def __init__(self, value):
        self._value = value

    def test(self, value):
        if isinstance(self._value, int):
            return len(value) == self._value
        return len(value) in self._value

    def __repr__(self):
        return repr(self._value)
    __str__ = __repr__


class IsA(Comparator):

    '''
    Test to see if a value is an instance of something. Arguments match
    isinstance
    '''

    def __init__(self, types):
        self._types = types

    def test(self, value):
        return isinstance(value, self._types)

    def _format_name(self):
        if isinstance(self._types, type):
            return self._types.__name__
        else:
            return str([o.__name__ for o in self._types])

    def __repr__(self):
        return "IsA(%s)" % (self._format_name())
    __str__ = __repr__


class Is(Comparator):

    '''
    Checks for identity not equality
    '''

    def __init__(self, obj):
        self._obj = obj

    def test(self, value):
        return self._obj is value

    def __repr__(self):
        return "Is(%s)" % (str(self._obj))
    __str__ = __repr__


class AlmostEqual(Comparator):

    '''
    Compare a float value to n number of palces
    '''

    def __init__(self, float_value, places=7):
        self._float_value = float_value
        self._places = places

    def test(self, value):
        return round(value - self._float_value, self._places) == 0

    def __repr__(self):
        return "AlmostEqual(value: %s, places: %d)" % (
            str(self._float_value), self._places)
    __str__ = __repr__


class Regex(Comparator):

    '''
    Checks to see if a string matches a regex
    '''

    def __init__(self, pattern, flags=0):
        self._pattern = pattern
        self._flags = flags
        self._regex = re.compile(pattern)

    def test(self, value):
        return self._regex.search(value) is not None

    def __repr__(self):
        return "Regex(pattern: %s, flags: %s)" % (self._pattern, self._flags)
    __str__ = __repr__


class Any(Comparator):

    '''
    Test to see if any comparator matches
    '''

    def __init__(self, *comparators):
        self._comparators = build_comparators(*comparators)

    def test(self, value):
        for comp in self._comparators:
            if comp.test(value):
                return True
        return False

    def __repr__(self):
        return "Any(%s)" % str(self._comparators)
    __str__ = __repr__


class In(Comparator):

    '''
    Test if a key is in a list or dict
    '''

    def __init__(self, hay_stack):
        self._hay_stack = hay_stack

    def test(self, needle):
        return needle in self._hay_stack

    def __repr__(self):
        return "In(%s)" % (str(self._hay_stack))
    __str__ = __repr__


class Contains(Comparator):

    '''
    Test if a key is in a list or dict
    '''

    def __init__(self, needle):
        self._needle = needle

    def test(self, hay_stack):
        return self._needle in hay_stack

    def __repr__(self):
        return "Contains('%s')" % (str(self._needle))
    __str__ = __repr__


class All(Comparator):

    '''
    Test to see if all comparators match
    '''

    def __init__(self, *comparators):
        self._comparators = build_comparators(*comparators)

    def test(self, value):
        for comp in self._comparators:
            if not comp.test(value):
                return False
        return True

    def __repr__(self):
        return "All(%s)" % (self._comparators)
    __str__ = __repr__


class Not(Comparator):

    '''
    Return the opposite of a comparator
    '''

    def __init__(self, *comparators):
        self._comparators = build_comparators(*comparators)

    def test(self, value):
        return all([not c.test(value) for c in self._comparators])

    def __repr__(self):
        return "Not(%s)" % (repr(self._comparators))
    __str__ = __repr__


class Function(Comparator):

    '''
    Call a func to compare the values
    '''

    def __init__(self, func):
        self._func = func

    def test(self, value):
        return self._func(value)

    def __repr__(self):
        return "Function(%s)" % (str(self._func))
    __str__ = __repr__


class Ignore(Comparator):

    '''
    Igore this argument
    '''

    def test(self, value):
        return True

    def __repr__(self):
        return "Ignore()"
    __str__ = __repr__


class Variable(Comparator):

    '''
    A mechanism for tracking variables and their values.
    '''
    _cache = {}

    @classmethod
    def clear(self):
        '''
        Delete all cached values. Should only be used by the test suite.
        '''
        self._cache.clear()

    def __init__(self, name):
        self._name = name

    @property
    def value(self):
        try:
            return self._cache[self._name]
        except KeyError:
            raise ValueError("no value '%s'" % (self._name))

    def test(self, value):
        try:
            return self._cache[self._name] == value
        except KeyError:
            self._cache[self._name] = value
        return True

    def __repr__(self):
        return "Variable('%s')" % (self._name)
    __str__ = __repr__


class Like(Comparator):

    '''
    A comparator that will assert that fields of a container look like
    another.
    '''

    def __init__(self, src):
        # This might have to change to support more iterable types
        if not isinstance(src, (dict, set, list, tuple)):
            raise ValueError(
                "Like comparator only implemented for basic container types")
        self._src = src

    def test(self, value):
        # This might need to change so that the ctor arg can be a list, but
        # any iterable type can be tested.
        if not isinstance(value, type(self._src)):
            return False

        rval = True
        if isinstance(self._src, dict):
            for k, v in self._src.items():
                rval = rval and value.get(k) == v

        else:
            for item in self._src:
                rval = rval and item in value

        return rval

    def __repr__(self):
        return "Like(%s)" % (str(self._src))
    __str__ = __repr__
