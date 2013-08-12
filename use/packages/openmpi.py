import use

class Default(use.Version):
    version = 'default'
    headers = ['mpi.h']
    libraries = ['mpi']

class openmpi(use.Package):
    versions = [Default]
