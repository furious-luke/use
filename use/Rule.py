import re, os
from .Node import Node
from .File import File
from .conv import to_list
import logging

__all__ = ['Rule', 'RuleList']

class RuleList(object):

    def __init__(self, *args):
        self._rules = list(args)
        self._expand()

    def __add__(self, op):
        return RuleList(self, op)

    def __iter__(self):
        return self._rules.__iter__()

    def __repr__(self):
        return str(self._rules)

    def _expand(self):
        rules = []
        for r in self._rules:
            if isinstance(r, RuleList):
                rules.extend(r._rules)
            else:
                rules.append(r)

class Rule(object):

    def __init__(self, source, use, options=None):
        super(Rule, self).__init__()
        self.source = source
        self._src_nodes = []
        self.product_nodes = []
        self.productions = []
        self.use = use
        self.options = options

    @property
    def source_nodes(self):
        nodes = sum([r.product_nodes for r in self.source if isinstance(r, Rule)], [])
        return self._src_nodes + nodes

    def __repr__(self):
        return str(self.source) + ' -> ' + str(self.use)

    def __add__(self, op):
        return RuleList(self, op)

    ##
    ## Scan for files.
    ##
    def scan(self, ctx):
        for src in self.source:
            logging.debug('Rule: Looking at source %s'%repr(self.source))

            # If our source is a string then locate any matching files.
            if isinstance(src, basestring):
                files = self.match_sources(src)
                self._src_nodes = [File(f) for f in files]

    ##
    ## Expand products. Rules begin with no products defined.
    ## There will be dependants that are marked as sources, which
    ## will be the recipients of the products.
    ##
    def expand(self, ctx):
        logging.debug('Rule: Expanding rule: %s'%repr(self))

        # The Use knows how to convert the sources into productions.
        # A production is a transformation from source to product,
        # in the form of a tuple with three elements, a tuple of sources,
        # a builder, and a tuple of products.
        self.productions = self.use.expand(self.source_nodes, self.options)
        logging.debug('Rule: Have productions: %s'%repr(self.productions))

        # Cache product nodes.
        self.product_nodes = sum([list(d) for s, b, d in self.productions], [])

        # Scan product nodes and update the source nodes with
        # product nodes and update product nodes with rules.
        for srcs, bldr, dsts in self.productions:
            for src in srcs:
                src.products = dsts
            for dst in dsts:
                dst.rule = self
                dst.builder = bldr

        logging.debug('Rule: Done expanding rule.')

    def match_sources(self, expr):
        logging.debug('Rule: Matching files.')

        # Compile the regular expression.
        prog = re.compile(expr)

        # Scan everything.
        srcs = []
        for dir_path, dir_names, file_names in os.walk('.'):
            for fn in file_names:
                path = os.path.join(dir_path, fn)
                match = prog.match(path)
                if match:
                    srcs.append(path)

        logging.debug('Rule: Found %s'%srcs)
        return srcs
