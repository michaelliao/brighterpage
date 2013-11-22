#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
comment app.
'''

from transwarp.web import post

from core.apis import api, check
from core.models import Comments

@api
@check()
@post('/api/comments/<cid>/delete')
def delete_comment(cid):
    c = Comments.get_by_id(cid)
    if c is None:
        raise notfound()
    c.delete()
    return dict(result=True)
