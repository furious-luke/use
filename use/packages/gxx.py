import gcc

class CompileProducer(gcc.CompileProducer):
    source_pattern = '(?P<name>.*)\.(?:cc?|CC?|cpp|CPP|cxx|CXX)$'

class gxx(gcc.gcc):
    producers = [CompileProducer, gcc.LinkProducer]
    binaries = ['g++']
