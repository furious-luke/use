import os
from .Node import *

class File(Node):

    def __init__(self, path, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        self.path = path
        self.abspath = os.path.abspath(path)
        self.absdirname = os.path.dirname(self.abspath)

    def __repr__(self):
        return self.path

    def invalidated(self, ctx):

        # If we have a builder then we know this node is a product.
        if self.builder:

            # If the file does not exist then we certainly need to rebuild
            # it.
            if not os.path.exists(self.path):
                return True

            # If it does exist then check our stored CRCs for sources.
            return Node.invalidated(self, ctx)

        # If we don't have a builder then we need to do a CRC check on the
        # file itself to see if it has changed.
        else:
            return self.invalidated_crc(self.path, ctx)

    ##
    ## Perform the parent update, but also update the new
    ## CRC value if not already done so.
    ##
    def update(self, ctx):
        logging.debug('File: Updating node: ' + str(self))
        super(File, self).update(ctx)
        if self._new_crc is None:
            self._new_crc = self._crc32_file(self.path)
        logging.debug('File: Done updating node: ' + str(self))
