import os, logging
import use
from ..Platform import platform
from ..Action import Command
from ..Scanner import CScanner

class default(use.Version):
    binaries = ['gcc']

    def actions(self, inst, sources, targets=[], options={}):
        return [Command(self.package.options(), inst.binaries[0])]

class gcc(use.Package):
    default_binary_filename = 'a.out'
    versions = [default]

    def __init__(self, *args, **kwargs):
        super(gcc, self).__init__(*args, **kwargs)
        add = self.option_parser.add
        add('compile', '-c')
        add('profile', '-pg')
        add('pic', '-fPIC')
        add('openmp', '-fopenmp')
        add('cxx11', '-std=c++11')
        add('optimise', '-O', space=False)
        add('symbols', '-g')
        if platform.os_name == 'darwin':
            add('shared_lib', text='-dynamiclib -install_name {target.abspath} -undefined dynamic_lookup')
        else:
            add('shared_lib', '-shared')
        add('define', '-D', space=False)
        add('targets', '-o')
        add('header_dirs', '-I')
        add('library_dirs', '-L')
        if platform.os_name != 'darwin':
            add('rpath_dirs', '-Wl,-rpath=', space=False, abspath=True)
        add('sources')
        add('libraries', '-l', space=False)
        if platform.os_name == 'darwin':
            add('coverage', text='')
        else:
            add('coverage', text='-fprofile-arcs -ftest-coverage')

    ##
    ## gcc's productions. The standard gcc production will
    ## produce a single object file for each source file.
    ##
    def make_productions(self, nodes, inst, opts):
        logging.debug('gcc: Making productions.')

        # Setup the mapping from source extensions to destination extensions.
        if 'suffix' not in opts:
            opts['suffix'] = '.os' if opts.get('pic', False) else '.o'

        # If profiling is selected, we must also have symbols.
        if opts.get('profile', False) == True:
            opts['symbols'] = True

        # Single target or multitarget?
        single = not opts.get('compile', False)

        # Have the platform order the library directories as appropriate.
        if 'library_dirs' in opts:
            opts['library_dirs'] = platform.order_library_dirs(opts['library_dirs'])

        # Call parent.
        prods = super(gcc, self).make_productions(nodes, inst, opts, single=single)

        # Prepare the scanners for each node.
        for n in nodes:
            if n.scanner is None:
                if os.path.splitext(str(n))[1].lower() in ['.c', '.cc', '.cxx', '.cpp']:
                    n.scanner = CScanner(self.ctx)

        logging.debug('gcc: Done making productions.')
        return prods
