#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

import re

from transwarp.web import ctx, post, notfound

from apis import api, check, APIValueError, APIPermissionError, ROLE_ADMIN
from models import Comments

_RE_COMMENT = re.compile(ur'</?script>', re.UNICODE | re.IGNORECASE)

def get_comments(ref_id, next_id=None, limit=100):
    if next_id:
        return Comments.select('where ref_id=? and _id<? order by _id desc limit ?', ref_id, next_id, limit)
    return Comments.select('where ref_id=? order by _id desc limit ?', ref_id, limit)

def create_comment(ref_type, ref_id, content):
    content = _RE_COMMENT.sub('', content)
    if len(content)>1000:
        raise APIValueError('content', 'exceeded maximun length: 1000.')
    u = ctx.user
    return Comments(user_id=u._id, user_name=u.name, user_image_url=u.image_url, ref_id=ref_id, ref_type=ref_type, content=content).insert()

def delete_comments(ref_id):
    db.update('delete from comments where ref_id=?', ref_id)
