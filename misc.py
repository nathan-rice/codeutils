'''
Created on Sep 13, 2011

@author: Administrator
'''

import inspect
import collections
import re
import types
import datetime
from simplejson import JSONEncoder
import simplejson
import sys
import cProfile

sys.setrecursionlimit(5000)

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
    return "_".join(n.lower() for n in re.findall(r"[A-Z][a-z0-9]*", name))

def camelcase_to_sentence(name):
    return " ".join(n.lower() for n in re.findall(r"[A-Z][a-z0-9]*", name)).title()

def underscore_to_camelcase(name):
    return "".join(n.title() for n in name.split("_"))

def underscore_to_titlecase(name):
    return "".join(n.lower() for n in name.split("_")).title()


class EasyEncoder(JSONEncoder):
    '''
    JSON encoder that handles custom classes fairly gracefully.
    '''

    def __init__(self, *args, **kwargs):
        super(EasyEncoder, self).__init__(*args, **kwargs)
        self._seen_registry = set()

    def default(self, o):
        try:
            if hasattr(o, 'isoformat'):
                return o.isoformat()
            if isinstance(o, collections.Mapping):
                return {k:v for (k, v) in o.items() if id(v) not in self._seen_registry}
            elif isinstance(o, collections.Iterable):
                return list(i for i in o if id(i) not in self._seen_registry)
            else:
                attributes = get_attributes(o)
                for v in attributes.values():
                    if not isinstance(o, (basestring, int, float)):
                        self._seen_registry.add(id(o))
                attributes = {k:v for (k, v) in attributes.items() if id(v) not in self._seen_registry}
                return attributes
        except TypeError:
            return JSONEncoder.default(self, o)


def dumps(o):
    enc = BoundedGoodEncoder()
    return enc.encode(o)

class GoodEncoder(object):

    def __init__(self):
        self.micro_encoder_map = {
            dict: self._dict_encoder,
            list: self._list_encoder,
            tuple: self._tuple_encoder,
            set: self._set_encoder,
            str: self._string_encoder,
            unicode: self._string_encoder,
            basestring: self._string_encoder,
            int: self._int_encoder,
            long: self._int_encoder,
            float: self._float_encoder,
            bool: self._bool_encoder,
            types.NoneType: self._none_encoder,
            datetime.datetime: self._datetime_encoder,
            object: self._default_encoder
        }
        self.initiator_map = {
            dict: lambda x: "{",
            object: lambda x: "{",
            list: lambda x: "[",
            set: lambda x: "[",
            tuple: lambda x: "[",
            str: lambda x: "'"
        }
        self.terminator_map = {
            dict: lambda x: "}",
            object: lambda x: "}",
            list: lambda x: "]",
            set: lambda x: "]",
            tuple: lambda x: "]",
            str: lambda x: "'"
        }
        self.map_separator = ":"
        self.item_separator = ","

    def _number_encoder(self, o):
        yield str(o)

    def _bool_encoder(self, o):
        yield o and "true" or "false"

    def _none_encoder(self, o):
        yield "null"

    def _string_encoder(self, o):
        yield "'"
        yield o
        yield "'"

    def _datetime_encoder(self, o):
        yield "'"
        yield o.isoformat()
        yield "'"

    def _dict_encoder(self, o):
#        yield self.get_map_entry(o, self.initiator_map)
        yield "{"
        start = True
        for (k, v) in o.items():
            if start:
                start = False
            else:
#                yield self.item_separator
                yield ":"
            for i in self.get_map_entry(k, self.micro_encoder_map):
                yield i
#            yield self.map_separator
            yield ":"
            for i in self.get_map_entry(v, self.micro_encoder_map):
                yield i
#        yield self.get_map_entry(o, self.terminator_map)
        yield "}"

    def _default_encoder(self, o):
#        yield self.get_map_entry(o, self.initiator_map)
        yield "{"
        start = True
        for (k, v) in get_attributes(o).items():
            if start:
                start = False
            else:
#                yield self.item_separator
                yield ","
            for i in self.get_map_entry(k, self.micro_encoder_map):
                yield i
#            yield self.map_separator
            yield ":"
            for i in self.get_map_entry(v, self.micro_encoder_map):
                yield i
#        yield self.get_map_entry(o, self.terminator_map)
        yield "}"

    def _iterable_encoder(self, o, True=True, False=False):
#        yield self.get_map_entry(o, self.initiator_map)
        yield "["
        start = True
        for e in o:
            if start:
                start = False
            else:
#                yield self.item_separator
                yield ","
            for i in self.get_map_entry(e, self.micro_encoder_map):
                yield i
#        yield self.get_map_entry(o, self.terminator_map)
        yield "]"

    def get_map_entry(self, o, map):
        _get = map.get
        for t in type(o).__mro__:
            translator = _get(t, None)
            if translator:
                return translator(o)

    def encode(self, o):
        gen = tuple(self.get_map_entry(o, self.micro_encoder_map))
        return ''.join(gen)

    # small optimizations here
    _list_encoder = _set_encoder = _tuple_encoder = _iterable_encoder

    _int_encoder = _float_encoder = _number_encoder


class BoundedGoodEncoder(GoodEncoder):

    def __init__(self):
        super(BoundedGoodEncoder, self).__init__()
        self._seen = set()

    def _default_encoder(self, o):
        object_id = id(o)
        if object_id in self._seen:
            yield "null"
        else:
            self._seen.add(object_id)
            for e in super(BoundedGoodEncoder, self)._default_encoder(o):
                yield e
            self._seen.discard(object_id)

    def _iterable_encoder(self, o):
        object_id = id(o)
        if object_id in self._seen:
            yield "null"
        else:
            self._seen.add(object_id)
            for e in super(BoundedGoodEncoder, self)._iterable_encoder(o):
                yield e
            self._seen.discard(object_id)

    def _dict_encoder(self, o):
        object_id = id(o)
        if object_id in self._seen:
            yield "null"
        else:
            self._seen.add(object_id)
            for e in super(BoundedGoodEncoder, self)._dict_encoder(o):
                yield e
            self._seen.discard(object_id)

    _list_encoder = _set_encoder = _tuple_encoder = _iterable_encoder


class TestObject(object):
    def __init__(self, a, b , c):
        self.foo = a
        self.bar = b
        self.baz = c

if __name__ == "__main__":
    foo = BoundedGoodEncoder()
    test1 = TestObject(1, 2, 3)
    test2 = TestObject(test1, 2, 3)
    test1.foo = test2
    a = []
    b = []
    a.append(b)
    b.append(a)
    print foo.encode([test1, datetime.datetime(2010, 1, 1), {1:"A", 2:"B", 3:True, 4:None, 5:["a", "b", 1.145]}, "3", 4])
    testdata = []
    data1 = [1, 1.01, 'hello world', True, None, -1, 11.011, "~!@#$%^&*()_+|", False, None]
    data2 = {}
    for k in ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']:
        data2[k] = data1
    for k in range(10):
        testdata.append(data2)
    cProfile.run("dumps(testdata)", "c:\\Development\\test_output.txt")
    start = datetime.datetime.now()
    for i in range(1000):
        dumps(testdata)
    end = datetime.datetime.now()
    print end - start
    start = datetime.datetime.now()
    for i in range(1000):
        simplejson.dumps(testdata)
    end = datetime.datetime.now()
    print end - start


