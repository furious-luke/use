argument('--prefix', default='/usr/local', help='installation path')
argument('--enable-debug', help='debugging mode')
argument('--enable-logging', help='logging switch')

# cc_flags = options(

cxx = use('cxx_compiler')
cc  = use('gcc')
mpi = use('mpi')

cxx_objs = rule('crc/src/.*\.cc', cxx, base='examples', label='compile C++ objects')
cc_objs  = rule('crc/src/.*\.c',  cc,  base='examples', label='compile C objects')
libs = rule(cc_objs + cxx_objs, cxx, options={'shared_library': True}, label='link library')
bins = rule(['crc/apps/.*\.cc', libs], cxx, label='link binary')
