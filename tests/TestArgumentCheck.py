from nose.tools import assert_equals
from use.Argument import *

class Context(object):
    def argument(self, name):
        return name

def test_init():
    ac = ArgumentCheck('add', 'l', 'r')
    assert_equals(ac.op, 'add')
    assert_equals(ac.left, 'l')
    assert_equals(ac.right, 'r')

def test_nonzero():
    ac = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac.__nonzero__(), False)
    ac = ArgumentCheck('eq', 'a', 'a')
    assert_equals(ac.__nonzero__(), True)

def test_eq():
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('eq', 'a', 'c')
    assert_equals(ac0 == ac1, False)
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0 == ac1, True)

def test_ne():
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('eq', 'a', 'c')
    assert_equals(ac0 != ac1, True)
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0 != ac1, False)

def test_and():
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('add', 'a', 'c')
    res = ac0 & ac1
    assert_equals(res.op, 'and')
    assert_equals(res.left, ac0)
    assert_equals(res.right, ac1)

def test_value_equal():
    ac = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac.value(), False)
    ac = ArgumentCheck('eq', 'a', 'a')
    assert_equals(ac.value(), True)

def test_value_in():
    ac = ArgumentCheck('in', ['b', 'c'], 'a')
    assert_equals(ac.value(), False)
    ac = ArgumentCheck('in', ['b', 'a'], 'a')
    assert_equals(ac.value(), True)

def test_value_and():
    ac = ArgumentCheck('and', False, False)
    assert_equals(ac.value(), False)
    ac = ArgumentCheck('and', False, True)
    assert_equals(ac.value(), False)
    ac = ArgumentCheck('and', True, False)
    assert_equals(ac.value(), False)
    ac = ArgumentCheck('and', True, True)
    assert_equals(ac.value(), True)

def test_value_add():
    ac = ArgumentCheck('add', 'a', 'b')
    assert_equals(ac.value(), 'ab')

def test_compare_op():
    ops = ['eq', 'in', 'and', 'add']
    for op0 in ops:
        ac0 = ArgumentCheck(op0, 'a', 'b')
        for op1 in ops:
            ac1 = ArgumentCheck(op1, 'a', 'b')
            assert_equals(ac0.compare(ac1), (op0 == op1))

def test_compare_left_type():
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('eq', 0, 'b')
    assert_equals(ac0.compare(ac1), False)
    ac0 = ArgumentCheck('eq', 0, 'b')
    ac1 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), True)

def test_compare_left_argument():
    arg = Argument('a', Context())
    ac1 = ArgumentCheck('eq', arg, 'b')
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    arg = Argument('a', Context())
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', arg, 'b')
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', arg, 'b')
    ac0 = ArgumentCheck('eq', arg, 'b')
    assert_equals(ac0.compare(ac1), True)

def test_compare_left_argument_check():
    arg = ArgumentCheck('add', 'c', 'd')
    ac1 = ArgumentCheck('eq', arg, 'b')
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    arg = Argument('a', Context())
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', arg, 'b')
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', arg, 'b')
    ac0 = ArgumentCheck('eq', arg, 'b')
    assert_equals(ac0.compare(ac1), True)

def test_compare_left_value():
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', 'c', 'b')
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', 'c', 'b')
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), True)

def test_compare_right_type():
    ac0 = ArgumentCheck('eq', 'a', 'b')
    ac1 = ArgumentCheck('eq', 'a', 0)
    assert_equals(ac0.compare(ac1), False)
    ac0 = ArgumentCheck('eq', 'a', 0)
    ac1 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    ac0 = ArgumentCheck('eq', 'a', 0)
    ac1 = ArgumentCheck('eq', 'a', 0)
    assert_equals(ac0.compare(ac1), True)

def test_compare_right_argument():
    arg = Argument('b', Context())
    ac1 = ArgumentCheck('eq', 'a', arg)
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    arg = Argument('a', Context())
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', 'a', arg)
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', 'a', arg)
    ac0 = ArgumentCheck('eq', 'a', arg)
    assert_equals(ac0.compare(ac1), True)

def test_compare_right_argument_check():
    arg = ArgumentCheck('add', 'c', 'd')
    ac1 = ArgumentCheck('eq', 'a', arg)
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    arg = Argument('a', Context())
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', 'a', arg)
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', 'a', arg)
    ac0 = ArgumentCheck('eq', 'a', arg)
    assert_equals(ac0.compare(ac1), True)

def test_compare_right_value():
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', 'a', 'c')
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', 'a', 'c')
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), False)
    ac1 = ArgumentCheck('eq', 'a', 'b')
    ac0 = ArgumentCheck('eq', 'a', 'b')
    assert_equals(ac0.compare(ac1), True)
