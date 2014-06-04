from nose.tools import assert_equals
from use.Rule import *

def test_init():
    r = Rule('src', 'use', 'cond', 'opts')
    assert_equals(r.source, 'src')
    assert_equals(r.use, 'use')
    assert_equals(r.condition, 'cond')
    assert_equals(r.options, 'opts')
    assert_equals(r._src_nodes, [])
    assert_equals(r.product_nodes, [])
    assert_equals(r.productions, [])

# TODO
def test_equality():
    pass
