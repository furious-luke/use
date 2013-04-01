import re, os, logging
import networkx as nx
from .Use import Use
from .Package import PackageBuilder
from .File import File

class Rules(object):

    def __init__(self):
        self._prog = None
        self._exps = []
        self._ops = []
        self.graph = nx.DiGraph()
        self._ph = 0
        self.packages = set()

    def compile(self, rules):
        all_exps = []
        for exp, op in rules.items():
            all_exps.append(exp)
            self._exps.append(exp)
            self._ops.append(op)
        self._prog = re.compile('(' + ')|('.join(all_exps) + ')')

    def match(self, path):
        match = self._prog.match(path)
        if match:
            return self._ops[match.lastindex - 1]
        else:
            return None

    def search(self):
        for dir_path, dir_names, file_names in os.walk('.'):
            for fn in file_names:
                path = os.path.join(dir_path, fn)
                op = self.match(path)
                srcs = File(path)
                if op:
                    self.graph.add_edge(srcs, self._placeholder(), operation=op, builder=None)

    def setup_packages(self):
        to_add = []
        for u, v, data in self.graph.edges_iter(data=True):
            op = data.get('operation')
            if op and op.has_packages():
                to_add.append((op, u))
        for op, u in to_add:
            for pkg in op.package_iter():
                self.graph.add_edge(pkg, u)
                self.packages.add(pkg)


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
