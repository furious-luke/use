import os, logging
import use

class GccProducer(use.Producer):

    def __init__(self, *args, **kwargs):
        super(GccProducer, self).__init__(*args, **kwargs)
        self.option('compile', '-c', help='compile to objects but do not link')
        self.option('profile', '-pg', help='add profiling information')
        self.option('pic', '-fPIC', help='position independent code')
        self.option('openmp', '-fopenmp', help='enable openmp')
        self.option('cxx11', '-std=c++11', help='enable C++11 standard')
        self.option('optimise', '-O', space=False, help='produce optimised code')
        self.option('symbols', '-g', help='include symbol information')
        if use.platform.os_name == 'darwin':
            o = self.option('shared_lib', text='-dynamiclib -install_name {target.abspath} -undefined dynamic_lookup')
        else:
            o = self.option('shared_lib', '-shared')
        o.help = 'produce a shared library'
        self.option(o)
        self.option('define', '-D', space=False, help='add preprocessor definition')
        self.option('target', '-o', help='production target')
        self.option('header_dirs', '-I', help='header search directories')
        self.option('library_dirs', '-L', help='library search directories')
        if use.platform.os_name != 'darwin':
            self.option('rpath_dirs', '-Wl,-rpath=', space=False, abspath=True, help='rpath search directories')
        self.option('sources', help='production sources')
        self.option('libraries', '-l', space=False, help='extra libraries')
        if use.platform.os_name == 'darwin':
            o = self.option('coverage', text='')
        else:
            o = self.option('coverage', text='-fprofile-arcs -ftest-coverage')
        o.help = 'include code coverage information'
        self.option('target_suffix', help='prepend to target name')
        self.option('target_prefix', help='append to target name')

    ##
    ## gcc's productions. The standard gcc production will
    ## produce a single object file for each source file.
    ##
    def make_productions(self, nodes, inst, opts):
        logging.debug('gcc: Making productions.')

        # Handle the mode (compile or link).
        if opts.get('compile'):
            if 'target_suffix' not in opts:
                opts['target_suffix'] = '.os' if opts.get('pic') else '.o'
        else:
            if 'target_suffix' not in opts:
                if opts.get('shared_lib'):
                    opts['target_suffix'] = '.so'
            if 'target_prefix' not in opts:
                if opts.get('shared_lib') == True:
                    opts['target_prefix'] = 'lib'

        # If profiling is selected, we must also have symbols.
        if opts.get('profile') == True:
            opts['symbols'] = True

        # Compiling is necessarily multitarget. Linking can be either, but
        # defaults to true as we typically link to a single target.
        if opts.get('compile'):
            single = True
        else:
            single = opts.get('single', True)

        # Have the platform order the library directories as appropriate.
        if 'library_dirs' in opts:
            opts['library_dirs'] = platform.order_library_dirs(opts['library_dirs'])

        # Call parent to make the list of productions.
        prods = super(gcc, self).make_productions(nodes, inst, opts, single=single)

        logging.debug('gcc: Done making productions.')
        return prods

    ##
    ## Add scanners to C source code.
    ##
    def add_scanners(self, prods):

        # Process each source node in the productions.
        for s, b, t in nodes:
            for n in s:

                # Don't try to apply the scanner twice.
                if n.scanner is None:

                    # Only apply to source code.
                    if os.path.splitext(str(n))[1].lower() in ['.c', '.cc', '.cxx', '.cpp']:
                        n.scanner = CScanner(self.ctx)

class CompileProducer(GccProducer):
    source_pattern = '(?P<name>.*)\.(?:c|C)$'
    target_pattern = '{name}.o'

class LinkProducer(GccProducer):
    source_pattern = '(?P<name>.*)\.os?$'
    target_pattern = 'a.out'

class gcc(use.Package):
    producers = [CompileProducer, LinkProducer]
    binaries = ['gcc']
