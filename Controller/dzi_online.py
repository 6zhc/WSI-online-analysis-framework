from collections import OrderedDict
from flask import abort, make_response
from io import BytesIO
import openslide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator
import os
from threading import Lock


def add_dzi_sever(app):
    app.config['SLIDE_CACHE_SIZE'] = 10
    app.config['DEEPZOOM_FORMAT'] = 'jpeg'
    app.config['DEEPZOOM_TILE_SIZE'] = 254
    app.config['DEEPZOOM_OVERLAP'] = 1
    app.config['DEEPZOOM_LIMIT_BOUNDS'] = True
    app.config['DEEPZOOM_TILE_QUALITY'] = 75

    @app.before_request
    def before_request():
        app.basedir = './'
        config_map = {
            'DEEPZOOM_TILE_SIZE': 'tile_size',
            'DEEPZOOM_OVERLAP': 'overlap',
            'DEEPZOOM_LIMIT_BOUNDS': 'limit_bounds',
        }
        opts = dict((v, app.config[k]) for k, v in config_map.items())
        app.cache = _SlideCache(app.config['SLIDE_CACHE_SIZE'], opts)

    class PILBytesIO(BytesIO):
        def fileno(self):
            # Classic PIL doesn't understand io.UnsupportedOperation.
            raise AttributeError('Not supported')

    class _SlideCache(object):
        def __init__(self, cache_size, dz_opts):
            self.cache_size = cache_size
            self.dz_opts = dz_opts
            self._lock = Lock()
            self._cache = OrderedDict()

        def get(self, path):
            with self._lock:
                if path in self._cache:
                    # Move to end of LRU
                    slide = self._cache.pop(path)
                    self._cache[path] = slide
                    return slide

            osr = OpenSlide(path)
            slide = DeepZoomGenerator(osr, **self.dz_opts)
            try:
                mpp_x = osr.properties[openslide.PROPERTY_NAME_MPP_X]
                mpp_y = osr.properties[openslide.PROPERTY_NAME_MPP_Y]
                slide.mpp = (float(mpp_x) + float(mpp_y)) / 2
            except (KeyError, ValueError):
                slide.mpp = 0

            with self._lock:
                if path not in self._cache:
                    if len(self._cache) == self.cache_size:
                        self._cache.popitem(last=False)
                    self._cache[path] = slide
            return slide

    class _Directory(object):
        def __init__(self, basedir, relpath=''):
            self.name = os.path.basename(relpath)
            self.children = []
            for name in sorted(os.listdir(os.path.join(basedir, relpath))):
                cur_relpath = os.path.join(relpath, name)
                cur_path = os.path.join(basedir, cur_relpath)
                if os.path.isdir(cur_path):
                    cur_dir = _Directory(basedir, cur_relpath)
                    if cur_dir.children:
                        self.children.append(cur_dir)
                elif OpenSlide.detect_format(cur_path):
                    self.children.append(_SlideFile(cur_relpath))

    class _SlideFile(object):
        def __init__(self, relpath):
            self.name = os.path.basename(relpath)
            self.url_path = relpath

    def _get_slide(path):
        path = os.path.abspath(os.path.join(app.basedir, path))
        # if not path.startswith(app.basedir + os.path.sep):
        #     # Directory traversal
        #     abort(404)
        if not os.path.exists(path):
            print(path)
            abort(404)
        try:
            slide = app.cache.get(path)
            slide.filename = os.path.basename(path)
            return slide
        except OpenSlideError:
            abort(404)

    @app.route('/dzi_online/<path:path>.dzi')
    def dzi(path):
        slide = _get_slide(path)
        format = app.config['DEEPZOOM_FORMAT']
        resp = make_response(slide.get_dzi(format))
        resp.mimetype = 'application/xml'
        return resp

    @app.route('/dzi_online/<path:path>_files/<int:level>/<int:col>_<int:row>.<format>')
    def tile(path, level, col, row, format):
        slide = _get_slide(path)
        format = format.lower()
        if format != 'jpeg' and format != 'png':
            # Not supported by Deep Zoom
            abort(404)
        try:
            tile = slide.get_tile(level, (col, row))
        except ValueError:
            # Invalid level or coordinates
            abort(404)
        buf = PILBytesIO()
        tile.save(buf, format, quality=app.config['DEEPZOOM_TILE_QUALITY'])
        resp = make_response(buf.getvalue())
        resp.mimetype = 'image/%s' % format
        return resp
