import use

class Default(use.Version):
    version = 'default'
    headers = ['libhpc/libhpc.hh']
    libraries = ['hpc']
    url = 'http://github.com/furious-luke/libhpc/archive/use.zip'

class libhpc(use.Package):
    versions = [Default]
    dependencies = ['boost', 'mpi', 'hdf5', 'pugixml'] #, '?glut']

    def build_handler(self):
        config = 'use --enable-debug --enable-openmp --prefix {prefix}'
        return [config,
                'use',
                'use install']
