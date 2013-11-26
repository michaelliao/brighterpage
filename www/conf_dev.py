#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' development-mode configurations '

import conf

conf.configs = {

    'debug': True,

    'auth': {
        'salt': 'debug',
    },

    'db': {
        'schema': 'brighterpage',
        'host': 'localhost',
        'port': 3306,
        'user': 'www-data',
        'password': 'www-data',
    },

    'cache': {
        'host': 'localhost:11211',
    },

    'store': {
        'db',
    },

    'oauth': {
        'SinaWeibo': {
            'app_id': '???',
            'app_secret': '???',
        },
        'QQ': {
            'app_id': '???',
            'app_secret': '???',
        },
    },

    'mail': {
        'host': 'smtp.sohu.com',
        'port': 25,
        'username': 'brighterpage',
        'password': 'BrighterPage',
    }

}
