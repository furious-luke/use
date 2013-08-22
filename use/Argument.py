class Arguments(object):

    def __init__(self, ctx):
        self._ctx = ctx

    def __call__(self, *args, **kwargs):

        # Replace any default with None and store the default
        # for later.
        default = kwargs.pop('default', None)
        kwargs['default'] = None
        if default is None:
            if kwargs.get('action', None) == 'store_true':
                default = False
            elif kwargs.get('action', None) == 'store_false':
                default = True

        # Create the argument to get hold of destination name.
        act = self._ctx.parser.add_argument(*args, **kwargs)

        # Set the default.
        self._ctx._def_args[act.dest] = default

        new_arg = Argument(act.dest, self._ctx)
        setattr(self, new_arg.name, new_arg)
        return self

class Argument(object):

    def __init__(self, name, ctx, use=None):
        self.name = name
        self.context = ctx
        self.use = use

    def __eq__(self, op):
        return ArgumentCheck('eq', self, op)

    def __deepcopy__(self, memo):
        return Argument(self.name, self.context, self.use)

    def __add__(self, op):
        return ArgumentCheck('add', self, op)

    def __str__(self):
        return self.value()

    def contains(self, op):
        return ArgumentCheck('in', self, op)

    def value(self):
        if self.use is None:
            return self.context.argument(self.name)
        else:
            return getattr(self.use, self.name)

    def compare(self, op):
        return self.name == op.name and self.use == op.use

class ArgumentCheck(object):

    def __init__(self, op, left, right=None):
        self.op = op
        self.left = left
        self.right = right

    def __nonzero__(self):
        left_val = self.left.value() if isinstance(self.left, Argument) else self.left
        if self.op == 'eq':
            right_val = self.right.value() if isinstance(self.right, Argument) else self.right
            return left_val == right_val
        elif self.op == 'in':
            right_val = self.right.value() if isinstance(self.right, Argument) else self.right
            return right_val in left_val
        assert 0

    def __eq__(self, op):
        return self.compare(op)

    def __ne__(self, op):
        return not self.compare(op)

    def __str__(self):
        assert self.op in ['add']
        return str(self.value())

    def value(self):
        left_val = self.left.value() if isinstance(self.left, Argument) else self.left
        right_val = self.right.value() if isinstance(self.right, Argument) else self.right
        if self.op == 'add':
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
            if not self.right.compare(op.right):
                return False
        else:
            return self.right == op.right

    def update_context(self, ctx):
        if isinstance(self.left, Argument):
            self.left.context = ctx
        if isinstance(self.right, Argument):
            self.right.context = ctx
