#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
article app.
'''

import time

from transwarp.web import view, get, post, ctx, notfound, seeother
from transwarp import db

from core.apis import api, theme, check, page_select, assert_not_empty, time2timestamp, APIValueError
from core import uploaders, texts, comments, counters

from models import Articles, Categories

def get_manage_menu():
    return 'Articles', 100

def get_navigation_menu():
    cats = _get_categories()
    return [(c.name, '/category/%s' % c._id) for c in cats]

@get('/')
@theme('index.html')
def homepage():
    categories = _get_categories()
    cat_dict = dict(((c._id, c.name) for c in categories))
    fn_get_category_name = lambda cid: cat_dict.get(cid, u'ERROR')
    articles = Articles.select('where publish_time<? order by publish_time desc limit ?', time.time(), 10)
    reads = counters.counts((a._id for a in articles))
    for a, r in zip(articles, reads):
        a.reads = r
    return dict(articles=articles, fn_get_category_name=fn_get_category_name)

@get('/feed')
def rss():
    ctx.response.content_type = 'application/rss+xml'
    return _get_rss()

def _get_rss():

    def _rss_datetime(ts):
        dt = datetime.fromtimestamp(ts, UTC_0)
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

    def _safe_str(s):
        if isinstance(s, str):
            return s
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return str(s)

    limit = 20
    name = u'廖雪峰的官方网站'
    description = u''
    copyright = 'copyright 2013'
    domain = ctx.request.host
    articles = _get_recent_articles(20)
    rss_time = articles and articles[0].publish_time or time.time()
    L = [
        '<?xml version="1.0"?>\n<rss version="2.0"><channel><title><![CDATA[',
        name,
        ']]></title><link>http://',
        domain,
        '/</link><description><![CDATA[',
        description,
        ']]></description><lastBuildDate>',
        _rss_datetime(rss_time),
        '</lastBuildDate><generator>BrighterPage</generator><ttl>600</ttl>'
    ]
    for a in articles:
        url = 'http://%s/article/%s' % (domain, a._id)
        L.append('<item><title><![CDATA[')
        L.append(a.name)
        L.append(']]></title><link>')
        L.append(url)
        L.append('</link><guid>')
        L.append(url)
        L.append('</guid><author><![CDATA[')
        L.append(a.user_name)
        L.append(']]></author><pubDate>')
        L.append(_rss_datetime(a.publish_time))
        L.append('</pubDate><description><![CDATA[')
        L.append(utils.cached_markdown2html(a))
        L.append(']]></description></item>')
    L.append(r'</channel></rss>')
    return ''.join(map(_safe_str, L))

###############################################################################
# Category management
###############################################################################

@get('/category/<cid>')
@theme('article/category.html')
def web_category(cid):
    category = Categories.get_by_id(cid)
    if category is None:
        raise notfound()
    page, articles = page_select(Articles, 'where category_id=? and publish_time<?', 'where category_id=? and publish_time<? order by publish_time desc', cid, time.time())
    reads = counters.counts((a._id for a in articles))
    for a, r in zip(articles, reads):
        a.reads = r
    return dict(category=category, page=page, articles=articles)

def _clear_categories_cache():
    pass

def _get_categories():
    return Categories.select('order by display_order')

def _check_category_id(cat_id):
    if cat_id:
        cat = Categories.get_by_id(cat_id)
        if cat:
            return cat_id
    raise APIValueError('category_id', 'Invalid category id.')

@api
@check()
@get('/api/categories')
def api_list_categories():
    '''
    List all categories.
    '''
    return _get_categories()

@api
@check()
@post('/api/categories/create')
def api_create_category():
    '''
    Create a new category.
    '''
    i = ctx.request.input(name='', description='')
    name = assert_not_empty(i.name, 'name')
    description = i.description.strip()
    c = Categories(name=name, description=description, display_order=len(_get_categories())).insert()
    _clear_categories_cache()
    return c

@api
@check()
@post('/api/categories/<cid>/update')
def api_update_category(cid):
    cat = Categories.get_by_id(cid)
    if cat is None:
        raise APIValueError('_id', 'category not found.')
    i = ctx.request.input()
    update = False
    if 'name' in i:
        cat.name = assert_not_empty(i.name.strip(), 'name')
        update = True
    if 'description' in i:
        cat.description = i.description.strip()
        update = True
    if update:
        cat.update()
        _clear_categories_cache()
    return dict(result=True)

@api
@check()
@post('/api/categories/<cid>/delete')
def api_delete_category(cid):
    cat = Categories.get_by_id(cid)
    if cat is None:
        raise APIValueError('_id', 'category not found.')
    if len(Articles.select('where category_id=?', cat._id)) > 0:
        raise APIValueError('_id', 'cannot delete non-empty categories.')
    cat.delete()
    _clear_categories_cache()
    return dict(result=True)

@api
@check()
@post('/api/categories/sort')
def api_sort_categories():
    '''
    Sort categories.
    '''
    ids = ctx.request.gets('_id')
    cats = _get_categories()
    l = len(cats)
    if l != len(ids):
        raise APIValueError('_id', 'bad id list.')
    sets = set([c._id for c in cats])
    odict = dict()
    n = 0
    for o in ids:
        if not o in sets:
            raise APIValueError('_id', 'some id was invalid.')
        odict[o] = n
        n = n + 1
    with db.transaction():
        for c in cats:
            db.update('update categories set display_order=?, version=version+1 where _id=?', odict.get(c._id, l), c._id)
    _clear_categories_cache()
    return dict(result=True)

@view('templates/article/categories_list.html')
def categories():
    return dict(categories=_get_categories())

@view('templates/article/category_form.html')
def create_category():
    return dict(form_title='Create New Category', form_action='/api/categories/create')

@view('templates/article/category_form.html')
def edit_category():
    cat = Categories.get_by_id(ctx.request['_id'])
    return dict( \
        form_title='Edit Category', \
        form_action='/api/categories/%s/update' % cat._id, \
        name = cat.name, \
        description = cat.description)

###############################################################################
# Article management
###############################################################################

@get('/article/<aid>')
@theme('article/article.html')
def web_get_article(aid):
    article = Articles.get_by_id(aid)
    if article is None or article.draft:
        raise notfound
    article.reads = counters.incr(aid)
    article.content = texts.md2html(texts.get(article.content_id))
    category = Categories.get_by_id(article.category_id)
    return dict(article=article, category=category, comments=comments.get_comments(aid))

TIME_FEATURE = 5500000000.0

@api
@check()
@post('/api/articles/create')
def api_create_article():
    i = ctx.request.input(name='', summary='', category_id='', tags='', draft='', publish_time='', cover=None, content='')
    if not i.cover:
        raise APIValueError('cover', 'Cover cannot be empty.')
    name = assert_not_empty(i.name, 'name')
    summary = assert_not_empty(i.summary, 'summary')
    category_id = _check_category_id(i.category_id)
    content = assert_not_empty(i.content, 'content')
    draft = i.draft.lower()=='true'
    if draft:
        publish_time = time.time() + TIME_FEATURE
    else:
        publish_time = time2timestamp(i.publish_time) if i.publish_time else time.time()

    f = i.cover
    atta = uploaders.upload_cover(name, f.file.read())

    article_id = db.next_id()
    article = Articles( \
        _id = article_id, \
        user_id = ctx.user._id, \
        cover_id = atta._id, \
        category_id = category_id, \
        content_id = texts.set(article_id, content), \
        publish_time = publish_time, \
        draft = draft, \
        user_name = ctx.user.name, \
        name = name, \
        summary = summary, \
        tags = texts.format_tags(i.tags) \
    ).insert()
    return dict(_id=article._id)

@api
@check()
@post('/api/articles/<aid>/update')
def api_update_article(aid):
    article = Articles.get_by_id(aid)
    if article is None:
        raise notfound()
    i = ctx.request.input()
    update = False
    if 'name' in i:
        article.name = assert_not_empty(i.name, 'name')
        update = True
    if 'summary' in i:
        article.summary = assert_not_empty(i.summary, 'summary')
        update = True
    if 'category_id' in i:
        article.category_id = _check_category_id(i.category_id)
        update = True
    if 'tags' in i:
        article.tags = texts.format_tags(i.tags)
        update = True
    # update draft first:
    if 'draft' in i:
        if i.draft.lower()=='true':
            if not article.draft: # change False to True:
                article.draft = True
                if article.publish_time < TIME_FEATURE:
                    article.publish_time = article.publish_time + TIME_FEATURE
                update = True
        else:
            if article.draft: # change True to False:
                article.draft = False
                # update publish time:
                if 'publish_time' in i and i.publish_time.strip():
                    article.publish_time = time2timestamp(i.publish_time)
                else:
                    article.publish_time = time.time()
                update = True
    if 'content' in i:
        content = assert_not_empty(i.content, 'content')
        article.content = content
        update = True
    old_cover_id = ''
    if 'cover' in i:
        f = i.cover
        if f:
            # update cover:
            old_cover_id = article.cover_id
            atta = uploaders.upload_cover(article.name, f.file.read())
            article.cover_id = atta._id
            update = True
    if hasattr(article, 'content'):
        article.content_id = texts.set(article._id, article.content)
    if update:
        article.update()
    if old_cover_id:
        uploaders.delete_attachment(old_cover_id)
    return dict(_id=article._id)

@api
@check()
@post('/api/articles/<aid>/delete')
def api_delete_article(aid):
    a = Articles.get_by_id(aid)
    if a is None:
        raise notfound()
    a.delete()
    uploaders.delete_attachment(a.cover_id)
    comments.delete_comments(aid)
    return dict(result=True)

@api
@post('/api/articles/<aid>/comments/create')
def api_create_article_comment(aid):
    u = ctx.user
    if u is None:
        raise APIPermissionError()
    i = ctx.request.input(content='')
    content = assert_not_empty(i.content, 'content')
    a = Articles.get_by_id(aid)
    if a is None:
        raise notfound()
    return comments.create_comment('article', aid, content)

@view('templates/article/articles_list.html')
def index():
    categories = _get_categories()
    cat_dict = dict(((c._id, c.name) for c in categories))
    fn_get_category_name = lambda cid: cat_dict.get(cid, u'ERROR')
    page, articles = page_select(Articles, '', 'order by publish_time desc')
    return dict( \
        page = page, \
        articles = articles, \
        categories = categories, \
        fn_get_category_name = fn_get_category_name)

@view('templates/article/article_form.html')
def create_article():
    return dict(form_title='Create New Article', form_action='/api/articles/create', categories=_get_categories())

@view('templates/article/article_form.html')
def edit_article():
    article = Articles.get_by_id(ctx.request['_id'])
    if article is None:
        raise notfound()
    return dict( \
        form_title = u'Edit Article', \
        form_action = '/api/articles/%s/update' % article._id, \
        _id = article._id, \
        name = article.name, \
        category_id = article.category_id, \
        draft = article.draft, \
        publish_time = article.publish_time, \
        tags = article.tags, \
        summary = article.summary, \
        cover_id = article.cover_id, \
        content = texts.get(article.content_id), \
        categories = _get_categories())
