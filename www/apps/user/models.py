#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Users model.
'''

import time, uuid, random

from transwarp import db

class Users(db.Model):
    '''
    user object.

    @@ unique key uk_email(email)
    @@ index idx_creation_time(creation_time)
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    name = db.StringField(ddl='varchar(50)')
    role = db.IntegerField(default=1000000, ddl='int')

    email = db.StringField(updatable=False, ddl='varchar(100)')
    verified = db.BooleanField(ddl='bool')

    binds = db.StringField(ddl='varchar(100)')
    passwd = db.StringField(ddl='varchar(100)')
    image_url = db.StringField(ddl='varchar(1000)')

    locked_time = db.FloatField(ddl='real')
    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class AuthUsers(db.Model):
    '''
    Authenticate user by third-party. e.g. weibo.

    @@ unique key uk_auth_id(auth_id)
    @@ index idx_creation_time(creation_time)
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    user_id = db.StringField(ddl='varchar(50)')

    auth_provider = db.StringField(updatable=False, ddl='varchar(50)')
    auth_id = db.StringField(updatable=False, ddl='varchar(200)')
    auth_token = db.StringField(ddl='varchar(200)')

    expires_time = db.FloatField()
    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()

    def pre_update(self):
        self.modified_time = time.time()
        self.version = self.version + 1

class AuthRandoms(db.Model):
    '''
    @@ unique key uk_value(value)
    @@ index idx_expires_time(expires_time)
    '''

    _id = db.StringField(primary_key=True, default=db.next_id, ddl='varchar(50)')

    value = db.StringField(updatable=False, default=lambda: '%s%s' % (uuid.uuid4().hex, random.randrange(100000000,999999999)), ddl='varchar(100)')
    expires_time = db.FloatField(updatable=False, default=lambda: time.time() + 600, ddl='real')

    creation_time = db.FloatField(updatable=False)
    modified_time = db.FloatField()
    version = db.VersionField()

    def pre_insert(self):
        self.creation_time = self.modified_time = time.time()
