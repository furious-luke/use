from nose.tools import *
from use.Rule import Rule, match_rules
from use.Use import Use
from use.Package import Package

class OtherRule(Rule):
    pass

class OtherPackage(Package):
    pass

def test_init():
    r = Rule('src', 'use', 'cond', 'opts')
    assert_equals(r.sources, ['src'])
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

def test_eq_sources():
    r1 = Rule('a', 'use')
    r2 = Rule('a', 'use')
    assert_equal(r1, r2)
    r2 = Rule('b', 'use')
    assert_not_equal(r1, r2)
    r1 = Rule(['a', 'b', 'c'], 'use')
    r2 = Rule(['a', 'b', 'c'], 'use')
    assert_equal(r1, r2)
    r2 = Rule(['a', 'c', 'd'], 'use')
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

def test_match_rules_empty():
    assert_equal(match_rules([], []), {})

def test_match_rules_different_sizes():
    assert_equal(match_rules([], ['a']), None)
    assert_equal(match_rules(['a'], []), None)
    assert_equal(match_rules(['a'], ['a', 'b']), None)
    assert_equal(match_rules(['a', 'b'], ['a']), None)

def test_match_rules_in_order():
    use = Use(Package(None))
    r1 = Rule([], use)
    r2 = Rule([], use)
    assert_equal(match_rules([r1], [r2]), {r1: r2})
    r3 = Rule([], use)
    r4 = Rule([], use)
    assert_equal(match_rules([r1, r3], [r2, r4]), {r1: r2, r3: r4})

def test_match_rules_out_of_order():
    use1 = Use(Package(None))
    use2 = Use(OtherPackage(None))
    r1 = Rule([], use1)
    r2 = Rule([], use2)
    r3 = Rule([], use2)
    r4 = Rule([], use1)
    assert_equal(match_rules([r1, r3], [r2, r4]), {r1: r4, r3: r2})

def test_match_rules_no_match():
    use1 = Use(Package(None))
    use2 = Use(OtherPackage(None))
    r1 = Rule([], use1)
    r2 = Rule([], use1)
    r3 = Rule([], use1)
    r4 = Rule([], use2)
    assert_equal(match_rules([r1, r3], [r2, r4]), None)

def test_match_rules_sources():
    use1 = Use(Package(None))
    use2 = Use(OtherPackage(None))
    r1 = Rule([], use1)
    r2 = Rule([], use1)
    r3 = Rule([r1], use1)
    r4 = Rule([r2], use1)
    assert_equal(match_rules([r3], [r4]), {r1: r2, r3: r4})
    r2 = Rule([], use2)
    r4 = Rule([r2], use1)
    assert_equal(match_rules([r3], [r4]), None)
