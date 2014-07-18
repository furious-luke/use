import json
from nose.tools import *
from use.Use import Use
from use.Package import Package, Installation
from use.Options import OptionDict

class Context(object):
    pass

class OtherPackage(Package):
    pass

class Version(object):
    pass

class Location(object):
    def __init__(self):
        self.one = '1'
        self.two = '2'

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

def test_save_data():
    opts = OptionDict(test='value')
    inst = Installation(Version(), Location())
    use = Use(Package(Context()), options=opts)
    use.selected = inst
    data = use.save_data()
    assert_equals(data['package'], str(Package(Context()).__class__))
    assert_equals(data['installation'], json.dumps(inst.save_data()))
    assert_equals(data['options'], json.dumps(opts.get()))
