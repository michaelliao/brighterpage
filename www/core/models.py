#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Models for core services.
'''

import time, uuid, random, hashlib

from transwarp.web import ctx
from transwarp import db

class Navigations(db.Model):
    '''
    Navigation object.
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    display_order = db.IntegerField()
    name = db.StringField(ddl='varchar(50)')
    url = db.StringField(ddl='varchar(1000)')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class Texts(db.Model):
    '''
    @@ index idx_ref_id(ref_id)
    @@ index idx_creation_time(creation_time)
    '''
    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    ref_id = db.StringField(updatable=False, ddl='varchar(50)')
    value = db.StringField(updatable=False, ddl='text')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class Attachments(db.Model):
    '''
    Attachment object.
    
    @@ index idx_creation_time(creation_time)
    '''

    _id = db.StringField(primary_key=True, ddl='varchar(50)')

    user_id = db.StringField(updatable=False, ddl='varchar(50)')
    resource_ids = db.StringField(updatable=False, ddl='varchar(1000)')

    kind = db.StringField(updatable=False, ddl='varchar(50)')
    size = db.IntegerField(updatable=False)
    name = db.StringField(updatable=False, ddl='varchar(100)')
    description = db.StringField(updatable=False, default='', ddl='varchar(100)')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class Resources(db.Model):
    '''
    A resource represents a single file.
    
    @@ index idx_ref_id(ref_id)
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    ref_id = db.StringField(updatable=False, ddl='varchar(50)')

    deleted = db.BooleanField()

    size = db.IntegerField(updatable=False)
    meta = db.StringField(updatable=False, ddl='varchar(100)')
    mime = db.StringField(updatable=False, ddl='varchar(100)')
    url = db.StringField(updatable=False, ddl='varchar(2000)')
    data = db.BlobField(updatable=False, ddl='mediumblob')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class Comments(db.Model):
    '''
    Comment object.
    
    @@ index idx_ref_id(ref_id)
    '''
    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')
    ref_id = db.StringField(updatable=False, ddl='varchar(50)')
    ref_type = db.StringField(updatable=False, ddl='varchar(50)')

    user_id = db.StringField(updatable=False, ddl='varchar(50)')
    user_name = db.StringField(updatable=False, ddl='varchar(50)')
    user_image_url = db.StringField(updatable=False, ddl='varchar(1000)')

    content = db.StringField(updatable=False, ddl='varchar(1000)')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class SNSTokens(db.Model):
    '''
    SNS Token object.
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    auth_provider = db.StringField(updatable=False, ddl='varchar(50)')
    auth_name = db.StringField(updatable=False, ddl='varchar(50)')
    auth_token = db.StringField(updatable=False, ddl='varchar(200)')

    creation_time = db.FloatField(updatable=False)
    expires_time = db.FloatField(updatable=False)
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = time.time()
