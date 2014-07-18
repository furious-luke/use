import os, tempfile, datetime
from nose.tools import *
from use.DB import DB
from use.Node import Node
from use.Package import Package
from use.Use import Use

class ContextMock(object):
    pass

class OtherPackage(Package):
    pass

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
    db.flush()
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

def test_save_uses():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    uses = [
        Use(Package(ContextMock())),
        Use(OtherPackage(ContextMock()))
    ]
    db.save_uses(uses)
    db.flush()
    assert_equal(db._cur_key, 2)
    assert_equal(db._keys, {uses[0]: 0, uses[1]: 1})
    os.remove(fn)

def test_load_uses():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    uses = [
        Use(Package(ContextMock())),
        Use(OtherPackage(ContextMock()))
    ]
    db.save_uses(uses)
    db.flush()
    new_uses = db.load_uses()
    # assert_equal(new_uses[0].
    os.remove(fn)

# def test_save_rules():
#     with tempfile.NamedTemporaryFile(delete=False) as file:
#         fn = file.name
#     db = DB(fn)
#     rules = [Rule('a', 'u1'), Rule('b', 'u2')]
#     db.save_rule(n)
#     os.remove(fn)
