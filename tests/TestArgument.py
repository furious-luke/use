import copy
from nose.tools import *
from use.Argument import *

class Context(object):
    def argument(self, name):
        return name

def test_init():
    ctx = Context()
    kw = {'one': 1}
    arg = Argument('a', ctx, 'b', kw)
    assert_equals(arg.name, 'a')
    assert_equals(arg.context, ctx)
    assert_equals(arg.use, 'b')
    assert_equals(arg._kwargs, kw)

def test_eq():
    arg = Argument('a', Context(), 'b')
    ac = arg == 'b'
    assert_equals(ac.op, 'eq')
    assert_is(ac.left, arg)
    assert_equals(ac.right, 'b')

def test_and():
    arg = Argument('a', Context(), 'b')
    ac = arg & 'b'
    assert_equals(ac.op, 'and')
    assert_is(ac.left, arg)
    assert_equals(ac.right, 'b')

def test_add():
    arg = Argument('a', Context(), 'b')
    ac = arg + 'b'
    assert_equals(ac.op, 'add')
    assert_is(ac.left, arg)
    assert_equals(ac.right, 'b')

def test_deepcopy():
    arg = Argument('a', Context(), {'one': 1})
    cp = copy.deepcopy(arg)
    assert_is(cp.name, arg.name)
    assert_is(cp.context, arg.context)
    assert_is(cp.use, arg.use)

def test_contains():
    arg = Argument('a', Context(), 'b')
    ac = arg.contains('b')
    assert_equals(ac.op, 'in')
    assert_is(ac.left, arg)
    assert_equals(ac.right, 'b')

def test_value_no_use():
    arg = Argument('a', Context())
    assert_equals(arg.value(), 'a')

def test_value_use_callable():
    arg = Argument('a', Context(), type('Use', (object,), {'a': lambda self: 'c'})())
    assert_equals(arg.value(), 'c')

def test_value_use_not_callable():
    arg = Argument('a', Context(), type('Use', (object,), {'a': 'c'}))
    assert_equals(arg.value(), 'c')

def test_compare():
    arg0 = Argument('a', Context(), 'b')
    arg1 = Argument('c', Context(), 'b')
    assert_equals(arg0.compare(arg1), False)
    arg0 = Argument('a', Context(), 'b')
    arg1 = Argument('a', Context(), 'c')
    assert_equals(arg0.compare(arg1), False)
    arg0 = Argument('a', Context(), 'b')
    arg1 = Argument('a', Context(), 'b')
    assert_equals(arg0.compare(arg1), True)
