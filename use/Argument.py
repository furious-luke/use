class Arguments(object):

    def __init__(self, ctx):
        self._ctx = ctx

    def __call__(self, *args, **kwargs):
        act = self._ctx.parser.add_argument(*args, **kwargs)
        new_arg = Argument(act.dest, self._ctx)
        setattr(self, new_arg.name, new_arg)
        return self

class Argument(object):

    def __init__(self, name, ctx):
        self.name = name
        self.context = ctx

    def __eq__(self, op):
        return ArgumentCheck('eq', self, op)

    def value(self):
        return getattr(self.context.arguments, self.name)

    def compare(self, op):
        return self.name == op.name

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
        else:
            return bool(left_val)

    def compare(self, op):
        if self.op != op.op:
            return False
        if type(self.left) != type(op.left):
            return False
        if isinstance(self.left, Argument):
            if not self.left.compare(op.left):
                return False
        elif self.left != op.left:
            return False
        if type(self.right) != type(op.right):
            return False
        if isinstance(self.right, Argument):
            if not self.right.compare(op.right):
                return False
        else:
            return self.right == op.right

    def update_context(self, ctx):
        if isinstance(self.left, Argument):
            self.left.context = ctx
        if isinstance(self.right, Argument):
            self.right.context = ctx
