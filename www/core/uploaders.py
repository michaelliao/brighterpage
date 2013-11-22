#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Upload service.
'''

import mimetypes

from datetime import datetime

from transwarp.web import ctx, notfound
from transwarp import db

from models import Attachments, Resources

from thumbnails import check_image_size, create_thumbnails, create_covers, get_image_info

def delete_attachment(atta_id):
    atta = Attachments.get_by_id(atta_id)
    if atta is None:
        return
    atta.delete()
    db.update('delete from resources where ref_id=?', atta_id)

def upload_cover(name, fcontent):
    '''
    upload image for cover. generate large jpeg image, medium jpeg image and small jpeg image, 
    but do NOT keep original image.

    return:
      Attachments object.
    '''
    # check fcontent:
    check_image_size(fcontent, 320, 180)
    covers = create_covers(fcontent, (640, 360), (320, 180), (160, 90))
    return _store_files('image/cover', name, covers)

def upload_image(name, fcontent):
    '''
    upload image for inline use. keep origin image, medium jpeg image and small jpeg image.
    return:
      Attachments object.
    '''
    ext, w, h = get_image_info(fcontent)
    # generate m, s:
    sizes = []
    keep_origin = (w <= 640)
    if not keep_origin:
        sizes.append((640, 0))
    sizes.append((160, 0))
    pics = create_thumbnails(fcontent, *sizes)
    if keep_origin:
        mime = mimetypes.types_map.get(ext, 'application/octet-stream')
        pics.insert(0, (mime, 'width=%s&height=%s' % (w, h), fcontent))
    return _store_files('image/inline', name, pics)

def _store_files(kind, name, files):
    '''
    Store a group of files as attachment.
    Args:
        kind: attachment type. e.g. 'image/cover'
        name: attachment name.
        files: list of (mime, meta, data).
    Returns:
        Attachments object.
    '''
    ref_id = db.next_id()
    atta = Attachments(_id=ref_id, user_id=ctx.user._id, kind=kind, name=name)
    resources = []
    for mime, meta, data in files:
        r_id = db.next_id()
        url = '/files/%s/%s' % (datetime.now().strftime('%Y/%m/%d'), r_id)
        r = Resources(_id=r_id, ref_id=ref_id, url=url, size=len(data), mime=mime, meta=meta, data=data)
        resources.append(r)
    atta.size = resources[0].size
    atta.resource_ids = ','.join([r._id for r in resources])
    with db.transaction():
        atta.insert()
        for r in resources:
            r.insert()
    return atta

def get_image_url(atta_id, index):
    ' index = 0 (origin), 1 (large), 2 (medium), 3 (small)... '
    a = Attachments.get_by_id(atta_id)
    if not a:
        raise notfound()
    if not a.kind.startswith('image/'):
        raise notfound()
    rs = Resources.select('where ref_id=?', atta_id)
    rs.sort(cmp=_cmp_image)
    url = rs[-1].url if index >= len(rs) else rs[index].url
    raise redirect(url)

