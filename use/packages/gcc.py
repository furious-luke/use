import os, re, logging
import use
from ..Platform import platform
from ..Action import Command
from ..Options import Option
from ..File import File
from ..utils import getarg
from ..conv import to_list, to_iter

##
##
##
class Default(use.Version):
    version = 'default'
    binaries = ['gcc']

    def actions(self, inst, sources, targets=[], options={}):
        return [Command(self.package.options())]

##
## GNU "gcc" tool.
##
class gcc(use.Package):
    default_target_node = use.File
    default_builder = use.Builder
    default_binary_filename = 'a.out'
    versions = [Default]

    def __init__(self, *args, **kwargs):
        super(gcc, self).__init__(*args, **kwargs)
        self._opts.binary = 'gcc'
        self._opts.add(Option('compile', '-c'))
        self._opts.add(Option('pic', '-fPIC'))
        self._opts.add(Option('c++11', '-std=c++11'))
        self._opts.add(Option('optimise', '-O', space=False))
        self._opts.add(Option('symbols', '-g'))
        if platform.os_name == 'darwin':
            self._opts.add(Option('shared_lib', text='-dynamiclib -install_name {target.abspath}'))
        else:
            self._opts.add(Option('shared_lib', text='-shared -Wl,-rpath={target.abspath}'))
        self._opts.add(Option('define', '-D', space=False))
        self._opts.add(Option('targets', '-o'))
        self._opts.add(Option('header_dirs', '-I'))
        self._opts.add(Option('library_dirs', '-L'))
        self._opts.add(Option('libraries', '-l', space=False))
        self._opts.add(Option('sources'))

    ##
    ## gcc's productions. The standard gcc production will
    ## produce a single object file for each source file.
    ##
    def make_productions(self, nodes, inst, opts):
        logging.debug('gcc: Making productions.')

        # Setup the mapping from source extensions to destination extensions.
        if 'suffix' not in opts:
            opts['suffix'] = '.os' if opts.get('pic', False) else '.o'

        # Single target or multitarget?
        single = not opts.get('compile', False)

        # If we're building a single binary then make sure we have a target.
        if 'target' not in opts:
            opts['target'] = self.default_binary_filename

        # Call parent.
        prods = super(gcc, self).make_productions(nodes, inst, opts, single=single)

        logging.debug('gcc: Done making productions.')
        return prods
