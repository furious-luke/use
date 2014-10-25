import use

class cxx_compiler(use.Package):
    name = 'C++ compiler'
    option_name = 'cxx'
    sub_packages = ['gxx', 'clangxx']
