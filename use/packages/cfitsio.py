import use

class Default(use.Version):
    version = 'default'
    headers = ['fitsio.h']
    libraries = ['cfitsio']

class cfitsio(use.Package):
    versions = [Default]
