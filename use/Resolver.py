from .Node import Node

##
## Resolve which packages will be used. When searching
## for packages there will likely be several options for
## many. The Resolver's job is to determine which of the
## packages may work in tandem and update all Use objects
## to reflect this selection. This will be a compilcated
## operation, generally, as it will depend on what options
## each use has requested of the same package and also
## what dependencies each package is built against.
##
class Resolver(Node):

    def __init__(self):
        super(Resolver, self).__init__()

    def __repr__(self):
        return 'Resolver'

    ##
    ## Resolve the graph. The graph must have had its
    ## packages built.
    ## @param[in] graph The graph to resolve.
    ##
    def update(self, graph):

        # Need to build a dictionary from packages to uses.
        pkg_uses = self._make_pkg_uses(graph)

        # TODO: Make less shitty.
        # Pick the first available version.
        for pkg, uses in pkg_uses.items():
            for use in uses:
                use.selected = list(pkg.iter_installations())[0]

    ##
    ##
    ##
    def _make_pkg_uses(self, graph):
        pkg_uses = {}
        for node, rule in graph.iter_nodes():
            if rule is None:
                continue
            pkg_uses.setdefault(rule.use.package, set()).add(rule.use)
        return pkg_uses

