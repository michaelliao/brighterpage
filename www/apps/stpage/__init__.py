#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
static page app.
'''

import re, time

from transwarp.web import view, get, post, ctx, notfound, seeother
from transwarp import db

from core.apis import api, check, theme, assert_not_empty, APIValueError
from core import texts

from models import Pages

def get_manage_menu():
    return 'Pages', 200

def get_navigation_menu():
    pages = _get_pages()
    return [(p.name, '/page/%s' % p.alias) for p in pages]

@get('/page/<alias>')
@theme('stpage/page.html')
def get_page(alias):
    page = Pages.select_one('where alias=?', alias)
    if page is None:
        raise notfound()
    page.content = texts.md2html(texts.get(page.content_id))
    return dict(page=page)

###############################################################################
# Page management
###############################################################################

_RE_ALIAS = re.compile(ur'^[0-9a-zA-Z\_\-]{1,50}$')

@api
@check()
@post('/api/pages/create')
def api_create_page():
    i = ctx.request.input(alias='', name='', tags='', draft='', content='')
    alias = assert_not_empty(i.alias, 'alias').lower()
    if _RE_ALIAS.match(alias) is None:
        raise APIValueError('alias', 'Invalid alias.')
    if Pages.select_one('where alias=?', alias):
        raise APIValueError('alias', 'Alias already exist.')
    name = assert_not_empty(i.name, 'name')
    content = assert_not_empty(i.content, 'content')
    draft = i.draft.lower()=='true'
    page_id = db.next_id()
    page = Pages( \
        _id = page_id, \
        alias = alias, \
        content_id = texts.set(page_id, content), \
        draft = draft, \
        name = name, \
        tags = texts.format_tags(i.tags) \
    ).insert()
    return dict(_id=page._id)

@api
@check()
@post('/api/pages/<pid>/update')
def api_update_page(pid):
    page = Pages.get_by_id(pid)
    if page is None:
        raise notfound()
    i = ctx.request.input()
    update = False
    if 'name' in i:
        page.name = assert_not_empty(i.name, 'name')
        update = True
    if 'tags' in i:
        page.tags = texts.format_tags(i.tags)
        update = True
    if 'draft' in i:
        draft = i.draft.lower()=='true'
        if draft != page.draft:
            page.draft = draft
            update = True
    if 'content' in i:
        content = assert_not_empty(i.content, 'content')
        page.content = content
        update = True

    if hasattr(page, 'content'):
        page.content_id = texts.set(page._id, page.content)
    if update:
        page.update()
    return dict(_id=page._id)

@api
@check()
@post('/api/pages/<pid>/delete')
def api_delete_page(pid):
    p = Pages.get_by_id(pid)
    if p is None:
        raise notfound()
    p.delete()
    return dict(result=True)

@view('templates/stpage/pages_list.html')
def index():
    return dict(pages=_get_pages())

@view('templates/stpage/page_form.html')
def create_page():
    return dict(form_title='Create New Page', form_action='/api/pages/create')

@view('templates/stpage/page_form.html')
def edit_page():
    page = Pages.get_by_id(ctx.request['_id'])
    if page is None:
        raise notfound()
    return dict( \
        form_title = 'Edit Page', \
        form_action = '/api/pages/%s/update' % page._id, \
        _id = page._id, \
        alias = page.alias, \
        name = page.name, \
        tags = page.tags, \
        draft = page.draft, \
        content = texts.get(page.content_id))

# private functions:

def _get_pages():
    return Pages.select('order by alias, name, creation_time desc')
