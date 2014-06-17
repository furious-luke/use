import datetime, time
from nose.tools import *
from use.Node import Node

def test_init():
    pass

def test_crc_property():
    n = Node('a')
    assert_equal(n.crc, None)
    assert_equal(n._crc, None)
    n.crc = '123abc'
    assert_equal(n.crc, '123abc')
    assert_equal(n._crc, '123abc')
    assert_equal(n._modified, True)
    n._ex_crc = '123abc'
    n.crc = '123abc'
    assert_equal(n._modified, False)

def test_mtime_property():
    n = Node('a')
    assert_equal(n.mtime, None)
    assert_equal(n._mtime, None)
    time = datetime.datetime.now()
    n.mtime = time
    assert_equal(n.mtime, time)
    assert_equal(n._mtime, time)
    assert_equal(n._outdated, True)
    n._ex_mtime = time
    n.mtime = time
    assert_equal(n._outdated, False)

def test_update_outdated_newer():
    n = Node'a'()
    n._ex_mtime = datetime.datetime.now()
    time.sleep(0.1)
    n._mtime = datetime.datetime.now()
    n._update_outdated()
    assert_equal(n._outdated, True)

def test_update_outdated_same():
    n = Node('a')
    n._mtime = datetime.datetime.now()
    n._ex_mtime = n._mtime
    n._update_outdated()
    assert_equal(n._outdated, False)

def test_update_outdated_older():
    n = Node('a')
    n._mtime = datetime.datetime.now()
    time.sleep(0.1)
    n._ex_mtime = datetime.datetime.now()
    assert_raises(Exception, n._update_outdated)

def test_update_outdated_missing_mtime():
    n = Node('a')
    n._mtime = None
    n._ex_mtime = datetime.datetime.now()
    n._update_outdated()
    assert_equal(n._outdated, True)

def test_update_outdated_missing_ex_mtime():
    n = Node('a')
    n._mtime = datetime.datetime.now()
    n._ex_mtime = None
    n._update_outdated()
    assert_equal(n._outdated, True)

def test_update_modified_changed():
    n = Node('a')
    n._crc = '123abc'
    n._ex_crc = '456def'
    n._update_modified()
    assert_equal(n._modified, True)

def test_update_modified_unchanged():
    n = Node('a')
    n._crc = '123abc'
    n._ex_crc = '123abc'
    n._update_modified()
    assert_equal(n._modified, False)

def test_update_modified_missing_crc():
    n = Node('a')
    n._crc = None
    n._ex_crc = '123abc'
    n._update_modified()
    assert_equal(n._modified, True)

def test_update_modified_missing_ex_crc():
    n = Node('a')
    n._crc = '123abc'
    n._ex_crc = None
    n._update_modified()
    assert_equal(n._modified, True)
