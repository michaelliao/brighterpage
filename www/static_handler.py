#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Handle static file with url '.../static/...'.

It is ONLY used in developement. You should use web server (e.g. nginx) to handle static file.
'''

import os, logging, mimetypes

from transwarp.web import ctx, get, HttpError

def _static_file_generator(fpath):
    BLOCK_SIZE = 8192
    with open(fpath, 'rb') as f:
        block = f.read(BLOCK_SIZE)
        while block:
            yield block
            block = f.read(BLOCK_SIZE)

@get('/<path:pre>/static/<path:file>')
def static_file_handler(pre, file):
    pathinfo = ctx.request.path_info
    if not pathinfo.startswith('/'):
        raise HttpError('403')
    fpath = os.path.join(ctx.application.document_root, pathinfo[1:])
    logging.info('static file: %s' % fpath)
    if not os.path.isfile(fpath):
        raise HttpError(404)
    fext = os.path.splitext(fpath)[1]
    ctx.response.content_type = mimetypes.types_map.get(fext.lower(), 'application/octet-stream')
    ctx.response.content_length = os.path.getsize(fpath)
    return _static_file_generator(fpath)

if __name__=='__main__':
    import doctest
    doctest.testmod()
