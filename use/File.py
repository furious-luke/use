import os
from .Node import *

class File(Node):

    def __init__(self, path):
        Node.__init__(self)
        self.path = path
        self.abspath = os.path.abspath(path)
        self.absdirname = os.path.dirname(self.abspath)

    def __repr__(self):
        return self.path

    def invalidated(self, ctx):

        # If we have a builder then we know this node is a product.
        # If that's the case, then just check if the file exists or not.
        if self.builder:
            return not os.path.exists(self.path)

        # If we don't have a builder then we need to do a CRC check.
        else:
            return self.invalidated_crc(self.path, ctx)
