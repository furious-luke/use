import datetime, time
from nose.tools import *
from use.Context import Context
from use.Node import Node
from use.File import File

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
    ctx._db = DummyDB(True)
    assert_equal(ctx.needs_configure(), False)
    ctx._db = DummyDB(False)
    assert_equal(ctx.needs_configure(), True)

def test_has_graph_changed_different_lengths():
    ctx = Context()
    ctx.rules = [1, 2]
    ctx._ex_rules = [1]
    assert_equal(ctx.has_graph_changed(), True)
    # TODO: Check success when same length

def test_has_graph_changed_same_rules():
    ctx = Context()
    ctx.rules = [Rule('a', 'u'), Rule('b', 'u')]
    ctx._ex_rules = []

def test_has_graph_changed_compatible():
    ctx = Context()
    ctx.rules = []
    ctx._ex_rules = []

def test_has_graph_changed_incompatible():
    ctx = Context()
    ctx.rules = []
    ctx._ex_rules = []
