import os
from nose.tools import *
from use.Options import OptionDict, parse, merge
from use.Argument import Argument

class Context(object):
    def argument(self, name):
        assert name == 'test'
        return 'arg_val'

def test_init():
    od = OptionDict(one='1', two='2')
    assert_equal(od.condition, True)
    assert_equal(od._opts, {'one': '1', 'two': '2'})
    od = OptionDict('hello', one='1', two='2')
    assert_equal(od.condition, 'hello')
    assert_equal(od._opts, {'one': '1', 'two': '2'})

def test_get_depth_0():
    one = Argument('test', Context())
    od = OptionDict(one=one, two='2')
    opts = od.get()
    assert_equals(opts, {'one': 'arg_val', 'two': '2'})
    assert_is_not(opts, od._opts)

def test_get_depth_1():
    one = Argument('test', Context())
    od = OptionDict(one=one, two='2')
    opts = od.get(depth=1)
    assert_equals(opts, {'one': one, 'two': '2'})
    assert_is_not(opts, od._opts)

def test_get_disabled():
    one = Argument('test', Context())
    od = OptionDict(False, one=one, two='2')
    opts = od.get()
    assert_equals(opts, {})

def test_parse_argument():
    one = Argument('test', Context())
    od = OptionDict(one=one, two='2')
    parse(od._opts)
    assert_equals(od._opts, {'one': 'arg_val', 'two': '2'})

def test_parse_format():
    od = OptionDict(one='1', two='2{one}')
    parse(od._opts)
    assert_equals(od._opts, {'one': '1', 'two': '21'})

def test_parse_format_recursive():
    od = OptionDict(one='1', two='2{one}', three='3{one}{two}')
    parse(od._opts)
    assert_equals(od._opts, {'one': '1', 'two': '21', 'three': '3121'})

def test_merge_dicts():
    x = {'a': 1, 'b': 2}
    y = {'c': 3, 'd': 4}
    assert_equal(merge(x, y), {'a': 1, 'b': 2, 'c': 3, 'd': 4})
    assert_equal(x, {'a': 1, 'b': 2})
    assert_equal(y, {'c': 3, 'd': 4})

def test_merge_option_dicts():
    x = OptionDict(a=1, b=2)
    y = OptionDict(c=3, d=4)
    assert_equal(merge(x, y), {'a': 1, 'b': 2, 'c': 3, 'd': 4})
    assert_equal(x, OptionDict(a=1, b=2))
    assert_equal(y, OptionDict(c=3, d=4))

def test_merge_combo():
    x = OptionDict(a=1, b=2)
    y = {'c': 3, 'd': 4}
    assert_equal(merge(x, y), {'a': 1, 'b': 2, 'c': 3, 'd': 4})
    assert_equal(merge(y, x), {'a': 1, 'b': 2, 'c': 3, 'd': 4})
    assert_equal(x, OptionDict(a=1, b=2))
    assert_equal(y, {'c': 3, 'd': 4})

def test_merge_nones():
    assert_equal(merge(None, None), {})

def test_merge_one_none():
    x = {'a': 1, 'b': 2}
    assert_equal(merge(x, None), {'a': 1, 'b': 2})
    assert_equal(merge(None, x), {'a': 1, 'b': 2})
