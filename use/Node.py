import logging
from .Validatable import Validatable

class Node(Validatable):

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.rule = None
        self.builder = None
        self.products = []
        self._seen = False
        self._invalid = False

    def __repr__(self):
        return 'Node'

    ##
    ## Called to process this node.
    ##
    def build(self, ctx):
        logging.debug('Node: Building node: ' + str(self))

        # If we've already processed this node don't do
        # so again.
        if self._seen:
            logging.debug('Node: Already seen this node.')
            return self._invalid

        # Call out to our parents first.
        if self.builder:
            self._invalid = self.builder.build_sources(ctx)
            if self._invalid:
                logging.debug('Node: Parents are invalidated.')

        # If our parents are invalidated we must rebuild. If not,
        # check if we're invalidated in any other way.
        if not self._invalid:
            self._invalid = self.invalidated(ctx)
            logging.debug('Node: Set invalidated state to %s'%self._invalid)

        # If we are invalid perform an update.
        if self._invalid:
            self.update(ctx)

        # Flag as seen.
        self._seen = True

        # Return our invalidation state.
        logging.debug('Node: Done building node: ' + str(self))
        return self._invalid

    ##
    ## Determine if this node is invalidated.
    ##
    def invalidated(self, ctx):
        return True

    ##
    ## Do what is needed to validate this node.
    ##
    def update(self, ctx):
        logging.debug('Node: Updating node: ' + str(self))

        if self.builder:
            self.builder.update(ctx)

        logging.debug('Node: Done updating node: ' + str(self))
