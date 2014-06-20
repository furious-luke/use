from nose.tools import *
from use.Rule import Rule

class OtherRule(Rule):
    pass

def test_init():
    r = Rule('src', 'use', 'cond', 'opts')
    assert_equals(r.source, 'src')
    assert_equals(r.use, 'use')
    assert_equals(r.condition, 'cond')
    assert_equals(r.options, 'opts')
    assert_equals(r._src_nodes, [])
    assert_equals(r.product_nodes, [])
    assert_equals(r.productions, [])

def test_eq_type():
    r1 = Rule('a', 'use')
    r2 = Rule('a', 'use')
    assert_equal(r1, r2)
    r2 = OtherRule('a', 'use')
    assert_not_equal(r1, r2)

def test_eq_source():
    r1 = Rule('a', 'use')
    r2 = Rule('a', 'use')
    assert_equal(r1, r2)
    r2 = Rule('b', 'use')
    assert_not_equal(r1, r2)

def test_eq_use():
    r1 = Rule('a', 'use')
    r2 = Rule('a', 'use')
    assert_equal(r1, r2)
    r2 = Rule('a', 'use2')
    assert_not_equal(r1, r2)

def test_eq_condition():
    r1 = Rule('a', 'use', cond='d')
    r2 = Rule('a', 'use', cond='d')
    assert_equal(r1, r2)
    r2 = Rule('a', 'use', cond='e')
    assert_not_equal(r1, r2)

def test_eq_options():
    r1 = Rule('a', 'use', options='d')
    r2 = Rule('a', 'use', options='d')
    assert_equal(r1, r2)
    r2 = Rule('a', 'use', options='e')
    assert_not_equal(r1, r2)
