import os
from nose.tools import *
from use.Options import Option

def test_init_no_options():
    assert_raises(AssertionError, Option)

def test_init_no_name():
    assert_equals(Option(short_opts='a').name, 'a')
    assert_equals(Option(long_opts='abc').name, 'abc')

def test_init():
    opt = Option('hello', 'a', 'abc')
    assert_equals(opt.name, 'hello')
    assert_items_equal(opt.short_opts, ['a'])
    assert_items_equal(opt.long_opts, ['abc'])
    assert_equals(opt.space, True)
    assert_equals(opt.text, None)
    assert_equals(opt.abspath, False)

def test_init_kwargs():
    opt = Option('hello', 'a', 'abc', space=False, text='more', abspath=True)
    assert_equals(opt.space, False)
    assert_equals(opt.text, 'more')
    assert_equals(opt.abspath, True)

def test_eq():
    opta = Option('hello', 'a', 'abc')
    optb = Option('world', 'b', 'bcd')
    assert_equals(opta, Option('hello', 'g'))
    assert_equals(opta, 'hello')
    assert_equals(opta, 'a')
    assert_equals(opta, 'abc')
    assert_not_equals(opta, optb)
    assert_not_equals(opta, 'world')
    assert_not_equals(opta, 'b')
    assert_not_equals(opta, 'bcd')

def test_call_bool():
    opta = Option('hello', 'a', 'abc')
    assert_equals(opta(True), ['a'])

def test_call_bool_text():
    opta = Option('hello', 'a', 'abc', text='some_text')
    assert_equals(opta(True), ['some_text'])

def test_call_bool_text_format():
    opta = Option('hello', 'a', 'abc', text='some_text_{conv}')
    assert_equals(opta(True, {'conv': 'value'}), ['some_text_value'])

def test_call_list():
    opta = Option('hello', 'a', 'abc')
    assert_equals(opta(['1', '2']), ['a', '1', 'a', '2'])

def test_call_list_no_space():
    opta = Option('hello', 'a', 'abc', space=False)
    assert_equals(opta(['1', '2']), ['a1', 'a2'])

def test_call():
    opta = Option('hello', 'a', 'abc')
    assert_equals(opta('1'), ['a', '1'])

def test_call_no_space():
    opta = Option('hello', 'a', 'abc', space=False)
    assert_equals(opta('1'), ['a1'])

def test_call_abspath():
    opta = Option('hello', 'a', 'abc', abspath=True)
    assert_equals(opta('1'), ['a', os.path.join(os.getcwd(), '1')])
    assert_equals(opta('/1'), ['a', '/1'])

def test_call_assign():
    opta = Option('hello', 'a', 'abc')
    assert_equals(opta(('B', '1')), ['aB=1'])
    assert_equals(opta([('B', '1'), ('C', '2')]), ['aB=1', 'aC=2'])
