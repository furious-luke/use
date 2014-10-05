import argparse

class EnableAction(argparse.Action):
    
    def __init__(self, option_strings, dest, required=False, help=None, metavar=None, default=None):
        strings = []
        self.positive_strings = set()
        self.negative_strings = set()
        for string in option_strings:
            assert string.startswith('--enable') or string.startswith('--with')
            strings.append(string)
            self.positive_strings.add(string)
            neg_string = string.replace('--enable', '--disable')
            neg_string = neg_string.replace('--with', '--without')
            strings.append(neg_string)
            self.negative_strings.add(neg_string)
        super(EnableAction, self).__init__(
            option_strings=strings, dest=dest, const=None, default=default, type=bool,
            choices=None, required=required, help=help, metavar=metavar, nargs=0
        )

    def __call__(self, parser, namespace, value, option_string=None):
        if value is None or value == []:
            value = option_string in self.positive_strings
        elif option_string in self.negative_strings:
            value = not value
        setattr(namespace, self.dest, value)

class Arguments(object):

    def __init__(self, desc=None):
        self.parser = argparse.ArgumentParser(desc)
        self.dict = None
        self.args = type('', (object,), {})
        self._arg_map = {}
        self._ex_args = {}
        self._base_def = {}

    ##
    ## Add a new argument.
    ## NOTE: Need to have loaded any arguments by here.
    ##
    def __call__(self, *args, **kwargs):

        # Figure out the name to use.
        if 'dest' in kwargs:
            name = kwargs['dest']
        elif args[0].startswith('--enable-'):
            name = args[0][9:]
        elif args[0].startswith('--with-'):
            name = args[0][7:]
        elif args[0][:2] == '--':
            name = args[0][2:]
        else:
            name = args[0][1:]
        name = name.replace('-', '_')

        # Perform the addition.
        return self._add(name, list(args), kwargs)

    def parse(self):
        self.dict = self.parser.parse_args()

    def _add(self, name, args, kwargs):

        # Replace any default with None and store the default
        # for later.
        default = kwargs.pop('default', None)
        if default is None:
            if kwargs.get('action', None) == 'store_true':
                default = False
            elif kwargs.get('action', None) == 'store_false':
                default = True

        # Store the baseline default. This should not take into
        # account previous runs.
        self._base_def[name] = default

        # If there is already a value stored from last time,
        # make that the default.
        if name in self._ex_args:
            default = self._ex_args[name]

        # Augment the action if needed.
        if args[0].startswith('--enable-') or args[0].startswith('--with-'):
            kwargs['action'] = EnableAction
            if kwargs.get('dest', None) is None:
                kwargs['dest'] = name

        # Overwrite the shown default.
        kwargs['default'] = default

        # Add to the parser and cache the action.
        self._arg_map[name] = self.parser.add_argument(*args, **kwargs)
        setattr(self.args, name, self._arg_map[name])

        return self._arg_map[name]

    def save_data(self, args):
        data = {}
        for k, v in self._arg_map.iteritems():
            if v.default != getattr(args, k).default:
                data[k] = getattr(args, k)
        return data

    def load_data(self, data):
        self._ex_args = dict(data)

class Argument(object):

    def __init__(self, name, parent, use=None, kwargs={}):
        self.name = name
        self.parent = parent
        self.use = use
        self._kwargs = kwargs

    def __eq__(self, op):
        return ArgumentCheck('eq', self, op)

    def __and__(self, op):
        return ArgumentCheck('and', self, op)

    def __add__(self, op):
        return ArgumentCheck('add', self, op)

    def __deepcopy__(self, memo):
        # Don't actually deepcopy anything.
        return Argument(self.name, self.parent, self.use)

    def __str__(self):
        return str(self.value())

    def contains(self, op):
        return ArgumentCheck('in', self, op)

    def value(self):
        if self.use is None:
            return getattr(self.parent.dict, self.name)
        else:
            attr = getattr(self.use, self.name)
            if callable(attr):
                return attr(**self._kwargs)
            else:
                return attr

    def compare(self, op):
        return self.name == op.name and self.use == op.use

class ArgumentCheck(object):

    def __init__(self, op, left, right=None):
        self.op = op
        self.left = left
        self.right = right

    def __nonzero__(self):
        return bool(self.value())

    def __eq__(self, op):
        return self.compare(op)

    def __ne__(self, op):
        return not self.compare(op)

    def __and__(self, op):
        return ArgumentCheck('and', self, op)

    def __str__(self):
        assert self.op in ['add']
        return str(self.value())

    def value(self):
        left_val  = self.left.value()  if isinstance(self.left,  Argument) else self.left
        right_val = self.right.value() if isinstance(self.right, Argument) else self.right
        if self.op == 'eq':
            return left_val == right_val
        elif self.op == 'in':
            return right_val in left_val
        elif self.op == 'and':
            return right_val and left_val
        elif self.op == 'add':
            return left_val + right_val
        assert 0

    def compare(self, op):
        if self.op != op.op:
            return False
        if type(self.left) != type(op.left):
            return False
        if isinstance(self.left, (Argument, ArgumentCheck)):
            if not self.left.compare(op.left):
                return False
        elif self.left != op.left:
            return False
        if type(self.right) != type(op.right):
            return False
        if isinstance(self.right, (Argument, ArgumentCheck)):
            return self.right.compare(op.right)
        else:
            return self.right == op.right

    # def update_context(self, ctx):
    #     if isinstance(self.left, Argument):
    #         self.left.context = ctx
    #     if isinstance(self.right, Argument):
    #         self.right.context = ctx
