class Node(object):

    def __init__(self):
        self.invalidated = False

    ##
    ## Called to process this node.
    ##
    def __call__(self, graph):
        if self.invalidated:
            self.update(graph)

    ##
    ## Do what is needed to validate this node.
    ##
    def update(self, graph):
        pass

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
