import use

class Default(use.Version):
    version = 'default'
    headers = ['hdf5.h']
    libraries = ['hdf5']

class hdf5(use.Package):
    default_target_node = use.File
    default_builder = use.Builder
    versions = [Default]
