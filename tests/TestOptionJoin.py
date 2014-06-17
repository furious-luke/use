from nose.tools import *
from use.Options import OptionJoin, OptionDict

def test_init():
    od1 = OptionDict(one='1', two='2')
    od2 = OptionDict(three='3', four='4')
    oj = OptionJoin(od1, od2)
    assert_is(oj.left, od1)
    assert_is(oj.right, od2)

def test_get():
    od1 = OptionDict(one='1', two='2')
    od2 = OptionDict(three='3', four='4')
    oj = OptionJoin(od1, od2)
    opts = oj.get()
    assert_equals(opts, {'one': '1', 'two': '2', 'three': '3', 'four': '4'})

def test_get_overwrite():
    od1 = OptionDict(one='1', two='2')
    od2 = OptionDict(one='3', four='4')
    oj = OptionJoin(od1, od2)
    opts = oj.get()
    assert_equals(opts, {'one': '3', 'two': '2', 'four': '4'})

def test_get_optional_overwrite():
    od1 = OptionDict(one='1', two='2')
    od2 = OptionDict(one='3', four='4')
    od3 = OptionDict(False, two='5')
    oj = OptionJoin(od1, od2) + od3
    opts = oj.get()
    assert_equals(opts, {'one': '3', 'two': '2', 'four': '4'})
    od3.condition = True
    opts = oj.get()
    assert_equals(opts, {'one': '3', 'two': '5', 'four': '4'})
