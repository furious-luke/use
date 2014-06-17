import datetime, time
from nose.tools import *
from use.Context import Context
from use.Node import Node
from use.File import File

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
