cp  = files.feature('copy', prefix='build')
cc  = use('cxx_compiler', optimise=0, symbols=True, compile=True, prefix='build')
bin = use('cxx_compiler', optimise=0, symbols=True)

hdrs = rule(r'src/.+\.hh$', cp)
objs = rule(r'src/.+\.cc$', cc)
prgs = rule(objs, bin, target='build/program')
