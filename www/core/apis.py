#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
JSON API definition.
'''

import re, json, time, logging, functools

from datetime import datetime

from transwarp.web import ctx, get, post, seeother, HttpError, Template
from transwarp.cache import client as cache_client

from core.models import Navigations

ROLE_ADMIN = 0
ROLE_GUEST = 100000

def _get_navigations():
    return Navigations.select('order by display_order, name')

def theme(path):
    '''
    Theme uses 'themes/<active>' to get real template.
    '''
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kw):
            r = func(*args, **kw)
            if isinstance(r, dict):
                r['__user__'] = ctx.user
                r['__request__'] = ctx.request
                r['__time__'] = int(1000 * time.time())
                r['__navigations__'] = _get_navigations()
                r['__theme_path__'] = 'themes/default'
                return Template('themes/default/%s' % path, r)
            return r
        return _wrapper
    return _decorator

def _init_template(path, model):
    model['__get_template_file__'] = lambda f: '/templates/%s' % f
    model['__user__'] = ctx.user
    model['__request__'] = ctx.request
    model['__time__'] = int(1000 * time.time())
    return Template('templates/%s' % path, model)

def template(path):
    '''
    Template uses 'templates/<path>' to get real template.
    '''
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kw):
            r = func(*args, **kw)
            if isinstance(r, dict):
                return _init_template(path, r)
            return r
        return _wrapper
    return _decorator

def get_counts(*objs):
    keys = [obj.id for obj in objs]
    cs = cache_client.getints(*keys)
    for o, c in zip(objs, cs):
        o.read_count = c

def incr_count(obj):
    obj.read_count = cache_client.incr(obj.id)

class APIError(StandardError):
    '''
    the base APIError which contains error(required), data(optional) and message(optional).
    '''

    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    '''
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)

class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)

def time2timestamp(s):
    dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    return time.mktime(dt.timetuple())

def check(role=ROLE_ADMIN):
    '''
    Allow access to role id equals or less than.
    '''
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kw):
            u = ctx.user
            if u and u.role<=role:
                return func(*args, **kw)
            raise seeother('/auth/signin')
        return _wrapper
    return _decorator

def api(func):
    '''
    A decorator that makes a function to json api, makes the return value as json.

    @api
    @post('/articles/create')
    def api_articles_create():
        return dict(id='123')
    '''
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        ctx.response.content_type = 'application/json; charset=utf-8'
        try:
            return json.dumps(func(*args, **kw))
        except APIError, e:
            logging.exception('API Error when calling api function.')
            return json.dumps(dict(error=e.error, data=e.data, message=e.message))
        except Exception, e:
            logging.exception('Error when calling api function.')
            return json.dumps(dict(error='server:internal_error', data=e.__class__.__name__, message=e.message))
    return _wrapper

class Pagination(object):

    '''
    Pagination object for display pages.
    '''

    def __init__(self, item_count, page_index=1, page_size=10):
        '''
        Init Pagination by item_count, page_index and page_size.

        >>> p1 = Pagination(100, 1, 10)
        >>> p1.page_count
        10
        >>> p1.offset
        0
        >>> p1.limit
        10
        >>> p2 = Pagination(90, 9, 10)
        >>> p2.page_count
        9
        >>> p2.offset
        80
        >>> p2.limit
        10
        >>> p3 = Pagination(91, 10, 10)
        >>> p3.page_count
        10
        >>> p3.offset
        90
        >>> p3.limit
        1
        '''
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)

        if item_count == 0 or page_index < 1 or page_index > self.page_count:
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size if page_index < self.page_count else (self.item_count - (self.page_count - 1) * self.page_size)

    def page_list(self, nearby=3):
        '''
        Return pagination list with smart choice.

        >>> p = Pagination(1000, 1)
        >>> p.page_list()
        [1, 2, 3, 4, None, 100]
        >>> p = Pagination(1000, 2)
        >>> p.page_list()
        [1, 2, 3, 4, 5, None, 100]
        >>> p = Pagination(1000, 3)
        >>> p.page_list()
        [1, 2, 3, 4, 5, 6, None, 100]
        >>> p = Pagination(1000, 4)
        >>> p.page_list()
        [1, 2, 3, 4, 5, 6, 7, None, 100]
        >>> p = Pagination(1000, 5)
        >>> p.page_list()
        [1, 2, 3, 4, 5, 6, 7, 8, None, 100]
        >>> p = Pagination(1000, 6)
        >>> p.page_list()
        [1, None, 3, 4, 5, 6, 7, 8, 9, None, 100]
        >>> p = Pagination(1000, 7)
        >>> p.page_list()
        [1, None, 4, 5, 6, 7, 8, 9, 10, None, 100]
        >>> p = Pagination(1000, 95)
        >>> p.page_list()
        [1, None, 92, 93, 94, 95, 96, 97, 98, None, 100]
        >>> p = Pagination(1000, 96)
        >>> p.page_list()
        [1, None, 93, 94, 95, 96, 97, 98, 99, 100]
        >>> p = Pagination(1000, 97)
        >>> p.page_list()
        [1, None, 94, 95, 96, 97, 98, 99, 100]
        >>> p = Pagination(1000, 98)
        >>> p.page_list()
        [1, None, 95, 96, 97, 98, 99, 100]
        >>> p = Pagination(1000, 99)
        >>> p.page_list()
        [1, None, 96, 97, 98, 99, 100]
        >>> p = Pagination(1000, 100)
        >>> p.page_list()
        [1, None, 97, 98, 99, 100]
        '''
        n_min = max(1, self.page_index - nearby)
        n_max = min(self.page_count, self.page_index + nearby)
        L = range(n_min, n_max + 1)
        if n_min > 1:
            L.insert(0, 1)
            if n_min > 2:
                L.insert(1, None)
        if n_max < self.page_count:
            if n_max < (self.page_count - 1):
                L.append(None)
            L.append(self.page_count)
        return L

def page_select(model, count_sql, select_sql, *args):
    page_index = int(ctx.request.get('page', '1'))
    total = model.count(count_sql, *args)
    page = Pagination(total, page_index)
    if total > 0:
        new_args = []
        new_args.extend(args)
        new_args.append(page.offset)
        new_args.append(page.limit)
        return page, model.select('%s limit ?, ?' % select_sql, *new_args)
    return page, []

def assert_not_empty(text, name):
    if not text:
        raise APIValueError(name, '%s is empty.' % name)
    return text

def assert_int(s, name):
    try:
        return int(s)
    except ValueError:
        raise APIValueError(name, '%s is invalid integer.' % name)

def assert_float(s, name):
    try:
        return float(s)
    except ValueError:
        raise APIValueError(name, '%s is invalid float.' % name)

def assert_url(url, name):
    if not url:
        raise APIValueError(name, '%s is empty.' % name)
    url = url.strip()
    if not url:
        raise APIValueError(name, '%s is empty.' % name)
    if url.startswith('http://') or url.startswith('https://'):
        return url
    raise APIValueError(name, 'Invalid URL: %s.' % name)

_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')

def assert_md5_passwd(passwd):
    pw = str(passwd)
    if _RE_MD5.match(pw) is None:
        raise APIValueError('passwd', 'Invalid password.')
    return pw

_REG_EMAIL = re.compile(r'^[0-9a-z]([\-\.\w]*[0-9a-z])*\@([0-9a-z][\-\w]*[0-9a-z]\.)+[a-z]{2,9}$')

def assert_email(email):
    '''
    Validate email address and return formated email.

    >>> assert_email('michael@example.com')
    'michael@example.com'
    >>> assert_email(' Michael@example.com ')
    'michael@example.com'
    >>> assert_email(' michael@EXAMPLE.COM\\n\\n')
    'michael@example.com'
    >>> assert_email(u'michael.liao@EXAMPLE.com.cn')
    'michael.liao@example.com.cn'
    >>> assert_email('michael-liao@staff.example-inc.com.hk')
    'michael-liao@staff.example-inc.com.hk'
    >>> assert_email('007michael@staff.007.com.cn')
    '007michael@staff.007.com.cn'
    >>> assert_email('localhost')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('@localhost')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('michael@')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('michael@localhost')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('michael@local.host.')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('-hello@example.local')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('michael$name@local.local')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('user.@example.com')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('user-@example.com')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    >>> assert_email('user-0@example-.com')
    Traceback (most recent call last):
      ...
    APIValueError: Invalid email address.
    '''
    e = str(email).strip().lower()
    if _REG_EMAIL.match(e) is None:
        raise APIValueError('email', 'Invalid email address.')
    return e

if __name__=='__main__':
    import doctest
    doctest.testmod()
