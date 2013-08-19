import use

class Default(use.Version):
    version = 'default'
    headers = ['GL/gl.h', 'GL/glu.h', 'GL/glut.h']
    libraries = ['GL', 'GLU', 'glut'] # TODO: Features and dependencies.

class glut(use.Package):
    versions = [Default]
