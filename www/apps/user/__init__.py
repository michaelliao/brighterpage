#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
auth app.
'''

import time, urllib, hashlib, base64, functools, logging

from transwarp.web import get, post, ctx, route, view, seeother, notfound
from transwarp import db

from models import Users, AuthUsers

from core.apis import api, template, theme, page_select, assert_email, assert_md5_passwd, ROLE_GUEST, APIError
from core.models import Attachments
from core import sns

from conf import configs

def get_manage_menu():
    return 'Users', 1200

###############################################################################
# User management
###############################################################################

@view('templates/user/users_list.html')
def index():
    page, users = page_select(Users, '', 'order by creation_time desc')
    return dict(users=users, page=page)

###############################################################################
# authentication
###############################################################################

_SIGNIN_FROM_LOCAL = 'local'

_SESSION_COOKIE_NAME = '_auth_token_'
_SESSION_COOKIE_SALT = configs['auth']['salt']

def load_user(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        user = extract_session_cookie()
        if user is None:
            auth = ctx.request.header('AUTHORIZATION')
            pass
        logging.info('bind ctx.user: %s' % user)
        ctx.user = user
        try:
            return func(*args, **kw)
        finally:
            del ctx.user
    return _wrapper

@api
@post('/api/authenticate')
def api_authenticate():
    '''
    Authenticate user by email and password.
    '''
    i = ctx.request.input(email='', passwd='')
    email = assert_email(i.email)
    passwd = assert_md5_passwd(i.passwd)
    user = Users.select_one('where email=?', email)
    if not user or not user.passwd or passwd != user.passwd:
        raise APIError('auth:failed', '', 'bad email or password.')
    make_session_cookie(_SIGNIN_FROM_LOCAL, user._id, passwd)
    # clear passwd:
    user.passwd = '******'
    return user

@get('/auth/signin')
@template('auth/signin.html')
def manage_signin():
    return dict()

@get('/auth/from/weibo')
def auth_from_weibo():
    provider = 'SinaWeibo'
    p = sns.create_client(provider)
    redirect = _get_redirect(excludes='/auth/')
    callback = 'http://%s/auth/callback/weibo?redirect=%s' % (ctx.request.host, urllib.quote(redirect))
    jscallback = ctx.request.get('jscallback', '')
    if jscallback:
        callback = '%s&jscallback=%s' % (callback, jscallback)
    raise seeother(p.get_authorize_url(callback))

@get('/auth/callback/weibo')
def auth_callback_weibo():
    provider = 'SinaWeibo'
    p = sns.create_client(provider)

    redirect = _get_redirect(excludes='/auth/')
    callback = 'http://%s/auth/callback/%s' % (ctx.request.host, provider)
    i = ctx.request.input(code='', state='')
    code = i.code
    if not code:
        raise IOError('missing code')
    state = i.state
    r = p.request_access_token(code, callback)

    thirdpart_id = r['uid']
    auth_id = '%s-%s' % (provider, thirdpart_id)
    auth_token = r['access_token']
    expires = r['expires']

    user = None
    auser = AuthUsers.select_one('where auth_id=?', auth_id)
    if auser:
        # already signed in before:
        auser.auth_token = auth_token
        auser.expires = expires
        auser.update()
        user = Users.get_by_id(auser.user_id)
        make_session_cookie(provider, auser._id, auth_token, expires)
    else:
        # not signed in before, so try to get info:
        info = p.users.show.get(uid=thirdpart_id)
        user_id = db.next_id()
        email = info['email'] if 'email' in info else '%s@tmp' % user_id
        name = info['screen_name']
        image_url = info['profile_image_url']
        user = Users(_id=user_id, role=ROLE_GUEST, binds=provider, email=email, name=name, image_url=image_url, passwd='')
        auser = AuthUsers( \
            user_id = user_id, \
            auth_id = auth_id, \
            auth_provider = provider, \
            auth_token = auth_token, \
            expires_time = expires \
        )
        with db.transaction():
            user.insert()
            auser.insert()
        make_session_cookie(provider, auser._id, auth_token, expires)
    jscallback = ctx.request.get('jscallback', '')
    if jscallback:
        ctx.response.write(r'''<html><body><script>
                window.opener.%s({'id': '%s', 'name': '%s'});
                self.close();
            </script></body></html>''' % (jscallback, user._id, user.name.replace('\'', '\\\'').replace('\n', '').replace('\r', '')));
        return
    raise seeother('/')

@route('/auth/signout')
def signout():
    delete_session_cookie()
    redirect = ctx.request.get('redirect', '')
    if not redirect:
        redirect = ctx.request.header('REFERER', '')
    if not redirect or redirect.find('/manage/')!=(-1) or redirect.find('/signin')!=(-1):
        redirect = '/'
    logging.debug('signed out and redirect to: %s' % redirect)
    raise seeother(redirect)

def make_session_cookie(signin_privider, uid, passwd, expires=None):
    '''
    Generate a secure client session cookie by constructing: 
    base64(signin_privider, uid, expires, md5(uid, expires, passwd, salt)).
    
    Args:
        signin_privider: signin from.
        uid: user id.
        expires: unix-timestamp as float.
        passwd: user's password.
        salt: a secure string.
    Returns:
        base64 encoded cookie value as str.
    '''
    signin_privider = str(signin_privider)
    sid = str(uid)
    exp = str(int(expires)) if expires else str(int(time.time() + 86400))
    secure = ':'.join([signin_privider, sid, exp, str(passwd), _SESSION_COOKIE_SALT])
    cvalue = ':'.join([signin_privider, sid, exp, hashlib.md5(secure).hexdigest()])
    logging.info('make cookie: %s' % cvalue)
    cookie = base64.urlsafe_b64encode(cvalue).replace('=', '.')
    ctx.response.set_cookie(_SESSION_COOKIE_NAME, cookie, expires=expires)

def extract_session_cookie():
    '''
    Decode a secure client session cookie and return user object, or None if invalid cookie.

    Returns:
        user as object, or None if cookie is invalid.
    '''
    try:
        s = str(ctx.request.cookie(_SESSION_COOKIE_NAME, ''))
        logging.debug('read cookie: %s' % s)
        if not s:
            return None
        ss = base64.urlsafe_b64decode(s.replace('.', '=')).split(':')
        if len(ss)!=4:
            raise ValueError('bad cookie: %s' % s)
        signin_privider, the_id, expires, md5 = ss

        # check if expires:
        if float(expires) < time.time():
            raise ValueError('expired cookie: %s' % s)

        # get user id and passwd:
        uid = the_id
        auth_token = None
        is_local = signin_privider == _SIGNIN_FROM_LOCAL
        if not is_local:
            au = AuthUsers.get_by_id(the_id)
            if not au:
                raise ValueError('bad cookie: auth user not found: %s' % the_id)
            uid = au.user_id
            auth_token = au.auth_token

        # get user:
        user = Users.get_by_id(uid)
        if not user:
            raise ValueError('bad cookie: user not found %s' % uid)

        expected_pwd = str(user.passwd) if is_local else auth_token
        expected = ':'.join([signin_privider, the_id, expires, expected_pwd, _SESSION_COOKIE_SALT])
        if hashlib.md5(expected).hexdigest()!=md5:
            raise ValueError('bad cookie: unexpected md5.')
        # clear password in memory:
        user.passwd = '******'
        user.is_local = is_local
        return user
    except BaseException, e:
        logging.exception('something wrong when extract cookie. now deleting cookie...')
        delete_session_cookie()
        return None

def delete_session_cookie():
    ' delete the session cookie immediately. '
    logging.debug('delete session cookie.')
    ctx.response.delete_cookie(_SESSION_COOKIE_NAME)

def _get_redirect(excludes=None):
    '''
    Get redirect url from parameter 'redirect'. 
    If argument not found, try using Referer header. 
    If the url starts with excludes, at least the path '/' will be returned.
    '''
    redirect = ctx.request.get('redirect', '')
    if not redirect:
        redirect = _get_referer(excludes)
    return redirect

def _get_referer(excludes=None):
    hh = 'http://%s/' % ctx.request.host
    sh = 'https://%s/' % ctx.request.host
    r = ctx.request.header('referer', '/')
    if r.startswith(hh):
        # http://mydomain/...
        r = r[len(hh)-1:]
    elif r.startswith(sh):
        # https://mydomain/...
        r = r[len(sh)-1:]
    elif r.startswith('http://') or r.startswith('https://'):
        # other websites:
        r = '/'
    if excludes and r.startswith(excludes):
        r = '/'
    return r
