#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
A WSGI application.
'''

import conf_prod

from wsgiapp import create_app

application = create_app()
