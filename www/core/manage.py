#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

import os

from transwarp.web import get, post, route, ctx, notfound, seeother, Template
from transwarp import utils

@get('/manage/')
def manage_index():
    raise seeother('/manage/%s/' % _apps_list[0][0])

@get('/manage/<app>/')
def manage_app_index(app):
    return _manage(app, 'index')

@get('/manage/<app>/<func>')
def manage_app_func(app, func):
    return _manage(app, func)

def _manage(app, func):
    if ctx.user is None:
        raise seeother('/auth/signin')
    mod = _apps.get(app, None)
    if mod is None:
        raise notfound()
    fn = getattr(mod, func, None)
    if fn is None:
        raise notfound()
    r = fn()
    if isinstance(r, Template):
        r.model['__user__'] = ctx.user
        r.model['__apps__'] = _apps_list
        return r

def _get_apps():
    apps = dict()
    apps_list = []
    for the_name, the_mod in _scan_submodules('apps').iteritems():
        if hasattr(the_mod, 'get_manage_menu'):
            apps[the_name] = the_mod
            menu_name, menu_order = the_mod.get_manage_menu()
            apps_list.append((the_name, menu_name, menu_order))
    apps_list.sort(cmp=lambda x,y: cmp(x[2], y[2]))
    return apps, [(m[0], m[1]) for m in apps_list]

def _scan_submodules(module_name):
    '''
    Scan sub modules and import as dict (key=module name, value=module).

    >>> ms = scan_submodules('apps')
    >>> type(ms['article'])
    <type 'module'>
    >>> ms['article'].__name__
    'apps.article'
    >>> type(ms['wiki'])
    <type 'module'>
    >>> ms['wiki'].__name__
    'apps.wiki'
    '''
    web_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mod_path = os.path.join(web_root, *module_name.split('.'))
    if not os.path.isdir(mod_path):
        raise IOError('No such file or directory: %s' % mod_path)
    dirs = os.listdir(mod_path)
    mod_dict = {}
    for name in dirs:
        if name=='__init__.py':
            continue
        p = os.path.join(mod_path, name)
        if os.path.isfile(p) and name.endswith('.py'):
            pyname = name[:-3]
            mod_dict[pyname] = __import__('%s.%s' % (module_name, pyname), globals(), locals(), [pyname])
        if os.path.isdir(p) and os.path.isfile(os.path.join(mod_path, name, '__init__.py')):
            mod_dict[name] = __import__('%s.%s' % (module_name, name), globals(), locals(), [name])
    return mod_dict

_apps, _apps_list = _get_apps()

def get_apps_list():
    return _apps.values()
