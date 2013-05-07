from .Node import Node
import logging

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
        logging.debug('Resolving package installations.')

        # Get the source installations.
        sources = graph.predecessors(self, source=True)
        dependants = graph.successors(self, source=True)
        logging.debug('Resolver: installations: %s'%sources)
        logging.debug('Resolver: uses: %s'%dependants)

        # If no sources return.
        if not sources:
            return

        # Totally shit, but pick the first and apply to all dependants.
        for dep in dependants:
            dep.selected = sources[0]
