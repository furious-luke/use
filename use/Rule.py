from .Graph import graph
from .Node import Node
from .conv import to_list

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
