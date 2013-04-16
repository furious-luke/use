from .Graph import graph

__all__ = ['rule', 'Rule', 'RuleList']

def rule(source, use, **kwargs):
    return graph.add(Rule(source, use, kwargs))

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
        self.source = source
        self.use = use
        self.options = options

    def __repr__(self):
        return str(self.source) + ' -> ' + str(self.use)

    def __add__(self, op):
        return RuleList(self, op)

    def productions(self, nodes):
        return self.use.productions(nodes, self.options)
