#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
SNS API interface.
'''

import json, time, logging

import snspy
import conf

_cache = dict()

def create_client(provider, redirect_uri='', access_token='', expires=0.0):
    name = '%sMixin' % provider
    mixin = _cache.get(provider, None)
    if mixin is None:
        mixin = getattr(snspy, name)
        _cache[provider] = mixin
    c = conf.configs['oauth'][provider]
    return snspy.APIClient(mixin, c['app_id'], c['app_secret'], redirect_uri, access_token, expires)
