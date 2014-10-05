import datetime, time, tempfile, os
from nose.tools import *
from use.Context import Context
from use.Node import Node
from use.Package import Package
from use.File import File
from use.Rule import Rule
from use.Use import Use
from use.Options import OptionDict

class DummyDB(object):
    def __init__(self, ex):
        self.ex = ex
    def exists(self):
        return self.ex

class OtherPackage(Package):
    pass

def test_node():
    ctx = Context(db=False)
    n = ctx.node(Node, 'a')
    assert_equal(isinstance(n, Node), True)
    assert_equal(n.key, 'a')

def test_node_duplicate():
    ctx = Context(db=False)
    a = ctx.node(Node, 'a')
    b = ctx.node(Node, 'b')
    c = ctx.node(Node, 'a')
    assert_is(a, c)
    assert_is_not(a, b)

def test_file():
    ctx = Context(db=False)
    n = ctx.file('some/path')
    assert_equal(isinstance(n, File), True)

def test_needs_configure_manual():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    ctx = Context(db_path=fn)
    ctx.arguments = type('', (object,), {'targets': []})
    assert_equal(ctx.needs_configure(), False)
    ctx.arguments = type('', (object,), {'targets': ['configure']})
    assert_equal(ctx.needs_configure(), True)
    ctx.arguments = type('', (object,), {'targets': ['reconfigure']})
    assert_equal(ctx.needs_configure(), True)
    os.remove(fn)

def test_needs_configure_db_missing():
    ctx = Context(db=False)
    ctx.arguments = type('', (object,), {'targets': []})
    ctx._db = DummyDB(True)
    assert_equal(ctx.needs_configure(), False)
    ctx._db = DummyDB(False)
    assert_equal(ctx.needs_configure(), True)

def test_needs_configure_match():
    ctx = Context(db=False)
    ctx.arguments = type('', (object,), {'targets': []})
    ctx._db = DummyDB(True)
    assert_equal(ctx.needs_configure(), False)
    ctx.rules = [Rule('src', 'use', 'cond', 'opts')]
    ctx._ex_rules = []
    assert_equal(ctx.needs_configure(), True)

def test_needs_configure_save_load():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    ctx = Context(db_path=fn)
    ctx.arguments = type('', (object,), {'targets': []})
    uses = [
        Use(Package()),
        Use(OtherPackage()),
        Use(Package(), OptionDict(one='1')),
    ]
    rules = [
        Rule('a', uses[0]),
        Rule('b', uses[1]),
        Rule('c', uses[2]),
        Rule('d', uses[0], options=OptionDict(two='2')),
    ]
    rules[3].add_children(rules[:2])
    rules[1].add_children(rules[2])
    ctx.uses = uses
    ctx.rules = rules
    ctx._db.save_uses(uses)
    ctx._db.save_rules(rules)
    ctx._db.flush()
    ctx.load()
    assert_equal(ctx.needs_configure(), False)
    os.remove(fn)
