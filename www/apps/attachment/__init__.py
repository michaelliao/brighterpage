#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
auth app.
'''

import os, time, hashlib, base64, functools, logging

from transwarp.web import get, post, ctx, route, view, seeother, notfound
from transwarp import db

from core.apis import api, template, page_select
from core.models import Attachments
from core import uploaders

def get_manage_menu():
    return 'Attachments', 1000

@api
@post('/api/images/create')
def api_create_images():
    i = ctx.request.input(name='', file=None)
    if not i.file:
        raise APIValueError('file', 'File cannot be empty.')
    f = i.file
    filename = f.filename
    name = os.path.splitext(os.path.split(filename)[1])[0]
    atta = uploaders.upload_image(name, f.file.read())
    atta.url = '/files/attachments/%s/0' % atta._id
    return atta

@api
@post('/api/attachments/<aid>/delete')
def api_delete_attachment(aid):
    uploaders.delete_attachment(aid)
    return dict(result=True)

@view('templates/attachment/attachments_list.html')
def index():
    page, attachments = page_select(Attachments, '', 'order by creation_time desc')
    return dict(page = page, attachments = attachments)

@get('/files/attachments/<aid>')
def attachment_by_id(aid):
    return _get_attachment(aid, 0)

@get('/files/attachments/<aid>/<int:index>')
def api_attachment_by_index(aid, index):
    if index=='s':
        return _get_attachment(aid, -1)
    return _get_attachment(aid, int(index))

def _get_attachment(atta_id, index):
    atta = Attachments.get_by_id(atta_id)
    if atta:
        rs = atta.resource_ids.split(',')
        if index >= (-1) and index < len(rs):
            return _get_resource(rs[index])
    raise notfound()

@get('/files/resources/<y>/<m>/<d>/<rid>')
def resource_by_id(y, m, d, rid):
    return _get_resource(rid, '/files/%s/%s/%s/%s' % (y, m, d, rid))

def _get_resource(rid, url=None):
    logging.info('Get resource: %s, %s' % (rid, url))
    r = db.select_one('select url, mime, size, data from resources where _id=?', rid)
    if url and r.url!=url:
        raise notfound()
    resp = ctx.response
    resp.content_type = r.mime
    resp.content_length = r.size
    return r.data
