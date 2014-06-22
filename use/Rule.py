import re, os
from collections import Counter
from .Node import Node
from .File import File
from .conv import to_list
from .utils import conditions_equal
import logging

__all__ = ['Rule', 'RuleList', 'match_rules']

def are_rules_compatible(x, y):
    if isinstance(x, Rule):
        if isinstance(y, Rule):
            return x.is_compatible(y)
        else:
            return False
    elif isinstance(y, Rule):
        return False
    else:
        return True

def match_rules(rules, ex_rules):
    if len(rules) != len(ex_rules):
        return None
    if len(rules) == 0:
        return {}
    rule = rules[0]
    for ii in range(len(ex_rules)):
        mapping = {}
        ex_rule = ex_rules[ii]
        if are_rules_compatible(rule, ex_rule):
            src_res = match_rules(rule.sources, ex_rule.sources)
            if src_res is None:
                continue
            ext_res = match_rules(rules[1:], ex_rules[:ii] + ex_rules[ii + 1:])
            if ext_res is None:
                continue
            mapping[rule] = ex_rule
            mapping.update(ext_res)
            mapping.update(src_res)
            return mapping
    return None

class RuleList(object):

    def __init__(self, *args):
        self._rules = list(args)
        self._expand()

    def __eq__(self, op):
        for rule in self._rules:
            if rule not in op._rules:
                return False
        return True

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

    def __init__(self, sources, use, cond=None, options={}):
        super(Rule, self).__init__()
        self.condition = cond
        self.sources = to_list(sources)
        self._src_nodes = []
        self.product_nodes = []
        self.productions = []
        self.use = use
        self.options = options

    def __eq__(self, op):
        if type(self) != type(op):
            return False
        elif Counter(self.sources) != Counter(op.sources):
            return False
        elif self.use != op.use:
            return False
        elif not conditions_equal(self.condition, op.condition):
            return False
        elif self.options != op.options:
            return False
        else:
            return True

    def __ne__(self, op):
        return not self.__eq__(op)

    @property
    def source_nodes(self):
        if isinstance(self.source, Rule):
            nodes = self.source.product_nodes
        elif isinstance(self.source, RuleList):
            nodes = sum([r.product_nodes for r in self.source if isinstance(r, Rule)], [])
        else:
            nodes = []
        return self._src_nodes + nodes

    @property
    def nodes(self):
        return self.source_nodes + self.product_nodes

    # def __repr__(self):
    #     return str(self.source) + ' -> ' + str(self.use)

    def __add__(self, op):
        return RuleList(self, op)

    def is_compatible(self, other):
        if self.use != other.use:
            return False
        return self.use.is_compatible(other.use, self.options)

    ##
    ## Scan for files.
    ##
    def find_sources(self, ctx):
        logging.debug('Rule: Looking at source %s'%repr(self.source))

        # If our source is a string then locate any matching files.
        if isinstance(self.source, basestring):
            files = self.match_sources(self.source)
            self._src_nodes = [ctx.file(f) for f in files]

    def scan(self, ctx):
        logging.debug('Rule: Scanning for dependencies.')
        for srcs, bldr, dsts in self.productions:
            for src in srcs:
                logging.debug('Rule: Scanning: ' + str(src))
                src.scan(ctx, bldr)
        logging.debug('Rule: Done scanning for dependencies.')

    ##
    ## Expand products. Rules begin with no products defined.
    ## There will be dependants that are marked as sources, which
    ## will be the recipients of the products.
    ##
    def expand(self, ctx):
        logging.debug('Rule: Expanding rule: %s'%repr(self))

        # Only perform expansion if the rule is enabled.
        if self.condition is None or bool(self.condition):

            # The Use knows how to convert the sources into productions.
            # A production is a transformation from source to product,
            # in the form of a tuple with three elements, a tuple of sources,
            # a builder, and a tuple of products.
            self.productions = self.use.expand(self.source_nodes, self.options)
            if self.productions is None:
                self.productions = []
            logging.debug('Rule: Have productions: %s'%repr(self.productions))

            # Cache product nodes.
            self.product_nodes = sum([list(d) for s, b, d in self.productions], [])

            # Scan product nodes and update the source nodes with
            # product nodes and update product nodes with rules.
            for srcs, bldr, dsts in self.productions:
                for src in srcs:
                    src.products.extend(dsts)
                    assert src not in dsts, 'A production rule has resulted in a product that depends on itself: %s'%(str(self))
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
        for dir_path, dir_names, file_names in os.walk('.', followlinks=True):
            for fn in file_names:
                path = os.path.join(dir_path, fn)
                path = path[2:]
                match = prog.match(path)
                if match:
                    try:
                        with open(path, 'r') as file:
                            srcs.append(path)
                    except:
                        pass

        logging.debug('Rule: Found %s'%srcs)
        return srcs
