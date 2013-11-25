#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
setting app.
'''

import time, urllib, hashlib, base64, functools, logging

from transwarp.web import get, post, ctx, route, view, seeother, notfound
from transwarp import db

from core.apis import api, check, template, APIError
from core.models import SNSTokens

from core import sns

from conf import configs

def get_manage_menu():
    return 'Settings', 10000

###############################################################################
# Settings
###############################################################################

@view('templates/setting/settings.html')
def index():
    return dict()

###############################################################################
# SNS Tokens
###############################################################################

@api
@check()
@post('/api/settings/snstokens/<tid>/delete')
def api_delete_snstoken(tid):
    t = SNSTokens.get_by_id(tid)
    if t is None:
        raise notfound()
    t.delete()
    return dict(result=True)

@view('templates/setting/snstokens_list.html')
def snstokens():
    tokens = SNSTokens.select('order by expires_time')
    t_now = time.time()
    t_warning = t_now + 432000.0
    for t in tokens:
        if t.expires_time < t_now:
            t.css = 'error'
        elif t.expires_time < t_warning:
            t.css = 'warning'
        else:
            t.css = ''
    return dict(snstokens=tokens)

@check()
def auth_from_weibo():
    provider = 'SinaWeibo'
    p = sns.create_client(provider)
    callback = 'http://%s/manage/setting/auth_callback_weibo' % ctx.request.host
    raise seeother(p.get_authorize_url(callback, forcelogin='true'))

@check()
def auth_callback_weibo():
    provider = 'SinaWeibo'
    p = sns.create_client(provider)

    callback = 'http://%s/manage/setting/auth_callback_weibo' % ctx.request.host
    i = ctx.request.input(code='', state='')
    code = i.code
    if not code:
        raise IOError('missing code')
    state = i.state
    r = p.request_access_token(code, callback)
    thirdpart_id = r['uid']
    info = p.users.show.get(uid=thirdpart_id)
    name = info['screen_name']
    auth_id = '%s-%s' % (provider, thirdpart_id)
    auth_token = r['access_token']
    expires_time = r['expires']
    db.update('delete from snstokens where auth_provider=?', provider)
    SNSTokens(auth_id=auth_id, auth_provider=provider, auth_name=name, auth_token=auth_token, expires_time=expires_time).insert()
    raise seeother('/manage/setting/snstokens')
