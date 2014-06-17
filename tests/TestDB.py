import os, tempfile, datetime
from nose.tools import *
from use.DB import DB
from use.Node import Node

def test_init():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    assert_equal(db.filename, fn)
    assert_not_equal(db._conn, None)
    assert_equal(db._buf, [])
    os.remove(fn)

def test_save_node():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    n = Node('some/path')
    n.mtime = datetime.datetime.now()
    n.crc = '3893aef4'
    db.save_node(n)
    os.remove(fn)

def test_load_node():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    time = datetime.datetime.strptime(datetime.datetime.now().strftime('%c'), '%c')
    n = Node('some/path')
    n.mtime = time
    n.crc = '3893aef4'
    db.save_node(n)
    db.flush()
    assert_equals(n._ex_mtime, None)
    assert_equals(n._ex_crc, None)
    db.load_node(n)
    assert_equal(n.key, 'some/path')
    assert_equal(n._ex_mtime, time)
    assert_equal(n._ex_crc, '3893aef4')
    os.remove(fn)

def test_load_node_missing():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    n = Node('some/path')
    n._ex_mtime = datetime.datetime.now()
    n._ex_crc = 'world'
    db.load_node(n)
    assert_equal(n.key, 'some/path')
    assert_equal(n._ex_mtime, None)
    assert_equal(n._ex_crc, None)
    os.remove(fn)
