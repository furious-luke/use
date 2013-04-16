from Node import Node
from .utils import load_class, getarg

##
## Locate one or more packages to use.
##
def use(graph, *args, **kwargs):

    # Load the package class.
    pkg_name, args = getarg('package', args, kwargs)
    opts, args = getarg('options', args, kwargs, False)
    pkg_class = load_class(pkg_name)

    # Try and locate the package class in the graph.
    pkg = graph.find_node(pkg_class)
    if not pkg:
        pkg = pkg_class()

        # Use the Search builder by default.
        bldr = Package.Search()

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

    # If we already have the package, find the resolver.
    else:
        rslvr = graph.find_first_child(pkg, Resolver)
        inst = graph.find_first_child(rslver, Installation)

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
        self.package = package
        self.options = options
        self.selected = None

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

    def productions(self, nodes, options={}):
        return self.selected.productions(nodes, self.options)
