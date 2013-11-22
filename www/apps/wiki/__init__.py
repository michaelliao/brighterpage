#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
wiki app.
'''

from transwarp.web import get, post, ctx, view, seeother, notfound, Dict
from transwarp import db

from core.apis import api, check, theme, assert_not_empty, APIValueError
from core import texts, comments

from models import Wikis, WikiPages

def get_manage_menu():
    return 'Wikis', 300

def get_navigation_menu():
    wikis = _get_wikis()
    return [(w.name, '/wiki/%s' % w._id) for w in wikis]

# web

@get('/wiki/<wid>')
@theme('wiki/wiki.html')
def web_wiki(wid):
    wiki = _get_wiki(wid)
    tree = _get_wikipages(wiki)
    content = texts.md2html(texts.get(wiki.content_id))
    return dict(wiki=wiki, page=None, tree=tree, name=wiki.name, content=content, comments=comments.get_comments(wid))

@get('/wiki/<wid>/<pid>')
@theme('wiki/wiki.html')
def web_wikipage(wid, pid):
    page = _get_full_wikipage(pid)
    if page.wiki_id != wid:
        raise notfound()
    wiki = _get_wiki(wid)
    tree = _get_wikipages(wiki)
    content = texts.md2html(texts.get(page.content_id))
    return dict(wiki=wiki, page=page, tree=tree, name=page.name, content=content, comments=comments.get_comments(pid))

# api

@api
@check()
@post('/api/wikis/create')
def api_create_wiki():
    ' create a new wiki. '
    i = ctx.request.input(name='', description='', content='')
    name = assert_not_empty(i.name, 'name')
    description = i.description.strip()
    content = assert_not_empty(i.content, 'content')
    wiki_id = db.next_str()
    wiki = Wikis( \
        _id=wiki_id, \
        name=name, \
        description=description, \
        content_id=texts.set(wiki_id, content)).insert()
    return wiki

@api
@get('/api/wikis/<wid>/pages')
def api_list_wiki_pages(wid):
    '''
    Get wiki pages as tree list, without content.
    '''
    wiki = _get_wiki(wid)
    return _get_wikipages(wiki)

@api
@get('/api/wikis/<wid>')
def api_get_wiki(wid):
    return _get_full_wiki(wid)

@api
@check()
@post('/api/wikis/<wid>/update')
def api_wikis_update(wid):
    ' update wiki name, description, content by id. '
    wiki = _get_wiki(wid)
    i = ctx.request.input()
    update = False
    if 'name' in i:
        wiki.name = assert_not_empty(i.name, 'name')
        update = True
    if 'description' in i:
        wiki.description = i.description.strip()
        update = True
    if 'content' in i:
        content = assert_not_empty(i.content, 'content')
        wiki.content_id = texts.set(wid, content)
        update = True
    if update:
        wiki.update()
    return dict(result=True)

@api
@check()
@post('/api/wikis/<wid>/delete')
def api_wikis_delete(wid):
    ' delete a wiki by id. '
    wiki = _get_wiki(wid)
    count = WikiPages.count('where wiki_id=?', wid)
    if count > 0:
        raise APIValueError('id', 'cannot delete non-empty wiki.')
    wiki.delete()
    comments.delete_comments(wid)
    return dict(result=True)

@api
@post('/api/wikis/<wid>/comments/create')
def api_create_wiki_comment(wid):
    u = ctx.user
    if u is None:
        raise APIPermissionError()
    i = ctx.request.input(content='')
    content = assert_not_empty(i.content, 'content')
    wiki = _get_wiki(wid)
    return comments.create_comment('wiki', wid, content)

@api
@get('/api/wikis/<wid>/pages')
def api_list_wiki_pages(wid):
    '''
    Get wiki pages as tree list, without content.
    '''
    if not wid:
        raise APIValueError('id', 'id cannot be empty.')
    wiki = _get_wiki(wid)
    return _get_wikipages(wiki)

@api
@get('/api/wikis/pages/<pid>')
def api_get_wiki_page(pid):
    return _get_full_wikipage(pid)

@api
@check()
@post('/api/wikis/<wid>/pages/create')
def api_create_wiki_page(wid):
    i = ctx.request.input(name='', content='')
    if not 'parent_id' in i:
        raise APIValueError('parent_id', 'bad parameter: parent_id')
    name = assert_not_empty(i.name, 'name')
    content = assert_not_empty(i.content, 'content')
    wiki = _get_wiki(wid)
    parent_id = i.parent_id.strip()
    if parent_id:
        p_page = _get_wikipage(parent_id, wiki._id)
    num = WikiPages.count('where wiki_id=? and parent_id=?', wiki._id, parent_id)
    return _create_wiki_page(wiki._id, parent_id, num, name, content)

@api
@check()
@post('/api/wikis/pages/<wpid>/update')
def api_update_wikipage(wpid):
    page = _get_wikipage(wpid)
    i = ctx.request.input()
    update = False
    if 'name' in i:
        page.name = assert_not_empty(i.name, 'name')
        update = True
    if 'content' in i:
        content = assert_not_empty(i.content, 'content')
        page.content_id = texts.set(wpid, content)
        update = True
    if update:
        page.update()
    return dict(result=True)

@api
@check()
@post('/api/wikis/pages/<wpid>/delete')
def api_wikis_pages_delete(wpid):
    page = _get_wikipage(wpid)
    if WikiPages.count('where wiki_id=? and parent_id=?', page.wiki_id, page._id) > 0:
        raise APIPermissionError('cannot delete non empty page.')
    page.delete()
    comments.delete_comments(wpid)
    return dict(result=True)

@api
@post('/api/wikis/pages/<wpid>/comments/create')
def api_create_wikipage_comment(wpid):
    u = ctx.user
    if u is None:
        raise APIPermissionError()
    i = ctx.request.input(content='')
    content = assert_not_empty(i.content, 'content')
    wikipage = _get_wikipage(wpid)
    return comments.create_comment('wikipage', wpid, content)

@api
@check()
@post('/api/wikis/pages/<wpid>/move/<target_id>')
def api_wikis_pages_move(wpid, target_id):
    '''
    Move wiki page from one node to another.
    '''
    if not wpid:
        raise APIValueError('id', 'bad parameter id.')
    if not target_id:
        raise APIValueError('target_id', 'bad parameter target_id.')
    i = ctx.request.input()
    if not 'index' in i:
        raise APIValueError('index', 'bad parameter index.')
    try:
        index = int(i.index)
    except ValueError:
        raise APIValueError('index', 'bad parameter index.')
    # get the 2 pages:
    moving_page = _get_wikipage(wpid)
    wiki = _get_wiki(moving_page.wiki_id)
    parent_page = None
    if target_id=='ROOT':
        parent_page = None # root node
    else:
        parent_page = _get_wikipage(target_id, wiki._id)
    # check to prevent recursive:
    pages = _get_wikipages(wiki, returnDict=True)
    if parent_page:
        p = parent_page
        while p.parent_id != '':
            if p.parent_id==moving_page._id:
                raise APIValueError('target_id', 'Will cause recursive.')
            p = pages[p.parent_id]
    # get current children:
    parent_id = parent_page._id if parent_page else ''
    L = [p for p in pages.itervalues() if p.parent_id==parent_id and p._id != moving_page._id]
    L.sort(cmp=lambda p1, p2: cmp(p1.display_order, p2.display_order))
    # insert at index N:
    L.insert(index, moving_page)
    # update display order:
    with db.transaction():
        n = 0
        for p in L:
            db.update('update wikipages set display_order=? where _id=?', n, p._id)
            n = n + 1
        db.update('update wikipages set parent_id=? where _id=?', parent_id, moving_page._id)
    return dict(result=True)

# management:

@view('templates/wiki/wiki_form.html')
def create_wiki():
    return dict(form_action='/api/wikis/create')

@view('templates/wiki/wikis_list.html')
def index():
    wikis = Wikis.select('order by name')
    return dict(wikis=wikis)

@view('templates/wiki/wikipages.html')
def edit_wiki():
    i = ctx.request.input()
    wiki = _get_wiki(i._id)
    return dict(wiki=wiki)

@view('templates/wiki/wikipage_form.html')
def edit_wiki_page():
    i = ctx.request.input(type='', _id='')
    if i.type=='wiki':
        wiki = _get_full_wiki(i._id)
        return dict( \
            name=wiki.name, \
            description=wiki.description, \
            has_description=True, \
            content=wiki.content, \
            wiki=wiki, \
            form_title='Edit Wiki Page', \
            form_action = '/api/wikis/%s/update' % wiki._id)
    elif i.type=='wikipage':
        wikipage = _get_full_wikipage(i._id)
        wiki = _get_wiki(wikipage.wiki_id)
        return dict( \
            name=wikipage.name, \
            content=wikipage.content, \
            has_description=False, \
            wiki=wiki, \
            form_title='Edit Wiki Page', \
            form_action = '/api/wikis/pages/%s/update' % wikipage._id)
    else:
        raise APIValueError('type', 'Invalid type.')

# private functions:

def _get_wikis():
    ' get all wikis of current website. '
    return Wikis.select('order by name, creation_time desc')

def _get_wiki(wid):
    ' get wiki by id. '
    wiki = Wikis.get_by_id(wid)
    if wiki is None:
        raise notfound()
    return wiki

def _get_full_wiki(wid):
    wiki = _get_wiki(wid)
    wiki.content = texts.get(wiki.content_id)
    return wiki

def _get_wikipage(wp_id, wiki_id=None):
    '''
    get a wiki page by id. If the wiki_id is not None, it check if the page belongs to wiki.
    '''
    wp = WikiPages.get_by_id(wp_id)
    if wp is None:
        raise notfound()
    if wiki_id and wp.wiki_id != wiki_id:
        raise APIValueError('wiki_id', 'bad wiki id.')
    return wp

def _get_full_wikipage(wp_id, wiki_id=None):
    wp = _get_wikipage(wp_id, wiki_id)
    wp.content = texts.get(wp.content_id)
    return wp

def _get_wikipages(wiki, returnDict=False):
    '''
    Get all wiki pages and return as tree. Each wiki page contains only id, wiki_id, parent_id, display_order, name and version.
    The return value is top-level list.
    '''
    pages = WikiPages.select('where wiki_id=?', wiki._id)
    pdict = dict(((p._id, p) for p in pages))
    if returnDict:
        return pdict
    proot = Dict(_id='')
    _tree_iter(pdict, proot)
    return proot.children

def _tree_iter(nodes, root):
    rid = root._id
    root.children = []
    for nid in nodes.keys():
        node = nodes[nid]
        if node.parent_id==rid:
            root.children.append(node)
            nodes.pop(nid)
    if root.children:
        root.children.sort(cmp=lambda n1, n2: -1 if n1.display_order < n2.display_order else 1)
        for ch in root.children:
            _tree_iter(nodes, ch)

def _create_wiki_page(wiki_id, parent_id, display_order, name, content):
    wp_id = db.next_str()
    content_id = texts.set(wp_id, content)
    return WikiPages( \
        _id=wp_id, \
        wiki_id=wiki_id, \
        parent_id=parent_id, \
        display_order=display_order, \
        name=name, \
        content_id=content_id).insert()

