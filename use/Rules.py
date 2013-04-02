import re, os, logging
import networkx as nx
from .Use import Use
from .Package import PackageBuilder
from .File import File

__all__ = ['rule', 'rules']

rules = RuleManager()

def rule(source, use, **kwargs):
    return rules.add(Rule(source, use, kwargs))

class Rule(object):

    def __init__(self, source, use, options=None):
        self.source = source
        self.use = use
        self.options = options

class RuleManager(object):

    def __init__(self):
        self.rules = []
        self.chained_rules = {}
        self._prog = None
        self._re_rules = []
        self.graph = nx.DiGraph()
        self._ph = 0
        self.packages = set()

    def add(self, rule):
        self.rules.append(rule)

    def compile(self, rules):
        all_exps = []
        for rule in self.rules:
            if isinstance(rule.source, str):
                all_exps.append(exp)
                self._re_rules.append(rule)
            else:
                for source_rule in rule.source:
                    self.chained_rules.setdefault(source_rule, []).append(rule)
        self._prog = re.compile('(' + ')|('.join(all_exps) + ')')

    def match(self, path):
        match = self._prog.match(path)
        if match:
            return self._re_rules[match.lastindex - 1]
        else:
            return None

    def search(self):
        for dir_path, dir_names, file_names in os.walk('.'):
            for fn in file_names:
                path = os.path.join(dir_path, fn)
                rule = self.match(path)
                srcs = File(path)
                ph = self._placeholder()
                self.graph.add_edge(srcs, ph, rule=rule, builder=None)
                self._add_chained_rules(ph, rule)

    def setup_packages(self):
        to_add = []
        for u, v, data in self.graph.edges_iter(data=True):
            rule = data.get('rule')
            if rule.use and rule.use.has_packages():
                to_add.append((rule.use, u))
        for use, u in to_add:
            for pkg in use.package_iter():
                self.graph.add_edge(pkg, u)
                self.packages.add(pkg)

    def targets(self):
        return []

    def linearise(self, targets):
        return []

    def build_packages(self):
        logging.debug('Building packages.')
        pkgs = list(self.packages)
        for pkg in pkgs:
            pkg.build()

    def draw_graph(self, path=None):
        import matplotlib.pyplot as plt
        nx.draw(self.graph)
        if path:
            plt.savefig(path)
        else:
            plt.show()

    def _placeholder(self):
        self._ph += 1
        return self._ph - 1

    ##
    ## Add chained rules to placeholder. Some rules will be given
    ## with another rule as the source, instead of a regular expression.
    ## In these cases we need to match the source rule against the
    ## the list of such rules and add the production.
    ##
    def _add_chained_rules(self, placeholder, source_rule):
        chained_rules = self._get_chained_rules(source_rule)
        for rule in chained_rules:
            ph = self._placeholder()
            self.graph.add_edge(placeholder, ph, rule=rule, builder=None)
            self._add_chained_rules(ph, rule)

    def _get_chained_rules(self, source_rule):
        return self.chained_rules.get(source_rule, [])
