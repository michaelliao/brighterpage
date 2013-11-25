#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Models for wikis.
'''

import time

from transwarp import db

class Wikis(db.Model):
    '''
    Wiki object.
    '''
    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    name = db.StringField(ddl='varchar(50)')
    description = db.StringField(ddl='varchar(100)')

    cover_id = db.StringField(ddl='varchar(50)')
    content_id = db.StringField(ddl='varchar(50)')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class WikiPages(db.Model):
    '''
    @@ index idx_wiki_id(wiki_id)
    '''
    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    wiki_id = db.StringField(updatable=False, ddl='varchar(50)')
    parent_id = db.StringField(ddl='varchar(50)')

    name = db.StringField(ddl='varchar(50)')
    content_id = db.StringField(ddl='varchar(50)')

    display_order = db.IntegerField()

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1
