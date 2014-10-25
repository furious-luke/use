argument('--prefix', default='/usr/local', help='installation path')
argument('--enable-debug', help='debugging mode')
argument('--enable-logging', help='logging switch')

# cc_flags = options(

cxx = use('cxx_compiler')
mpi = use('mpi')

objs = rule('crc/src/.*\.cc', cxx, base='examples')
libs = rule(objs, cxx, options={'shared_library': True})
