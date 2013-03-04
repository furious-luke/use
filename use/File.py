from Node import *

class File(Node):

    def __init__(self, path):
        Node.__init__(self)
        self.path = path

    def __repr__(self):
        return self.path
