import os, re, logging
import use
from ..Action import Command
from ..Options import Option
from ..File import File
from ..utils import getarg
from ..conv import to_list, to_iter

##
##
##
class Builder(use.Builder):
    pass

##
##
##
class Default(use.Version):
    version = 'default'
    binaries = ['gcc']

    def actions(self, sources, targets=[], options={}):
        # sources = to_iter(sources)
        # targets = to_iter(targets)
        # if isinstance(options, (str, unicode)):
        #     cmd = self.options()(self.binaries[0], options, sources=sources, targets=targets)
        # else:
        #     opts = {'targets': targets, 'sources': sources}
        #     opts.update(options)
        #     cmd = self.options()(self.binaries[0], **opts)
        return [Command(self.package.options())]

##
## GNU "gcc" tool.
##
class gcc(use.Package):
    default_target_node = use.File
    default_builder = Builder
    versions = [Default]

    def __init__(self, *args, **kwargs):
        super(gcc, self).__init__()
        self._opts.binary = 'gcc'
        self._opts.add(Option('compile', '-c'))
        self._opts.add(Option('targets', '-o'))
        self._opts.add(Option('header_dirs', '-I'))
        self._opts.add(Option('library_dirs', '-L'))
        self._opts.add(Option('libraries', '-l', space=False))
        self._opts.add(Option('sources'))

    ##
    ## gcc's productions. The standard gcc production will
    ## produce a single object file for each source file.
    ##
    def expand(self, nodes, vers, inst, use_options={}, rule_options={}):
        logging.debug('gcc: Expanding %s'%nodes)

        opts = self.merge_options(vers, use_options, rule_options)
        prods = []

        # If we have the compile flag then produce separate targets.
        if 'compile' in opts:
            for node in nodes:
                obj_filename, obj_ext = os.path.splitext(node.path)
                if obj_ext.lower() in ['.c', '.cc', '.cpp']:
                    obj_filename += '.o'
                    target = self.default_target_node(obj_filename)
                prods.append(((node,), self.default_builder(node, target, vers.actions(node, target, opts), opts), (target,)))

        # Else produce a single target.
        else:
            target = opts.get('target', None)
            if target is None:
                target = File('a.out')
            prods.append((list(nodes), self.default_builder(nodes, target, vers.actions(nodes, target, opts)), (target,)))

        logging.debug('gcc: Productions = ' + str(prods))
        return prods
