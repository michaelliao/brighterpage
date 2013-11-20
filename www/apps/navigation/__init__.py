#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
navigation app.
'''

from collections import namedtuple

from transwarp.web import view, get, post, ctx, notfound, seeother
from transwarp import db

from core.apis import api, check, assert_not_empty, template

from core.models import Navigations

def get_manage_menu():
    return 'Navigations', 1100

# api:

@api
@check()
@post('/api/navigations/sort')
def api_sort_navigations():
    '''
    Sort navigations.
    '''
    ids = ctx.request.gets('_id')
    navs = _get_navigations()
    l = len(navs)
    if l != len(ids):
        raise APIValueError('_id', 'bad id list.')
    sets = set([n._id for n in navs])
    odict = dict()
    n = 0
    for o in ids:
        if not o in sets:
            raise APIValueError('_id', 'some id was invalid.')
        odict[o] = n
        n = n + 1
    with db.transaction():
        for n in navs:
            db.update('update navigations set display_order=?, version=version+1 where _id=?', odict.get(n._id, l), n._id)
    _clear_navigations_cache()
    return dict(result=True)

@api
@check()
@post('/api/navigations/create')
def api_create_navigation():
    i = ctx.request.input(name='', url='')
    name = assert_not_empty(i.name, 'name')
    url = assert_not_empty(i.url, 'url')
    max_display = db.select_one('select max(display_order) as max from navigations').max
    nav = Navigations(_id=db.next_id(), name=name, url=url, display_order=max_display+1).insert()
    _clear_navigations_cache()
    return nav

@api
@check()
@post('/api/navigations/<nid>/update')
def api_update_navigation(nid):
    nav = Navigations.get_by_id(nid)
    if nav is None:
        raise notfound()
    i = ctx.request.input(name='', url='')
    nav.name = assert_not_empty(i.name, 'name')
    nav.url = assert_not_empty(i.url, 'url')
    nav.update()
    _clear_navigations_cache()
    return dict(result=True)

@api
@check()
@post('/api/navigations/<nid>/delete')
def api_delete_navigation(nid):
    if not nid:
        raise notfound()
    nav = Navigations.get_by_id(nid)
    if nav is None:
        raise notfound()
    nav.delete()
    _clear_navigations_cache()
    return dict(result=True)

# management:

@view('templates/navigation/navigations_list.html')
def index():
    return dict(navigations=_get_navigations())

Menu = namedtuple('Menu', ['name', 'url'])

_menus = None

@view('templates/navigation/navigation_form.html')
def create_navigation():
    return dict(menus=_get_menus(), name='', url='', form_action='/api/navigations/create', form_title='Create New Navigation')

@view('templates/navigation/navigation_form.html')
def edit_navigation():
    _id = ctx.request['_id']
    nav = Navigations.get_by_id(_id)
    if nav is None:
        raise notfound()
    return dict(menus=_get_menus(), name=nav.name, url=nav.url, form_action='/api/navigations/%s/update' % nav._id, form_title='Edit Navigation')

# private functions:

def _get_menus():
    global _menus
    if _menus is None:
        from core import manage
        apps = manage.get_apps_list()
        menus = []
        for app in apps:
            if hasattr(app, 'get_navigation_menu'):
                menus.extend([Menu(m[0], m[1]) for m in app.get_navigation_menu()])
        menus.sort(lambda m1, m2: cmp(m1[0], m2[0]))
        menus.append(Menu('Custom', 'http://'))
        _menus = menus
    return _menus

def _clear_navigations_cache():
    pass

def _get_navigations():
    return Navigations.select('order by display_order, name')
