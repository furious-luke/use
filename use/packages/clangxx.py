import clang

class Default(clang.Default):
    binaries = ['clang++']

class clangxx(clang.clang):
    versions = [Default]

    def __init__(self, *args, **kwargs):
        super(clangxx, self).__init__(*args, **kwargs)
        self.name = 'clang++'
        self._opts.binary = 'clang++'
