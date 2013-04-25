import logging

class Node(object):

    def __init__(self):
        self._seen = False
        self._invalid = False

    def __repr__(self):
        return 'Node'

    ##
    ## Called to process this node.
    ##
    def __call__(self, graph):
        logging.debug('Called node ' + str(self))

        # If we've already processed this node don't do
        # so again.
        if self._seen:
            logging.debug('Already seen this node.')
            return self._invalid

        # Call out to our parents first.
        self._invalid = False
        parents = graph.predecessors(self)
        for par in parents:
            if par(graph):
                self._invalid = True
        if self._invalid:
            logging.debug('Parents are invalidated.')

        # If our parents are invalidated we must rebuild. If not,
        # check if we're invalidated in any other way.
        if not self._invalid:
            self._invalid = self.invalidated(graph)
            logging.debug('Set invalidated state to %s'%self._invalid)

        # If we are invalid perform an update.
        if self._invalid:
            self.update(graph)

        # Flag as seen.
        self._seen = True

        # Return our invalidation state.
        return self._invalid

    ##
    ## Determine if this node is invalidated.
    ##
    def invalidated(self, graph):
        return True

    ##
    ## Do what is needed to validate this node.
    ##
    def update(self, graph):
        logging.debug('Called update on node ' + str(self))

    ##
    ## Find the parent that produces this node. The method is
    ## that each product node may have only one producer. So,
    ## iterate over the incoming edges and return the 'from' node
    ## of the first one to be marked as a product edge.
    ##
    def producer(self, graph):
        for edge in graph.iter_incoming_edges(self):
            if edge[2].get('product'):
                return edge[0]
        return None
