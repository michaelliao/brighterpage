#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
comment app.
'''

from transwarp.web import post, view

from core.apis import api, check, page_select
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

def get_manage_menu():
    return 'Comments', 50

@view('templates/comment/comments_list.html')
def index():
    page, cs = page_select(Comments, '', 'order by creation_time desc')
    return dict(comments=cs, page=page)
