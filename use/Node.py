import logging, threading
from .Validatable import Validatable

class Node(Validatable):

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__()
        self.rule = None
        self.builder = None
        self.products = []
        self.dependencies = []
        self.progenitors = []
        self.scanner = None
        self.seen = False
        self._invalid = False
        self._src_crcs = None
        self._done_scan = False
        self._job_done = False
        self._in_queue = False
        self._lock = threading.Lock()

    def __eq__(self, op):
        return repr(self) == repr(op)

    def __ne__(self, op):
        return not self.__eq__(op)

    def __repr__(self):
        return 'Node'

    def make_jobs(self, ctx):
        logging.debug('Node: Creating job for: ' + str(self))

        # If we've already processed this node don't do
        # so again.
        if self.seen:
            logging.debug('Node: Already seen this node.')
            return

        self.seen = True

        # If there are any dependencies, call them and skip myself.
        if (self.builder and self.builder.sources) or self.dependencies:
            logging.debug('Node: Have dependences/sources.')
            if self.builder:
                for src in self.builder.sources:
                    src.make_jobs(ctx)
            for dep in self.dependencies:
                dep.make_jobs(ctx)
            self.seen = True
            return

        # Add to job queue.
        self._in_queue = True
        ctx.job(self)

    def build_job(self, ctx):
        logging.debug('Node: Building job: ' + str(self))

        # Grab validity of sources.
        if self.builder:
            for src in self.builder.sources:
                if src._invalid:
                    self._invalid = True
                    logging.debug('Node: Parents are invalidated.')
                    break

        # Calculate my validity.
        if not self._invalid:
            self._invalid = self.invalidated(ctx)
            logging.debug('Node: Is invalidated: ' + str(self._invalid))

        if self._invalid:
            self.invalidate_progenitors(ctx)
            self.update(ctx)

        self._job_done = True

        for n in self.products:
            n.ready_check(ctx)
        for n in self.progenitors:
            n.ready_check(ctx)

    def ready_check(self, ctx):
        self._lock.acquire()
        logging.debug('Node: ' + str(self) + ': Checking if ready.')

        # Don't do anything if we've already been processed, or
        # if we're already in the queue.
        if self._job_done or self._in_queue:
            self._lock.release()
            logging.debug('Node: ' + str(self) + ': Already done/in queue.')
            return

        # Can only process this node if all dependencies are done.
        if self.builder:
            for src in self.builder.sources:
                if not src._job_done:
                    self._lock.release()
                    logging.debug('Node: ' + str(self) + ': Sources not built.')
                    return
        for dep in self.dependencies:
            if not dep._job_done:
                self._lock.release()
                logging.debug('Node: ' + str(self) + ': Dependencies not built: ' + str(dep))
                return

        # Send new job to job queue.
        logging.debug('Node: ' + str(self) + ': Sending to job queue.')
        self._in_queue = True
        self._lock.release()
        ctx.job(self)

    ##
    ## Called to process this node.
    ##
    def build(self, ctx):
        logging.debug('Node: Building node: ' + str(self))

        # If we've already processed this node don't do
        # so again.
        if self.seen:
            logging.debug('Node: Already seen this node.')
            return self._invalid

        # Call out to our parents first.
        if self.builder:
            self._invalid = self.builder.build_sources(ctx)
            if self._invalid:
                logging.debug('Node: Parents are invalidated.')

        # Build our dependencies.
        invalid = self.build_dependencies(ctx)
        if invalid:
            self._invalid = invalid
            logging.debug('Node: Dependencies are invalidated.')

        # If our parents are invalidated we must rebuild. If not,
        # check if we're invalidated in any other way.
        if not self._invalid:
            self._invalid = self.invalidated(ctx)
            logging.debug('Node: Set invalidated state to %s'%self._invalid)

        # If we are invalid perform an update.
        if self._invalid:

            # Flag all other nodes dependent on this one that
            # they are now invalidated.
            self.invalidate_progenitors(ctx)

            # Do the update.
            self.update(ctx)

        # Flag as seen.
        self.seen = True

        # Return our invalidation state.
        logging.debug('Node: Done building node: ' + str(self))
        return self._invalid

    def build_dependencies(self, ctx):
        logging.debug('Node: Building dependencies.')

        invalid = False
        for dep in self.dependencies:
            this = dep.build(ctx)
            invalid = invalid or this

        logging.debug('Node: Done building dependencies.')
        return invalid

    ##
    ## Determine if this node is invalidated.
    ##
    def invalidated(self, ctx):

        # If any of my sources are invalidated then I must be so. However
        # this is already checked in build.

        # If there is no CRC record on the context for this node
        # then I need to rebuild it.
        if ctx.node_crc(self) == None:
            return True

        # Run checks if this node is produced by a builder.
        if self.builder:

            # Compare CRCs of sources to those I have stored.
            old_src_crcs = ctx.node_source_crcs(self)
            if old_src_crcs is None:
                return True
            for src in self.builder.dependent_nodes:
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

    def scan(self, ctx, bldr):
        logging.debug('Node: Scanning.')
        if self.scanner is None:
            scanner = bldr.options.get('scanner', None)
            if scanner is not None:
                scanner = scanner(ctx)
        else:
            scanner = self.scanner
        if not self._done_scan:
            if scanner is not None:
                logging.debug('Node: Using scanner: ' + str(scanner.__class__))
                with open(str(self), 'r') as src_file:
                    data = src_file.read()
                new_deps = list(scanner.find_all(self, data, bldr))
                logging.debug('Node: New dependencies: ' + str(new_deps))
                self.dependencies.extend(new_deps)
                for nd in new_deps:
                    nd.progenitors.append(self)
                self._new_crc = self._crc32(data)
        logging.debug('Node: Done scanning.')

    def update_source_crcs(self, ctx):
        if self.builder:
            self._src_crcs = {}
            for src in self.builder.dependent_nodes:
                cur_crc = src.current_crc(ctx)
                if cur_crc is not None:
                    self._src_crcs[repr(src)] = cur_crc
        else:
            self._src_crcs = None

    def current_source_crcs(self, ctx):
        if self._src_crcs is None:
            self.update_source_crcs(ctx)
        return self._src_crcs

    def invalidate_progenitors(self, ctx):

        # Stop if there is no CRC stored on the context.
        if ctx.node_crc(self) is None:
            return

        # Remove the context's CRC.
        del ctx.crcs[repr(self)]

        # Call for all up builder targets.
        for n in self.products:
            n.invalidate_progenitors(ctx)
        for n in self.progenitors:
            n.invalidate_progenitors(ctx)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_lock']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._lock = threading.Lock()

class Always(Node):

    def __init__(self, *args, **kwargs):
        super(Always, self).__init__(*args, **kwargs)
        self.path = None

    def invalidated(self, ctx):
        return True
