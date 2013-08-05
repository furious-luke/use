import os, re, logging
import use
from ..utils import getarg
from ..conv import to_list

##
##
##
class Builder(use.Builder):

    _prog = re.compile('(' + ')|('.join([
    ]) + ')')

    def _parse(self):
        assert len(self.sources) == 1 and len(self.targets) == 1, 'Can\'t run "file" on multiple sources/targets.'
        match = self._prog.search(self.actions[0].stdout)
        assert match and match.lastindex > 0
        self.targets[0].file_type = match.lastindex - 1

##
## A feature for mpicc.
##
class mpicc(use.Feature):
    binaries = ['mpicc']

    def __init__(self, *args, **kwargs):
        super(mpicc, self).__init__(*args, **kwargs)

        # We will need to figure out which compiler type this
        # mimics.
        self.cc = None

    def actions(self, sources, targets=[]):
        return self.cc.expand(*args, **kwargs)

    def expand(self, *args, **kwargs):
        return self.cc.expand(*args, **kwargs)

##
##
##
class Default(use.Version):
    version = 'default'
    headers = ['mpi.h']
    libraries = ['mpich']
    features = [mpicc]

    def actions(self, *args, **kwargs):
        for ftr in self.features:
            acts = ftr(*args, **kwargs)
            if acts is not None:
                return acts
        return None

##
## MPICH2
##
class mpich2(use.Package):
    default_target_node = use.File
    default_builder = Builder
    versions = [Default]

    ##
    ## mpich2's productions.
    ##
    def expand(self, nodes, options={}):
        logging.debug('mpich2: Expanding.')
        logging.debug('mpich2: Nodes: %s'%nodes)

        # Expand the list of productions.
        prods = []
        for node in nodes:
            obj_filename = os.path.splitext(node.path)[0] + '.o'
            target = self.default_target_node(obj_filename)
            prods.append(((node,), self.default_builder(node, target), (target,)))

        logging.debug('mpich2: Productions: ' + str(prods))
        logging.debug('mpich2: Done expanding.')
        return prods
