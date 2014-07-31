import argparse
from nose.tools import *
from use.Argument import Arguments

def test_init():
    args = Arguments()
    assert_equal(args._raw_args, [])
    assert_equal(args._ex_args, {})

def test_call():
    args = Arguments()
    args('--test', help='hello')
    args('--other', dest='blah')
    assert_equal(args._raw_args, [
        ('test', ['--test'], {'help': 'hello'}),
        ('blah', ['--other'], {'dest': 'blah'})
    ])

def test_add_to_parser():
    args = Arguments()
    args('--test', help='hello')
    args('--other', dest='blah')
    parser = argparse.ArgumentParser()
    args.add_to_parser(parser)
    res = parser.parse_args('--test a --other b'.split())
    assert_equal(res.test, 'a')
    assert_equal(res.blah, 'b')
    assert_equal(args._base_def, {'test': None, 'blah': None})
    assert_equal(hasattr(args, 'test'), True)
    assert_equal(hasattr(args, 'blah'), True)

def test_add_to_parser_defaults():
    args = Arguments()
    args('-a', default='blah')
    args('-b', action='store_true')
    args('-c', action='store_false')
    parser = argparse.ArgumentParser()
    args.add_to_parser(parser)
    assert_equal(args._base_def, {'a': 'blah', 'b': False, 'c': True})
    assert_equal(args._arg_map['a'].default, 'blah')
    assert_equal(args._arg_map['b'].default, False)
    assert_equal(args._arg_map['c'].default, True)

def test_add_to_parser_loaded_defaults():
    args = Arguments()
    args('-a', default='blah')
    args('-b', action='store_true')
    args('-c', action='store_false')
    args._ex_args = {'a': 'hello', 'b': True, 'c': False}
    parser = argparse.ArgumentParser()
    args.add_to_parser(parser)
    assert_equal(args._base_def, {'a': 'blah', 'b': False, 'c': True})
    assert_equal(args._arg_map['a'].default, 'hello')
    assert_equal(args._arg_map['b'].default, True)
    assert_equal(args._arg_map['c'].default, False)

def test_add_to_parser_enable():
    args = Arguments()
    args('--enable-a', default=True)
    args('--enable-b')
    args('--with-c', default=False)
    parser = argparse.ArgumentParser()
    args.add_to_parser(parser)
    assert_equal(args._arg_map['a'].option_strings, ['--enable-a', '--disable-a'])
    assert_equal(args._arg_map['a'].dest, 'a')
    assert_equal(args._arg_map['a'].default, True)
    assert_equal(args._arg_map['a'].const, None)
    assert_equal(args._arg_map['b'].option_strings, ['--enable-b', '--disable-b'])
    assert_equal(args._arg_map['b'].dest, 'b')
    assert_equal(args._arg_map['b'].default, None)
    assert_equal(args._arg_map['b'].const, None)
    assert_equal(args._arg_map['c'].option_strings, ['--with-c', '--without-c'])
    assert_equal(args._arg_map['c'].dest, 'c')
    assert_equal(args._arg_map['c'].default, False)
    assert_equal(args._arg_map['c'].const, None)
    res = parser.parse_args('--disable-a --enable-b'.split())
    assert_equal(res.a, False)
    assert_equal(res.b, True)
    assert_equal(res.c, False)

# def test_add_to_parser_load_enable():
#     args = Arguments()
#     args('--enable-a', action='store_true', default=True)
#     args('--enable-b', action='store_true')
#     args._ex_args = {'a': False, 'b': True}
#     parser = argparse.ArgumentParser()
#     args.add_to_parser(parser)
#     assert_equal(args._arg_map['a'].dest, 'a')
#     assert_equal(args._arg_map['a'].default, False)
#     assert_equal(args._arg_map['a'].const, True)
#     assert_equal(args._arg_map['a'].option_strings, ['--enable-a'])
#     assert_equal(args._arg_map['b'].dest, 'b')
#     assert_equal(args._arg_map['b'].default, True)
#     assert_equal(args._arg_map['b'].const, False)
#     assert_equal(args._arg_map['b'].option_strings, ['--disable-b'])
