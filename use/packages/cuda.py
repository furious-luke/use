import os, re, logging
import use
from ..Platform import platform
from ..Action import Command
from ..Options import Option
from ..File import File
from ..Scanner import CScanner
from ..utils import getarg
from ..conv import to_list, to_iter

class default(use.Version):
    binaries = ['nvcc']
    headers = ['cuda.h', 'cuda_runtime.h']
    libraries = ['cudart']

    def actions(self, inst, sources, targets=[], options={}):
        return [Command(self.package.options(), inst.binaries[0])]

class cuda(use.Package):
    default_binary_filename = 'a.out'
    versions = [default]

    def __init__(self, *args, **kwargs):
        super(cuda, self).__init__(*args, **kwargs)
        self.name = 'CUDA'
        self._opts.add(Option('compile', '-c'))
        self._opts.add(Option('optimise', '-O', space=False))
        self._opts.add(Option('symbols', '-g'))
        self._opts.add(Option('define', '-D', space=False))
        self._opts.add(Option('targets', '-o'))
        self._opts.add(Option('header_dirs', '-I'))
        self._opts.add(Option('library_dirs', '-L'))
        self._opts.add(Option('sources'))
        self._opts.add(Option('libraries', '-l', space=False))

    ##
    ## gcc's productions. The standard gcc production will
    ## produce a single object file for each source file.
    ##
    def make_productions(self, nodes, inst, opts):
        logging.debug('cuda: Making productions.')

        # Setup the mapping from source extensions to destination extensions.
        if 'suffix' not in opts:
            opts['suffix'] = '.o'

        # Single target or multitarget?
        single = not opts.get('compile', False)

        # Have the platform order the library directories as appropriate.
        if 'library_dirs' in opts:
            opts['library_dirs'] = platform.order_library_dirs(opts['library_dirs'])

        # Call parent.
        prods = super(cuda, self).make_productions(nodes, inst, opts, single=single)

        # Prepare the scanners for each node.
        for n in nodes:
            if n.scanner is None:
                if os.path.splitext(str(n))[1].lower() in ['.c', '.cc', '.cxx', '.cpp', '.cu']:
                    n.scanner = CScanner(self.ctx)

        logging.debug('cuda: Done making productions.')
        return prods
