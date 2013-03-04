##
## We are guaranteed of having the following defined:
##
##   use  : Interface to finding packages. Packages are defined
##          as begin a cohesive collection of binaries, headers
##          and libraries.
##

# # How to influence all C compilers with a common set of flags?
# # Create an option set and pass it to each compiler access.
# options({
#    'cc': '-O0',
#    'hpcc': '-O2 -DNDEBUG',
# })

# Cache packages.
cc = use('gcc', name='cc')
hpcc = use('gcc', name='hpcc')
mpi = use('mpi')
others = use('gsl', 'fftw')
default(cc, mpi)

# # Setup variants.
# var = variant('debug')
# #var = variant('optimised')
# default(var)

# Define the rules used to build sources.
rules({
    'sub1': None, # build sub-project
    'src/*.cc': [], #[cc, use('mpi')]
    'apps/prog.cc': ['src/*.cc'],
    'hpsrc/*.cc': [hpcc, use('libhpc'), others],
})
