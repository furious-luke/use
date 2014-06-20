from nose.tools import *
from use.Use import Use
from use.Package import Package

class Context(object):
    pass

class OtherPackage(Package):
    pass

def test_init():
    pkg = Package(Context())
    u = Use(pkg)
    assert_is(u.package, pkg)
    assert_equals(u.condition, None)
    assert_equals(u.options, None)
    assert_equals(u.selected, None)
    assert_equals(u.parents, [])
    assert_equals(u._found, False)
    assert_equals(pkg.uses, [u])

def test_eq_package():
    u1 = Use(Package(Context()))
    u2 = Use(Package(Context()))
    assert_equal(u1, u2)
    u1 = Use(Package(Context()))
    u2 = Use(OtherPackage(Context()))
    assert_not_equal(u1, u2)

def test_eq_condition():
    u1 = Use(Package(Context()), cond=None)
    u2 = Use(Package(Context()), cond=True)
    assert_not_equal(u1, u2)
    u1 = Use(Package(Context()), cond=None)
    u2 = Use(Package(Context()), cond=False)
    assert_not_equal(u1, u2)
    u1 = Use(Package(Context()), cond=None)
    u2 = Use(Package(Context()), cond=None)
    assert_equal(u1, u2)
    u1 = Use(Package(Context()), cond=False)
    u2 = Use(Package(Context()), cond=False)
    assert_equal(u1, u2)

def test_eq_options():
    u1 = Use(Package(Context()), options=None)
    u2 = Use(Package(Context()), options=True)
    assert_not_equal(u1, u2)
    u1 = Use(Package(Context()), options=None)
    u2 = Use(Package(Context()), options=False)
    assert_not_equal(u1, u2)
    u1 = Use(Package(Context()), options=None)
    u2 = Use(Package(Context()), options=None)
    assert_equal(u1, u2)
    u1 = Use(Package(Context()), options=False)
    u2 = Use(Package(Context()), options=False)
    assert_equal(u1, u2)
