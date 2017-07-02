'''Caching utilities'''
import io
import os
import six
import json
import yaml
import pandas as pd
from tornado.template import Template
from gramex.config import app_log


_opener_defaults = dict(mode='r', buffering=-1, encoding='utf-8', errors='strict',
                        newline=None, closefd=True)
_markdown_defaults = dict(output_format='html5', extensions=[
    'markdown.extensions.codehilite',
    'markdown.extensions.extra',
    'markdown.extensions.headerid',
    'markdown.extensions.meta',
    'markdown.extensions.sane_lists',
    'markdown.extensions.smarty',
])


def _opener(callback):
    '''
    Converts method that accepts a handle into a method that accepts a file path.
    For example, ``jsonload = _opener(json.load)`` allows ``jsonload('x.json')``
    to return the parsed JSON contents of ``x.json``.

    Any keyword arguments applicable for ``io.open`` are passed to ``io.open``.
    All other arguments and keyword arguments are passed to the callback (e.g.
    json.load).
    '''
    def method(path, **kwargs):
        open_args = {key: kwargs.pop(key, val) for key, val in _opener_defaults.items()}
        with io.open(path, **open_args) as handle:
            return callback(handle, **kwargs)
    return method


@_opener
def _markdown(handle, **kwargs):
    from markdown import markdown
    return markdown(handle.read(), **{k: kwargs.pop(k, v) for k, v in _markdown_defaults.items()})


_OPEN_CACHE = {}
_CALLBACKS = dict(
    txt=_opener(lambda handle: handle.read()),
    text=_opener(lambda handle: handle.read()),
    yaml=_opener(yaml.load),
    json=_opener(json.load),
    csv=pd.read_csv,
    excel=pd.read_excel,
    xls=pd.read_excel,
    xlsx=pd.read_excel,
    hdf=pd.read_hdf,
    html=pd.read_html,
    sas=pd.read_sas,
    stata=pd.read_stata,
    table=pd.read_table,
    template=_opener(lambda handle, **kwargs: Template(handle.read(), **kwargs)),
    md=_markdown,
    markdown=_markdown,
)


def open(path, callback, **kwargs):
    '''
    Reads a file, processes it via a callback, caches the result and returns it.
    When called again, returns the cached result unless the file has updated.

    The callback can be a function that accepts the filename and any other
    arguments, or a string that can be one of

    - ``text`` or ``txt``: reads files using io.open
    - ``yaml``: reads files using PyYAML
    - ``json``: reads files using json.load
    - ``template``: reads files using tornado.Template
    - ``markdown`` or ``md``: reads files using markdown.markdown
    - ``csv``, ``excel``, ``xls``, `xlsx``, ``hdf``, ``html``, ``sas``,
      ``stata``, ``table``: reads using Pandas

    For example::

        # Load data.yaml as YAML into an AttrDict
        open('data.yaml', 'yaml')

        # Load data.json as JSON into an AttrDict
        open('data.json', 'json', object_pairs_hook=AttrDict)

        # Load data.csv as CSV into a Pandas DataFrame
        open('data.csv', 'csv', encoding='cp1252')

        # Load data using a custom callback
        open('data.fmt', my_format_reader_function, arg='value')
    '''
    # Pass _reload_status = True for testing purposes. This returns a tuple:
    # (result, reloaded) instead of just the result.
    _reload_status = kwargs.pop('_reload_status', False)
    reloaded = False

    stat = os.stat(path)
    mtime, size = stat.st_mtime, stat.st_size
    _cache = kwargs.pop('_cache', _OPEN_CACHE)
    callback_is_str = isinstance(callback, six.string_types)
    key = (path, callback if callback_is_str else id(callback))
    if key not in _cache or mtime > _cache[key].get('mtime') or size != _cache[key].get('size'):
        reloaded = True
        if callable(callback):
            data = callback(path, **kwargs)
        elif callback_is_str:
            method = _CALLBACKS.get(callback)
            if method is not None:
                data = method(path, **kwargs)
            else:
                raise TypeError('gramex.cache.open(callback="%s") is not a known type', callback)
        else:
            raise TypeError('gramex.cache.open(callback=) must be a function, not %r', callback)
        _cache[key] = {'data': data, 'mtime': mtime, 'size': size}

    result = _cache[key]['data']
    return (result, reloaded) if _reload_status else result


# Date and size of file when module was last loaded. Used by reload_module
_MODULE_CACHE = {}


def reload_module(*modules):
    '''
    Reloads one or more modules if they are outdated, i.e. only if required the
    underlying source file has changed.

    For example::

        import mymodule             # Load cached module
        reload_module(mymodule)     # Reload module if the source has changed

    This is most useful during template development. If your changes are in a
    Python module, add adding these lines to pick up new module changes when
    the template is re-run.
    '''
    for module in modules:
        name = getattr(module, '__name__', None)
        path = getattr(module, '__file__', None)
        if name is None or path is None or not os.path.exists(path):
            app_log.warn('Path for module %s is %s: not found', name, path)
            continue
        # On Python 3, __file__ points to the .py file. In Python 2, it's the .pyc file
        # https://www.python.org/dev/peps/pep-3147/#file
        if path.lower().endswith('.pyc'):
            path = path[:-1]
            if not os.path.exists(path):
                app_log.warn('Path for module %s is %s: not found', name, path)
                continue
        # The first time, don't reload it. Thereafter, if it's older or resized, reload it
        stat = os.stat(path)
        time, size = stat.st_mtime, stat.st_size
        updated = _MODULE_CACHE.get((name, 't'), time) < time
        resized = _MODULE_CACHE.get((name, 's'), size) != size
        if updated or resized:
            app_log.info('Reloading module %s', name)
            six.moves.reload_module(module)
        _MODULE_CACHE[name, 't'], _MODULE_CACHE[name, 's'] = time, size
