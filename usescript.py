argument('--prefix', default='/usr/local', help='installation path')
argument('--enable-debug', help='debugging mode')
argument('--enable-logging', help='logging switch')

gcc = use('gcc')
mpi = use('mpi')

objs = rule('crc/src/.*\.cc', gcc, base='examples')
libs = rule(objs, gcc, options={'shared_library': True})
