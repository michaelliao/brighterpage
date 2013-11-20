#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Models for static pages.
'''

import time

from transwarp import db

class Pages(db.Model):
    '''
    Static page object.

    @@ unique idx_alias(alias)
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    alias = db.StringField(updatable=False, ddl='varchar(50)')
    content_id = db.StringField(ddl='varchar(50)')

    draft = db.BooleanField()
    name = db.StringField(ddl='varchar(50)')
    tags = db.StringField(ddl='varchar(200)')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1
