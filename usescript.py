argument('--prefix', default='/usr/local', help='installation path')
argument('--enable-debug', help='debugging mode')
argument('--enable-logging', help='logging switch')
argument('--with-opengl', help='use opengl')

gcc = use('gcc')
mpi = use('mpi')

ex = rule('examples/crc/src/*.cc', gcc, options={'sharedlibrary': True})
