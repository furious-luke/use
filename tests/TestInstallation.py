import json
from nose.tools import *
from use.Package import Installation
from use.Location import Location

class Package(object):
    pass

class Version(object):
    package = Package

def test_save_data():
    loc = Location('/a', 'b', 'c', 'd')
    inst = Installation(Version(), loc, binaries=['a'], headers=['b'], libraries=['c'])
    inst._ftr_map['ftr'] = 'test'
    data = inst.save_data()
    assert_equals(data['version'], str(Version().__class__))
    assert_equals(data['location'], json.dumps(loc.__dict__))
    assert_equals(data['binaries'], json.dumps(['a']))
    assert_equals(data['headers'], json.dumps(['b']))
    assert_equals(data['libraries'], json.dumps(['c']))
    assert_equals(data['features'], json.dumps(['ftr']))

def test_load_data():
    loc = Location('/a', 'b', 'c', 'd')
    inst = Installation(Version(), loc, binaries=['a'], headers=['b'], libraries=['c'])
    inst._ftr_map['ftr'] = 'test'
    data = inst.save_data()
    inst = Installation(data)
    assert_equals(inst.version.__class__, Version().__class__)
    assert_equals(inst.location.__dict__, loc.__dict__)
    assert_equals(inst._bins, ['a'])
    assert_equals(inst._hdrs, ['b'])
    assert_equals(inst._libs, ['c'])
    assert_equals(inst._ftr_map.keys(), ['ftr'])
