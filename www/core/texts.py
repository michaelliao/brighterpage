#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Texts services for store and retreive big text.
'''

import re, logging, functools

import markdown2

from models import Texts

def md2html(md):
    if isinstance(md, str):
        md = md.decode('utf-8')
    return unicode(markdown2.markdown(md))

def get(_id):
    ' get text value '
    return Texts.get_by_id(_id).value

def gets(ref_id):
    '''
    Get texts objects.
    '''
    return Texts.select('where ref_id=? order by creation_time desc', ref_id)

def set(ref_id, text):
    return Texts(ref_id=ref_id, value=text).insert()._id

def delete(ref_id):
    db.update('delete from texts where ref_id=?', ref_id)

_TAG_SPLITTER = re.compile(u',|;|\uff0c|\uff1b')

def format_tags(tags):
    if tags:
        return u','.join([s for s in [t.strip() for t in _TAG_SPLITTER.split(tags)] if s])
    return u''

if __name__=='__main__':
    import doctest
    doctest.testmod()
 