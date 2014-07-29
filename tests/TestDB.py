import os, tempfile, datetime
from nose.tools import *
from use.DB import DB
from use.Node import Node
from use.Package import Package
from use.Use import Use
from use.Rule import Rule

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
    assert_equal(len(new_uses), 2)
    assert_equal(isinstance(new_uses[0], Use), True)
    assert_equal(isinstance(new_uses[1], Use), True)
    assert_equal(isinstance(new_uses[0].package, Package), True)
    assert_equal(isinstance(new_uses[1].package, OtherPackage), True)
    assert_equal(new_uses[0].selected, None)
    assert_equal(new_uses[1].selected, None)
    assert_equal(new_uses[0].options, None)
    assert_equal(new_uses[1].options, None)
    os.remove(fn)

def test_save_rules():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    rules = [
        Rule('a', 'u1'),
        Rule('b', 'u2')
    ]
    rules[1].children = [rules[0]]
    db._keys['u1'] = 10
    db._keys['u2'] = 20
    db.save_rules(rules)
    db.flush()
    assert_equal(db._cur_key, 2)
    assert_equal(db._keys, {'u1': 10, 'u2': 20, rules[0]: 0, rules[1]: 1})
    os.remove(fn)

##
## Had accidentally set the 'parent' field on the DB to
## be a primary key, causing failures with multiple children.
##
def test_save_rules_multiple_children():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    rules = [
        Rule('a', 'u1'),
        Rule('b', 'u2'),
        Rule('c', 'u3'),
    ]
    rules[1].children = [rules[0], rules[2]]
    db._keys['u1'] = 10
    db._keys['u2'] = 20
    db._keys['u3'] = 30
    db.save_rules(rules)
    db.flush()
    assert_equal(db._cur_key, 3)
    assert_equal(db._keys, {'u1': 10, 'u2': 20, 'u3': 30, rules[0]: 0, rules[1]: 1, rules[2]: 2})
    os.remove(fn)

def test_load_rules():
    with tempfile.NamedTemporaryFile(delete=False) as file:
        fn = file.name
    db = DB(fn)
    rules = [
        Rule('a', 'u1'),
        Rule('b', 'u2')
    ]
    rules[1].children = [rules[0]]
    db._keys['u1'] = 10
    db._keys['u2'] = 20
    db._objs[10] = 'u1'
    db._objs[20] = 'u2'
    db.save_rules(rules)
    db.flush()
    rules = db.load_rules()
    assert_equal(len(rules), 2)
    assert_equal(rules[0].use, 'u1')
    assert_equal(rules[1].use, 'u2')
    assert_equal(rules[0].children, [])
    assert_equal(rules[1].children, [rules[0]])
    os.remove(fn)
