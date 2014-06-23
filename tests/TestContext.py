import datetime, time
from nose.tools import *
from use.Context import Context
from use.Node import Node
from use.File import File
from use.Rule import Rule

class DummyDB(object):
    def __init__(self, ex):
        self.ex = ex
    def exists(self):
        return self.ex

def test_node():
    ctx = Context()
    n = ctx.node(Node, 'a')
    assert_equal(isinstance(n, Node), True)
    assert_equal(n.key, 'a')

def test_node_duplicate():
    ctx = Context()
    a = ctx.node(Node, 'a')
    b = ctx.node(Node, 'b')
    c = ctx.node(Node, 'a')
    assert_is(a, c)
    assert_is_not(a, b)

def test_file():
    ctx = Context()
    n = ctx.file('some/path')
    assert_equal(isinstance(n, File), True)

def test_needs_configure_manual():
    ctx = Context()
    ctx.arguments = type('', (object,), {'targets': []})
    assert_equal(ctx.needs_configure(), False)
    ctx.arguments = type('', (object,), {'targets': ['configure']})
    assert_equal(ctx.needs_configure(), True)
    ctx.arguments = type('', (object,), {'targets': ['reconfigure']})
    assert_equal(ctx.needs_configure(), True)

def test_needs_configure_db_missing():
    ctx = Context()
    ctx.arguments = type('', (object,), {'targets': []})
    ctx._db = DummyDB(True)
    assert_equal(ctx.needs_configure(), False)
    ctx._db = DummyDB(False)
    assert_equal(ctx.needs_configure(), True)

def test_needs_configure_match():
    ctx = Context()
    ctx.arguments = type('', (object,), {'targets': []})
    ctx._db = DummyDB(True)
    assert_equal(ctx.needs_configure(), False)
    ctx.rules = [Rule('src', 'use', 'cond', 'opts')]
    ctx._ex_rules = []
    assert_equal(ctx.needs_configure(), True)
