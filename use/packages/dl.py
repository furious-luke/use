import use

class default(use.Version):
    version = 'default'
    headers = ['dlfcn.h']
    libraries = ['dl']

class dl(use.Package):
    versions = [default]
