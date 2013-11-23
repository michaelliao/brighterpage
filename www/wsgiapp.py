#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
A WSGI application entry.
'''

import os

import logging; logging.basicConfig(level=logging.INFO)

from transwarp import web, db, cache

import conf
from apps.user import load_user

def create_app():
    configs = conf.configs
    debug = configs['debug']
    logging.info('starting %s mode...' % ('DEBUG' if debug else 'PROD'))
    logging.info('db conf: %s' % str(configs['db']))
    logging.info('cache conf: %s' % str(configs['cache']))
    # init db:
    db.init(db_type='mysql',
        db_schema=configs['db']['schema'], \
        db_host=configs['db']['host'], \
        db_port=configs['db']['port'], \
        db_user=configs['db']['user'], \
        db_password=configs['db']['password'], \
        use_unicode=True, charset='utf8')
    # init cache:
    cache.client = cache.MemcacheClient(configs['cache']['host'])
    scan = ['apps.article', 'apps.stpage', 'apps.wiki', 'apps.attachment', 'apps.navigation', 'apps.user', 'apps.comment', 'apps.setting', 'core.manage']
    if debug:
        scan.append('static_handler')
    return web.WSGIApplication(scan, \
            document_root=os.path.dirname(os.path.abspath(__file__)), \
            filters=(load_user, ), \
            template_engine='jinja2', \
            DEBUG=debug)
