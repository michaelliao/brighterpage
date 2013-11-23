#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Generating SQL.
'''

import os, sys

from transwarp import db, utils

import conf_dev

def generate(mod):
    m = utils.load_module(mod)
    L = []
    for name in dir(m):
        c = getattr(m, name)
        if isinstance(c, db.ModelMetaclass):
            L.append(c().__sql__())
    return '\n\n'.join(L) + '\n\n'

if __name__=='__main__':
    sqlfile = os.path.abspath('../schema.sql')
    print('Generating SQL %s...' % sqlfile)
    mods = sys.argv[1:]
    if not mods:
        apps = ['article', 'stpage', 'wiki', 'user', 'navigation']
    	mods = ['apps.%s.models' % app for app in apps]
        mods.append('core.models')
    with open(sqlfile, 'w') as f:
        for mod in mods:
            print('Scanning %s...' % mod)
            f.write(generate(mod))
