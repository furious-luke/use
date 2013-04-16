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
##
##
class Default(use.Version):
    version = 'default'
    binaries = ['gcc']

    def _actions(self, sources, targets=[]):
        return [use.Action('%s -c -o %s %s'%(
            self.binaries[0].path,
            targets[0].path,
            ' '.join([s.path for s in sources]),
        ))]

##
## GNU "gcc" tool.
##
class gcc(use.Package):
    default_target_node = use.File
    default_builder = Builder
    versions = [Default]

    ##
    ## gcc's productions. The standard gcc production will
    ## produce a single object file for each source file.
    ##
    def productions(self, nodes, options={}):
        prods = []
        for node in nodes:
            obj_filename = os.path.splitext(node.path)[0] + '.o'
            prods.append(((node,), obj_filename))
        logging.debug('gcc: Productions = ' + str(prods))
        return prods
