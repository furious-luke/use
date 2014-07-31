import use

class default(use.Version):
    headers = ['gsl/gsl_types.h']
    libraries = ['gsl', 'gslcblas'] # TODO: gslcblas should be feature
    url = 'http://gnu.mirror.uber.com.au/gsl/gsl-1.15.tar.gz'

class gsl(use.Package):
    versions = [default]
