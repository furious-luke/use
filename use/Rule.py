import re, os
from .Graph import graph
from .Node import Node
from .File import File
from .conv import to_list
import logging

__all__ = ['rule', 'Rule', 'RuleList']

def rule(graph, source, use, **kwargs):

    # We must be able to locate the requested use already
    # in the graph.
    assert graph.has_node(use)

    # Create a new rule to encapsulate this.
    new_rule = Rule(source, use, kwargs)

    # Source can either be a regular expression, a list
    # of regular expressions or a RuleList. If we have a rule
    # list we add edges between the rules.
    if isinstance(source, RuleList):
        for src in source:
            graph.add_edge(src, new_rule)

    # Otherwise make sure we have a list and add the rule
    # as a node.
    else:
        new_rule.source = to_list(source)
#        graph.add_node(new_rule)

    # Add an edge from the use to this rule.
    graph.add_edge(use, new_rule)

    # Return the new rule object.
    return new_rule

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

class Rule(Node):

    def __init__(self, source, use, options=None):
        super(Rule, self).__init__()
        self.source = source
        self.use = use
        self.options = options

    def __repr__(self):
        return str(self.source) + ' -> ' + str(self.use)

    def __add__(self, op):
        return RuleList(self, op)

    def productions(self, nodes):
        return self.use.productions(nodes, self.options)

    ##
    ##
    ##
    def update(self, graph):

        # If our source is a string then locate any matching files.
        logging.debug('Rule: Looking at source %s'%self.source)
        for src in self.source:
            if isinstance(src, str):
                files = self.match_sources(src)
                for f in files:
                    graph.add_edge(File(f), self, source=True)

        # Run the expansion.
        self.expand(graph)

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

    ##
    ## Expand products. Rules begin with no products defined.
    ## There will be dependants that are marked as sources, which
    ## will be the recipients of the products.
    ##
    def expand(self, graph):

        # Get hold of dependants and sources.
        dependants = graph.successors(self, source=True)
        sources = graph.predecessors(self, source=True)

        # The Use knows how to convert the sources into productions.
        # A production is a transformation from source to product,
        # in the form of a tuple with three elements, a tuple of sources,
        # a builder, and a tuple of products.
        productions = self.use.expand(sources, self.options)

        # In preparation for inserting the productions, detach the
        # rule from sources and dependants.
        graph.remove_node(self)

        # Insert the productions.
        for prod in productions:

            # Add sources.
            for src in prod[0]:
                graph.add_edge(src, prod[1], source=True)

            # Add products.
            for pr in prod[2]:
                graph.add_edge(prod[1], pr, product=True)

            # Add the rule as a dependency of the builder.
            graph.add_edge(self, prod[1])
