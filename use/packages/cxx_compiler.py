import use
from ..Platform import platform

class cxx_compiler(use.Package):
    name = 'C++ compiler'
    option_name = 'cxx'
    sub_packages = ['gcc', 'clangxx']

    def resolve(self):

        # If we're building on Darwin, favor clang.
        if platform.os_name == 'darwin':
            pass
