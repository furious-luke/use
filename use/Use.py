from .Node import Node
from .Package import Search, Installation
from .Resolver import Resolver
from .utils import load_class, getarg

##
## Locate one or more packages to use.
##
def use(graph, *args, **kwargs):

    # Need to store a mapping from the package class to the
    # instantiated package.
    if not hasattr(graph, '_pkg_map'):
        setattr(graph, '_pkg_map', {})

    # Load the package class.
    pkg_name, args = getarg('package', args, kwargs)
    opts, args = getarg('options', args, kwargs, False)
    pkg_class = load_class(pkg_name)

    # Do we already have this package loaded?
    if pkg_class not in graph._pkg_map:

        # Instantiate the package and insert into mapping.
        pkg = pkg_class()
        graph._pkg_map[pkg_class] = pkg

        # Use the Search builder by default.
        bldr = Search(pkg)

        # Need a placeholder for the potentially many installations
        # found by the package.
        ph = graph.placeholder()

        # Use a particular resolver by default.
        rslvr = Resolver()

        # Create an installation for the resolver product.
        inst = Installation()

        # Insert into the graph.
        graph.add_edge(pkg, bldr, source=True)
        graph.add_edge(bldr, ph, product=True)
        graph.add_edge(ph, rslvr, source=True)
        graph.add_edge(rslvr, inst, product=True)

    # If we already have the package, find the installation.
    else:
        pkg = graph._pkg_map[pkg_class]

        # Get the second child of the package and make sure it's
        # a resolver.
        rslvr = graph.first_child(graph.first_child(graph.first_child(pkg)))
        assert isinstance(rslvr, Resolver)

        # Make a new installation to be attached to the resolver.
        inst = Installation()
        graph.add_edge(rslvr, inst)

    # Create the new Use and attach it as a child of the
    # resolved installation.
    this_use = Use(pkg, opts)
    graph.add_edge(inst, this_use)

    # Return the created Use.
    return this_use

##
## Represents a package installation with options.
##
class Use(Node):

    def __init__(self, package, options):
        super(Use, self).__init__()
        self.package = package
        self.options = options
        self.selected = None

    # def __call__(self, source):
    #     return self.package(source)

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

    def productions(self, nodes, options={}):
        return self.selected.productions(nodes, self.options)
