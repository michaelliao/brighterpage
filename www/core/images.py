#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Attachments services for store and retreive attachments.
'''

import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    import Image
except ImportError:
    from PIL import Image

def _load_from_file(fpath):
    with open(fpath, 'rb') as f:
        return f.read()

def _cover(fcontent, tw, th):
    '''
    >>> pwd = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'tests')
    
    >>> # cover from 1000 x 600 to 500 x 300:

    >>> f1000x600 = _load_from_file(os.path.join(pwd, '1000x600.jpg'))
    >>> f = _cover(f1000x600, 500, 300)
    >>> f.size
    (500, 300)
    >>> f.save(os.path.join(pwd, 'saved-cover-500x300.jpg'), 'JPEG')
    
    >>> # cover from 960 x 600 to 700 x 600:
    
    >>> f960x600 = _load_from_file(os.path.join(pwd, '960x600.jpg'))
    >>> f = _cover(f960x600, 700, 600)
    >>> f.size
    (700, 600)
    >>> f.save(os.path.join(pwd, 'saved-cover-700x600.jpg'), 'JPEG')
    
    >>> # cover from 720 x 300 to 500 x 400:
    
    >>> f720x300 = _load_from_file(os.path.join(pwd, '720x300.jpg'))
    >>> f = _cover(f720x300, 300, 400)
    >>> f.size
    (300, 400)
    >>> f.save(os.path.join(pwd, 'saved-cover-300x400.jpg'), 'JPEG')
    
    >>> f = _cover(f720x300, 100, 200)
    >>> f.size
    (100, 200)
    >>> f.save(os.path.join(pwd, 'saved-cover-100x200.jpg'), 'JPEG')

    >>> f = _cover(f720x300, 100, 400)
    >>> f.size
    (100, 400)
    >>> f.save(os.path.join(pwd, 'saved-cover-100x400.jpg'), 'JPEG')

    >>> f440x640 = _load_from_file(os.path.join(pwd, '440x640.jpg'))
    >>> f = _cover(f440x640, 200, 100)
    >>> f.size
    (200, 100)
    >>> f.save(os.path.join(pwd, 'saved-cover-200x100.jpg'), 'JPEG')
    >>> f = _cover(f440x640, 500, 800)
    >>> f.size
    (500, 800)
    >>> f.save(os.path.join(pwd, 'saved-cover-500x800.jpg'), 'JPEG')
    '''
    if tw < 10 and th < 10:
        raise IOError('bad size.')
    im = Image.open(StringIO(fcontent))
    ow, oh = im.size[0], im.size[1]

    if ow * th == oh * tw:
        return im.resize((tw, th), Image.ANTIALIAS)

    if 1.0 * ow / oh > 1.0 * tw / th:
        ww = oh * tw / th
        x1 = (ow - ww) / 2
        x2 = x1 + ww
        nim = im.crop((x1, 0, x1 + ww, oh))
        return nim.resize((tw, th), Image.ANTIALIAS)

    else:
        hh = ow * th / tw
        y1 = (oh - hh) / 2
        nim = im.crop((0, y1, ow, y1 + hh))
        return nim.resize((tw, th), Image.ANTIALIAS)

def _scale(fcontent, tw, th, keep_aspect=True):
    '''
    >>> pwd = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'tests')
    
    >>> # scale from 1000 x 600 to 500 x ?:

    >>> f1000x600 = _load_from_file(os.path.join(pwd, '1000x600.jpg'))
    >>> f = _scale(f1000x600, 500, 0)
    >>> f.size
    (500, 300)
    >>> f.save(os.path.join(pwd, 'saved-scale-500x300.jpg'), 'JPEG')
    
    >>> # scale from 960 x 600 to ? x 120:
    
    >>> f960x600 = _load_from_file(os.path.join(pwd, '960x600.jpg'))
    >>> f = _scale(f960x600, 0, 120)
    >>> f.size
    (192, 120)
    >>> f.save(os.path.join(pwd, 'saved-scale-192x120.jpg'), 'JPEG')
    
    >>> # scale from 720 x 300 to 240 x 100 (exactly):
    
    >>> f720x300 = _load_from_file(os.path.join(pwd, '720x300.jpg'))
    >>> f = _scale(f720x300, 240, 100)
    >>> f.size
    (240, 100)
    >>> f.save(os.path.join(pwd, 'saved-scale-240x100.jpg'), 'JPEG')

    >>> # scale from 720 x 300 to 180 x 180 (auto scale):
    >>> f = _scale(f720x300, 180, 180)
    >>> f.size
    (180, 75)
    >>> f.save(os.path.join(pwd, 'saved-scale-180x75.jpg'), 'JPEG')

    >>> # scale from 720 x 300 to 180 x 180 (force scale):
    >>> f = _scale(f720x300, 180, 180, keep_aspect=False)
    >>> f.size
    (180, 180)
    >>> f.save(os.path.join(pwd, 'saved-scale-force-180x180.jpg'), 'JPEG')
    
    >>> # scale from 500 x 600 to 700 x 800 (enlarge):
    
    >>> f500x600 = _load_from_file(os.path.join(pwd, '500x600.jpg'))
    >>> f = _scale(f500x600, 700, 800)
    >>> f is None
    True
    
    >>> # scale from 960 x 600 to 599 x 499 (force):
    
    >>> f960x600 = _load_from_file(os.path.join(pwd, '960x600.jpg'))
    >>> f = _scale(f960x600, 599, 499, keep_aspect=False)
    >>> f.size
    (599, 499)
    >>> f.save(os.path.join(pwd, 'saved-scale-force-599x499.jpg'), 'JPEG')

    >>> _scale(f960x600, 0, 0)
    Traceback (most recent call last):
      ...
    ValueError: Invalid size (0, 0).
    '''
    if tw<=0 and th<=0:
        raise ValueError('Invalid size (%s, %s).' % (tw, th))
    im = Image.open(StringIO(fcontent))
    ow, oh = im.size[0], im.size[1]
    if tw >= ow and th >= oh:
        return None

    if not keep_aspect:
        if tw==0 and th==0:
            raise ValueError('Invalid size (0, 0).')
        return im.resize((tw, th), Image.ANTIALIAS)

    if th==0 and tw > 0:
        # scale to fit target width:
        th = tw * oh / ow
        if th < 4:
            th = 4
    elif tw==0 and th > 0:
        # scale to fit target height:
        tw = ow * th / oh
        if tw < 4:
            tw = 4
    im.thumbnail((tw, th), Image.ANTIALIAS)
    return im

def _to_jpeg(im):
    if im.mode != 'RGB':
        im = im.convert('RGB')
    return im.tostring('jpeg', 'RGB'), '.jpg', im.size[0], im.size[1]

_FORMATS = dict(JPEG='.jpg', PNG='.png', GIF='.gif')

def _format2ext(format):
    return _FORMATS.get(format)

def get_image_info(fcontent):
    '''
    get image info: ext, width, height.

    >>> pwd = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'tests')
    >>> get_image_info(_load_from_file(os.path.join(pwd, '1000x600.jpg')))
    ('.jpg', 1000, 600)
    >>> get_image_info(_load_from_file(os.path.join(pwd, 'test.png')))
    ('.png', 440, 432)
    >>> get_image_info(_load_from_file(os.path.join(pwd, 'test.gif')))
    ('.gif', 440, 370)
    '''
    im = Image.open(StringIO(fcontent))
    return _format2ext(im.format), im.size[0], im.size[1]

def check_size(fcontent, min_width, min_height):
    '''
    check if size less than min_width or min_height.

    >>> pwd = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'tests')
    >>> f1000x600 = _load_from_file(os.path.join(pwd, '1000x600.jpg'))
    >>> check_size(f1000x600, 800, 400)
    >>> check_size(f1000x600, 800, 700)
    Traceback (most recent call last):
      ...
    ValueError: Image too small.
    '''
    im = Image.open(StringIO(fcontent))
    w, h = im.size[0], im.size[1]
    if w < min_width or h < min_height:
        raise ValueError('Image too small.')

def create_covers(fcontent, *sizes):
    '''
    create a group of covers as (data, width, height).
    '''
    return [_to_jpeg(_cover(fcontent, w, h)) for w, h in sizes]

def create_thumbnails(fcontent, *sizes):
    '''
    create a group of thumbnails as (data, width, height).
    '''
    L = [_scale(fcontent, w, h) for w, h in sizes]
    return [_to_jpeg(im) for im in L if im is not None]

if __name__=='__main__':
    import doctest
    doctest.testmod()
