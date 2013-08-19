import use

class Default(use.Version):
    version = 'default'
    headers = ['libhpc/libhpc.hh']
    libraries = ['hpc']

class libhpc(use.Package):
    versions = [Default]
