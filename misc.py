'''
Created on Sep 13, 2011

@author: Administrator
'''

import sys
import inspect
import collections
import re
from json import JSONEncoder

def get_module_classes(module):
    is_member = lambda m: getattr(m, "__module__", None) == module.__name__ and inspect.isclass(m)
    return inspect.getmembers(module, is_member)

def get_attributes(o):
    attributes = [
        (a, getattr(o, a)) for a in getattr(o, "__attributes__", None) or
        set(dir(o)).difference(dir(object)) if a[0] != "_"
    ]
    return {a[0]:a[1] for a in attributes if not callable(a[1])}

def camelcase_to_underscore(name):
    return "_".join(w.title() for w in re.findall(r"[A-Z][a-z0-9]+", name))

def underscore_to_camelcase(name):
    return "".join(n.title() for n in name.split("_"))


class NoQuotes(str):
    '''
    Stub class, to avoid quoting things that should not be quoted during JSON serialization.
    '''


class EasyEncoder(JSONEncoder):
    '''
    JSON encoder that handles custom classes fairly gracefully.
    '''

    def default(self, o):
        try:
            if hasattr(o, 'isoformat'):
                return o.isoformat()
            if isinstance(o, collections.Mapping):
                return dict(o.items())
            elif isinstance(o, collections.Iterable):
                return list(o)
            else:
#                is_valid_attribute = lambda a: not callable(getattr(o, a)) and a[0] is not "_"
#                object_attributes = set(dir(o)).difference(dir(object))
#                return { a:getattr(o, a) for a in object_attributes if is_valid_attribute(a) }
                return get_attributes(o)
        except TypeError:
            return JSONEncoder.default(self, o)
