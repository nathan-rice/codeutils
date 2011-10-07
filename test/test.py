'''
Created on Sep 14, 2011

@author: Administrator
'''

import nose
from misc import EasyEncoder, get_attributes
from json import dumps

class TestClass(object):
    def __init__(self, one=None, two=None, three=None):
        self.a_one = one
        self.a_two = two
        self.a_three = three
        self._should_not_show_up = 4
        self.also_should_not_show_up = str

def test_get_attributes():
    test_instance = TestClass(1, 2, 3)
    assert get_attributes(test_instance) == { "a_one":1, "a_two":2, "a_three":3 }

def test_EasyEncoder():
    test_object = TestClass("one", [TestClass(1, 2, 3), TestClass(True, False, None)], TestClass("a", "b", "c"))
    assert dumps(test_object, cls=EasyEncoder) == '{"a_three": {"a_three": "c", "a_one": "a", "a_two": "b"}, "a_one": "one", "a_two": [{"a_three": 3, "a_one": 1, "a_two": 2}, {"a_three": null, "a_one": true, "a_two": false}]}'

if __name__ == "__main__":
    nose.runmodule(argv=["-d", "-s", "--with-xunit"])
