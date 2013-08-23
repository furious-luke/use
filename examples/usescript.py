# Define some arguments.
args = (arguments()
        ('--prefix', default='/usr/local', help='Installation path.')
        ('--enable-debug', dest='debug', action='boolean', default=False, help='Enable/disable debugging mode.')
        ('--enable-instrument', dest='instrument', action='boolean', default=False, help='Enable/disable instrumentation.')
        ('--enable-stacktrace', dest='stacktrace', action='boolean', default=False, help='Enable/disable debugging stacktrace.')
        ('--enable-memory-debug', dest='memory_debug', action='boolean', default=False, help='Enable/disable memory debugging.')
        ('--enable-memory-ops', dest='memory_ops', action='boolean', default=False, help='Enable/disable memory operation logging.')
        ('--enable-memory-stats', dest='memory_stats', action='boolean', default=False, help='Enable/disable memory statistics logging.')
        ('--enable-logging', dest='logging', action='boolean', default=True, help='Enable/disable all logging routines.'))

# Need to define optional packages ahead of some options
# so we can include preprocessor definitions.
glut = use('glut')

# Define some options.
cc_opts = (
    options(cxx11=True,
            pic=True,
            define=[platform.os_name.upper()]) + 
    options(args.debug == True,
            prefix='build/debug',
            library_dirs=['build/debug/lib'],
            rpath_dirs=['build/debug/lib'],
            header_dirs=['build/debug/include'],
            optimise=0,
            symbols=True) +
    options(args.debug == False,
            prefix='build/optimised',
            library_dirs=['build/optimised/lib'],
            rpath_dirs=['build/optimised/lib'],
            header_dirs=['build/optimised/include'],
            optimise=3,
            symbols=False,
            define=['NDEBUG']) +
    options(args.instrument == False,   define=['NINSTRUMENT']) +
    options(args.logging == False,      define=['NLOG']) +
    options(args.stacktrace == False,   define=['NSTACKTRACE']) +
    options(args.memory_debug == False, define=['NMEMDEBUG']) +
    options(args.memory_ops == False,   define=['NMEMOPS']) +
    options(args.memory_stats == False, define=['NMEMSTATS']) +
    options(glut.have == True, define=['HAVE_GLUT'])
)
cp_opts = (
    options(args.debug == True,
            prefix='build/debug/include/libhpc') +
    options(args.debug == False,
            prefix='build/optimised/include/libhpc')
)

# Define compilers/linkers.
cc  = use('cxx_compiler', cc_opts, compile=True)
sl  = use('cxx_compiler', cc_opts, shared_lib=True)
sl_inst = use('cxx_compiler', cc_opts, targets.contains('install'), shared_lib=True, prefix=args.prefix)
bin = use('cxx_compiler', cc_opts)
ar  = use('ar', cc_opts, add=True)

# Which packages will we be using?
boost   = use('boost')
mpi     = use('mpi')
hdf5    = use('hdf5')
pugixml = use('pugixml')
cp      = files.feature('copy', cp_opts)
hdr_inst = files.feature('copy', None, targets.contains('install'), prefix=args.prefix + '/include/libhpc')
lib_inst = files.feature('copy', None, targets.contains('install'), prefix=args.prefix)

# Setup flows.
pkgs = boost + mpi + hdf5 + pugixml + (glut | identity)
cc  = cc  + pkgs
sl  = sl  + pkgs
bin = bin + pkgs

# Copy all headers.
hdrs = rule(r'src/.+\.hh$', cp & hdr_inst, target_strip_dirs=1)
tccs = rule(r'src/.+\.tcc$', cp & hdr_inst, target_strip_dirs=1)

# Build all sources.
objs = rule(r'src/.+\.cc$', cc)

# Link into static/shared library.
static_lib = rule(objs, ar, target=platform.make_static_library('lib/hpc'))
shared_lib = rule(objs, sl & sl_inst, target=platform.make_shared_library('lib/hpc'))
rule(static_lib, lib_inst, target_strip_dirs=2)

# Build the unit test runner.
rule(r'tests/.+\.cc$', bin, target='bin/libhpc_unit', libraries=['hpc'])
