from nose.tools import *
from use.utils import *

class SomeClass(object):
    pass

def test_split_class():
    path = str(SomeClass().__class__)
    mod, cls = split_class(path)
    assert_equal(mod, 'TestUtils')
    assert_equal(cls, 'SomeClass')
