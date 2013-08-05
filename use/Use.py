from .Node import Node
from .Resolver import Resolver
from .utils import load_class, getarg

##
## Represents a package installation with options.
##
class Use(Node):

    def __init__(self, package, options={}):
        super(Use, self).__init__()
        self.package = package
        self.options = options if options is not None else {}
        self.selected = None

    def __repr__(self):
        text = 'use<' + repr(self.package)
        if self.options:
            text += ', ' + repr(self.options)
        text += '>'
        return text

    def __add__(self, op):
        return UseGroup(self, op, 'and')

    @property
    def found(self):
        return self.selected is not None

    def has_packages(self):
        return True

    def package_iter(self):
        yield self.package

    def make_options_dict(self, options):
        return self.selected.options().make_options_dict(options)

    def apply(self, prods, options={}):
        self.selected.apply(prods, self.options, options)

    def expand(self, nodes, options={}):
        return self.selected.expand(nodes, self.options, options)

##
##
##
class UseGroup(object):

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    @property
    def found(self):
        if self.op == 'and':
            return self.left.found and self.right.found
        elif self.op == 'or':
            return self.left.found or self.right.found
        return False

    def apply(self, prods):
        if self.op == 'and':
            self.left.apply(prods)
            self.right.apply(prods)
        elif self.op == 'or':
            if self.left.found:
                self.left.apply(prods)
            else:
                self.right.apply(prods)

    def expand(self, nodes, options):
        if self.op == 'and':
            prods = self.left.expand(nodes, options)
            if prods is None:
                prods = self.right.expand(nodes, options)
                if prods is not None:
                    self.left.apply(prods)
            else:
                self.right.apply(prods)

        elif self.op == 'or':
            if self.left.found:
                prods = self.left.expand(nodes, options)
            else:
                prods = self.right.expand(nodes, options)

        return prods
