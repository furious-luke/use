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
        self._src_crcs = None

    def __eq__(self, op):
        return repr(self) == repr(op)

    def __ne__(self, op):
        return not self.__eq__(op)

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

        # If any of my sources are invalidated then I must be so. However
        # this is already checked in build.

        # Compare CRCs of sources to those I have stored.
        if self.builder:
            old_src_crcs = ctx.node_source_crcs(self)
            if old_src_crcs is None:
                return True
            for src in self.builder.dependent_nodes:
                if src.builder is None:
                    crc = old_src_crcs.get(repr(src), None)
                    if crc is None or crc != src.current_crc(ctx):
                        return True

            # Also check if the builder has changed.
            if hasattr(ctx, 'old_bldrs'):
                old_bldr = ctx.old_bldrs.get(repr(self), None)
                if old_bldr is None or self.builder != old_bldr:
                    return True

        return False

    ##
    ## Do what is needed to validate this node.
    ##
    def update(self, ctx):
        logging.debug('Node: Updating node: ' + str(self))

        if self.builder:
            self.builder.update(ctx)

        logging.debug('Node: Done updating node: ' + str(self))

    def update_source_crcs(self, ctx):
        if self.builder:
            self._src_crcs = {}
            for src in self.builder.dependent_nodes:
                if src.builder is None:
                    self._src_crcs[repr(src)] = src.current_crc(ctx)
        else:
            self._src_crcs = None

    def current_source_crcs(self, ctx):
        if self._src_crcs is None:
            self.update_source_crcs(ctx)
        return self._src_crcs
