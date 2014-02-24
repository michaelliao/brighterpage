#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Build release package.
'''

import os

from datetime import datetime
from fabric.api import *

env.user = 'root'
env.hosts = ['www.liaoxuefeng.com']

_TAR_FILE = 'brighterpage.tar.gz'
_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE

_REMOTE_DIST_LINK = '/srv/liaoxuefeng.com/www'
_REMOTE_DIST_DIR = '/srv/liaoxuefeng.com/www-%s' % datetime.now().strftime('%y-%m-%d_%H.%M.%S')

def _current_path():
    return os.path.abspath('.')

##########
# backup #
##########

def backup():
    dt = datetime.now().strftime('%y-%m-%d_%H.%M.%S')
    f = 'liaoxuefeng-backup-%s.sql' % dt
    remote_path = '/srv/liaoxuefeng.com'
    with cd(remote_path):
        run('mysqldump --user=root --password=asdfjkl --skip-opt --add-drop-table --default-character-set=utf8 --quick brighterpage > %s' % f)
        run('tar -czvf %s.tar.gz %s' % (f, f))
        get('%s.tar.gz' % f, '%s/backup/' % _current_path())
        run('rm -f %s' % f)

def _build():
    includes = ['apps', 'core', 'static', 'templates', 'themes', 'transwarp', 'app.py', 'conf.py', 'conf_prod.py', 'favicon.ico', 'markdown2.py', 'memcache.py', 'snspy.py', 'wsgiapp.py']
    excludes = ['.*', '*.pyc', '*.pyo', '*.psd', 'static/css/bp-less/*', 'themes/default/static/css/less/*']
    local('rm -f %s' % _TAR_FILE)
    cmd = ['tar', '--dereference', '-czvf', '../%s' % _TAR_FILE]
    cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
    cmd.extend(includes)
    local(' '.join(cmd))

def _scp():
    run('rm -f %s' % _REMOTE_TMP_TAR)
    put(_TAR_FILE, _REMOTE_TMP_TAR)
    run('mkdir %s' % _REMOTE_DIST_DIR)
    with cd(_REMOTE_DIST_DIR):
        run('tar -xzvf %s' % _REMOTE_TMP_TAR)
    run('chown -R www-data:www-data %s' % _REMOTE_DIST_DIR)
    run('rm -f %s' % _REMOTE_DIST_LINK)
    run('ln -s %s %s' % (_REMOTE_DIST_DIR, _REMOTE_DIST_LINK))
    run('chown www-data:www-data %s' % _REMOTE_DIST_LINK)
    with settings(warn_only=True):
        run('supervisorctl stop liaoxuefeng')
        run('supervisorctl start liaoxuefeng')

def make():
    with lcd('www'):
        _build()
    _scp()
