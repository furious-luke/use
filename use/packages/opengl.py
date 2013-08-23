import use

class glu(use.Feature):
    headers = ['GL/glu.h']
    libraries = ['GLU']

class Default(use.Version):
    version = 'default'
    headers = ['GL/gl.h']
    libraries = ['GL']
    features = [glu]

class opengl(use.Package):
    versions = [Default]
