import clang

class clangxx(clang.clang):
    binaries = ['clang++']

    def __init__(self, *args, **kwargs):
        super(clangxx, self).__init__(*args, **kwargs)
        # add = self.option_parser.add
        # add('cxx11', text='-std=c++11 -stdlib=libc++')
