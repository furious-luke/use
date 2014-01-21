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

    ##
    ## Confirm package can be built.
    ##
    def resolve_set(self, root, use_set, inst, ver):

        # # Create temporary file.
        # code = '#include <mpi.h> int main( int argc, char* argv[] ) { return 0; }'
        # node = use.Node()

        # # Run a simple compile/link.
        # prods = root.expand([node])
        # if prods:
        #     root.apply(prods)
        #     return prods[1].update(self.ctx)
        # else:
        #     return True

        return True
