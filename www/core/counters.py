#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' counters module '

import logging

from transwarp import cache

_COUNTER_KEY = '__@%s'

def incr(key):
    '''
    Increase counter.

    >>> key = uuid.uuid4().hex
    >>> inc(key)
    1
    '''
    return cache.client.incr(_COUNTER_KEY % key)

def count(key):
    return cache.client.getint(_COUNTER_KEY % key)

def counts(keys):
    return cache.client.getints(*map(lambda key: _COUNTER_KEY % key, keys))

if __name__=='__main__':
    import uuid, doctest
    doctest.testmod()
