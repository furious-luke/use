import re, os, logging
import networkx as nx
from .Use import Use
from .File import File
from .Node import Node

##
##
##
class Placeholder(Node):

    def __init__(self, id):
        super(Placeholder, self).__init__()
        self.id = id

    def __repr__(self):
        return 'Placeholder(%d)'%self.id

##
##
##
class Graph(object):

    def __init__(self):
        self.rules = []
        self.chained_rules = {}
        self._prog = None
        self._re_rules = []
        self._graph = nx.DiGraph()
        self._ph = 0
        self.packages = set()

    def __repr__(self):
        return repr(self._graph)

    # ##
    # ## Add a rule to the graph.
    # ## @param[in] rule The rule to add.
    # ##
    # def add(self, rule):
    #     logging.debug('Adding rule: ' + str(rule))
    #     self.rules.append(rule)
    #     return rule

    def add_node(self, *args, **kwargs):
        return self._graph.add_node(*args, **kwargs)

    def has_node(self, *args, **kwargs):
        return self._graph.has_node(*args, **kwargs)

    def remove_node(self, *args, **kwargs):
        return self._graph.remove_node(*args, **kwargs)

    def add_edge(self, *args, **kwargs):
        return self._graph.add_edge(*args, **kwargs)

    def remove_edge(self, *args, **kwargs):
        return self._graph.remove_edge(*args, **kwargs)

    def first_child(self, node):
        children = self._graph.successors(node)
        if len(children):
            return children[0]
        return None

    def predecessors(self, *args, **kwargs):
        if kwargs:
            pred = []
            for edge in self._graph.in_edges_iter(*args):
                for k, v in kwargs.iteritems():
                    if self._graph.edge[edge[0]][edge[1]].get(k, None) == v:
                        pred.append(edge[0])
            return pred
        else:
            return self._graph.predecessors(*args, **kwargs)

    def successors(self, *args, **kwargs):
        if kwargs:
            succ = []
            for edge in self._graph.out_edges_iter(*args):
                for k, v in kwargs.iteritems():
                    if self._graph.edge[edge[0]][edge[1]].get(k, None) == v:
                        succ.append(edge[1])
            return succ
        else:
            return self._graph.successors(*args, **kwargs)

    ##
    ## Updating is a bit of a nasty. Because nodes in the graph may
    ## modify descendant connections we can't depend on a recursive
    ## method calling approach.
    ##
    def update(self):

        # Begin with a list of targets to process. By default
        # this is all leaf nodes.
        targets = []
        for node in self._graph.nodes_iter():
            if not self._graph.successors(node):
                targets.append(node)

        # Walk target dependencies, building a set of nodes
        # to be processed.
        to_build, to_build_set = _to_build(targets)

        # Begin processing each node.
        while len(to_build):
            node = to_build.pop(0)

            # Execute the node. This will return FROM HERE

        # Execute each target node to handle invalidation and
        # updating.
        for tgt in targets:
            tgt(self)

    def _to_build(self, targets):
        to_build = []
        to_build_set = set()
        for t in targets:
            _to_build_node(t, to_build, to_build_set)
        return to_build, to_build_set

    def _to_build_node(self, node, to_build, to_build_set):
        if node not in to_build_set:
            to_build.prepend(node)
            to_build_set.insert(node)
            for s in self.predecessors(source=True):
                _to_build_node(s, to_build, to_build_set)

    ##
    ## Prepare regular expressions for searching.
    ##
    def compile(self):
        all_exps = []
        for rule in self.rules:
            if isinstance(rule.source, str):
                logging.debug('Compiling regexp rule: ' + str(rule.source))
                all_exps.append(rule.source)
                self._re_rules.append(rule)
            else:
                for source_rule in rule.source:
                    logging.debug('Adding chained rule: ' + str(source_rule) + ' to ' + str(rule))
                    self.chained_rules.setdefault(source_rule, []).append(rule)
        self._prog = re.compile('(' + ')|('.join(all_exps) + ')')

    ##
    ## Match a path to a rule.
    ##
    def match(self, path):
        match = self._prog.match(path)
        if match:
            return self._re_rules[match.lastindex - 1]
        else:
            return None

    ##
    ## Try to fulfil all rules.
    ##
    def search(self):
        placeholders = {}
        for dir_path, dir_names, file_names in os.walk('.'):
            for fn in file_names:
                path = os.path.join(dir_path, fn)
                rule = self.match(path)
                if rule is None:
                    continue
                logging.debug('File ' + path + ' matches rule ' + str(rule))
                src = File(path)
                ph = placeholders.get(rule, None)
                if ph is None:
                    ph = self._placeholder()
                    placeholders[rule] = ph
                self._graph.add_node(src)
                self._graph.add_node(ph, rule=rule)
                self._graph.add_edge(src, ph, rule=rule)
                self._add_chained_rules(ph, rule, placeholders)

    ##
    ## Add packages to the graph.
    ##
    def setup_packages(self):
        to_add = []
        for u, v, data in self._graph.edges_iter(data=True):
            rule = data.get('rule')
            if rule and rule.use and rule.use.has_packages():
                to_add.append((rule.use, v))
        for use, v in to_add:
            for pkg in use.package_iter():
                self._graph.add_edge(pkg, v)
                self.packages.add(pkg)

    def build_packages(self):
        logging.debug('Building packages.')
        pkgs = list(self.packages)
        for pkg in pkgs:
            pkg.build()

    def targets(self):

        # By default get all nodes with no outgoing edges.
        targets = []
        for node in self._graph.nodes_iter():
            if not self._graph.successors(node):
                targets.append(node)
        return targets

    def production_rule(self, node):
        return self._graph.node[node].get('rule')

    def iter_source_edges(self, node):
        for edge in self._graph.in_edges_iter(node):
            data = self._graph.get_edge_data(*edge)
            rule = data.get('rule')
            if rule is not None:
                yield edge[0], edge[1], rule

    def iter_prior_edges(self, node):
        for edge in self._graph.in_edges_iter(node):
            data = self._graph.get_edge_data(*edge)
            rule = data.get('rule')
            if rule is None:
                yield edge[0], edge[1]

    def iter_sources(self, node):
        for edge in self.iter_source_edges(node):
            yield edge[0]

    def iter_priors(self, node):
        for edge in self.iter_prior_edges(node):
            yield edge[0]

    def iter_nodes(self):
        for node in self._graph.nodes_iter():
            data = self._graph.node[node]
            rule = data.get('rule')
            yield node, rule

    ##
    ## Expand nodes using packages. During the construction of the
    ## graph we didn't have enough information to know whether products
    ## should be individualised from sources, or whether they are
    ## combined. Now that the pacakges have been built we can go
    ## back and expand any incorrectly combined products.
    ##
    def post_package_expand(self):
        logging.debug('Expanding nodes.')
        targets = self.targets()
        logging.debug('Using targets: ' + str(targets))
        for target in targets:
            self._expand_node(target)

    def _expand_node(self, product_node):
        logging.debug('Looking at product node ' + str(product_node))
        sources = list(self.iter_sources(product_node))
        for src in sources:
            self._expand_node(src)
        rule = self.production_rule(product_node)
        if rule:
            self._do_expand_node(product_node, rule, sources)

    ##
    ## Do the work of actually expanding a node.
    ##
    def _do_expand_node(self, product_node, rule, sources):

        # Get hold of the real mappings from source nodes to
        # product nodes. This is general, the rule can return
        # any combination of sources to each product.
        priors = list(self.iter_priors(product_node))
        productions = rule.productions(sources)
        logging.debug('Replacing placeholder with expanded products.')
        logging.debug('Placeholder: ' + str(product_node))
        logging.debug('Productions: ' + str(productions))

        # Cache the incoming and outgoing edges prior to deleting
        # the original placeholder product node.
        out_edges = self._graph.out_edges(product_node)

        # Delete the original placeholder node all edges associated
        # with it.
        self._graph.remove_node(product_node)

        # Replace the incoming edges with new ones, and outgoing
        # edges.
        for sources, product in productions:
            for src in sources:
                self._graph.add_node(product)
                self._graph.add_edge(src, product)
            for edge in out_edges:
                self._graph.add_edge(product, edge[1])

            # Also add back in the priors.
            for prior in priors:
                self._graph.add_edge(prior, product)

    def draw_graph(self, path=None):
        path = 'plot.png'
        import matplotlib.pyplot as plt
        nx.draw_spring(self._graph)
        if path:
            plt.savefig(path)
        else:
            plt.show()

    def placeholder(self):
        self._ph += 1
        return Placeholder(self._ph - 1)

    ##
    ## Add chained rules to placeholder. Some rules will be given
    ## with another rule as the source, instead of a regular expression.
    ## In these cases we need to match the source rule against the
    ## the list of such rules and add the production.
    ##
    def _add_chained_rules(self, placeholder, source_rule, placeholders):
        chained_rules = self._get_chained_rules(source_rule)
        for rule in chained_rules:
            ph = placeholders.get(rule, None)
            if ph is None:
                ph = self._placeholder()
                placeholders[rule] = ph
            self._graph.add_node(ph, rule=rule)
            self._graph.add_edge(placeholder, ph, rule=rule)
            self._add_chained_rules(ph, rule, placeholders)

    def _get_chained_rules(self, source_rule):
        return self.chained_rules.get(source_rule, [])

# Declare a global graph object.
graph = Graph()
