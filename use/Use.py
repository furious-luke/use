from utils import load_class, getarg

# Keep track of used packages.
used_packages = {}
uses = {}

##
## Locate one or more packages to use.
##
def use(*args, **kwargs):
    pkg_name, args = getarg('package', args, kwargs)
    opts, args = getarg('options', args, kwargs, False)
    pkg = used_packages.get(pkg_name, None)
    if not pkg:
        pkg_class = load_class(pkg_name)
        pkg = pkg_class()
        used_packages[pkg_name] = pkg
    if pkg not in uses:
        uses[pkg] = []
    this_use = Use(pkg, opts)
    uses[pkg].append(this_use)
    return this_use

##
## Represents a package installation with options.
##
class Use(object):

    def __init__(self, package, options):
        self.package = package
        self.options = options

    def __call__(self, source):
        return self.package(source)

    def __repr__(self):
        text = 'Use(' + repr(self.package)
        if self.options:
            text += ', ' + repr(self.options)
        text += ')'
        return text

    def has_packages(self):
        return True

    def package_iter(self):
        yield self.package
