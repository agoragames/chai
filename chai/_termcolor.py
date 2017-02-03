'''
Copyright (c) 2011-2017, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''

try:
    from termcolor import colored
except ImportError:
    def colored(s, *args, **kargs):
        return s
