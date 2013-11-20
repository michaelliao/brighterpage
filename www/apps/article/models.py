#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Models for Articles, Categories.
'''

import time

from transwarp import db

TIME_FEATURE = 10000000000.0 # about Nov. 21, 2286 AD.

class Categories(db.Model):
    '''
    Category object.
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    display_order = db.IntegerField()
    name = db.StringField(ddl='varchar(50)')
    description = db.StringField(ddl='varchar(100)')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class Articles(db.Model):
    '''
    @@ index idx_publish_time(publish_time)
    @@ index idx_user_id(user_id)
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    user_id = db.StringField(updatable=False, ddl='varchar(50)')
    category_id = db.StringField(ddl='varchar(50)')
    cover_id = db.StringField(ddl='varchar(50)')
    content_id = db.StringField(ddl='varchar(50)')

    draft = db.BooleanField(ddl='bool')
    user_name = db.StringField(updatable=False, ddl='varchar(20)')

    name = db.StringField(ddl='varchar(50)')
    tags = db.StringField(ddl='varchar(200)')
    summary = db.StringField(ddl='varchar(1000)')

    publish_time = db.FloatField(ddl='real')
    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()
        if self.draft:
            self.publish_time = TIME_FEATURE + self.creation_time
        else:
            if 'publish_time' not in self or self.publish_time < 1.0:
                self.publish_time = self.creation_time

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1
