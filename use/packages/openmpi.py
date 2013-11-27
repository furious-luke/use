import use

class mpicxx(use.Feature):
    name = 'mpic++'
    binaries = ['mpic++']
#    libraries = ['mpi_cxx']

class Default(use.Version):
    version = 'default'
    headers = ['mpi.h']
    libraries = [['mpi_cxx', 'mpi'],
                 ['mpi']]
    features = [mpicxx]

class openmpi(use.Package):
    versions = [Default]
    header_sub_dirs = ['include/mpi'] # Ubuntu
    environ_name = 'MPI'
