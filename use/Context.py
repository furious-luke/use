import argparse
from utils import getarg, load_class
from .Use import Use
from .Rule import *
from .Resolver import Resolver
from .conv import to_list
import logging

##
## Wraps a single build context. The context manages the
## overall run, including commencement and storage. (??)
##
class Context(object):

    def __init__(self):
        self.packages = []
        self.rules = []
        self.uses = []
        self.targets = []
        self.resolver = Resolver()
        self._pkg_map = {}
        self.parser = argparse.ArgumentParser('"Use": Software configuration and build.')

    ##
    ##
    ##
    def parse_arguments(self):

        # Add arguments.
        self.parser.add_argument('targets', nargs='*', help='Specify build targets.')
        for pkg in self.packages:
            pkg.add_arguments(self.parser)

        # Parse.
        self.arguments = self.parser.parse_args()

    ##
    ## Search for packages.
    ##
    def configure(self):

        # Repeat the 'search' operation on each package until all return
        # True, indicating there are no new potential locations.
        done = False
        while not done:
            done = True
            for pkg in self.packages:
                if not pkg.search():
                    done = False

        # Now we have a list of all locations that passed the footprint
        # testing. Perform thorough checks.
        for pkg in self.packages:
            pkg.check()

        # We have our list of available packages now. Analyse the entire build
        # graph to determine which packages need to be able to build with each
        # other.
        if self.resolver is not None:
            self.resolver(self)

    ##
    ## Scan files for rule sources.
    ##
    def scan(self):
        for rule in self.rules:
            rule.scan(self)

    ##
    ## Expand sources into objects.
    ##
    def expand(self):
        logging.debug('Context: Expanding rules.')
        for rule in self.rules:
            rule.expand(self)

    ##
    ## Decide which targets to build.
    ##
    def find_targets(self):
        logging.debug('Context: Finding targets.')

        # By default we locate any nodes with no children.
        self.targets = []
        for rule in self.rules:
            for node in rule.product_nodes:
                if not node.products:
                    self.targets.append(node)
        logging.debug('Context: Found targets: ' + str(self.targets))

        logging.debug('Context: Done finding targets.')

    ##
    ## Build targets.
    ##
    def build(self):
        logging.debug('Context: Building targets.')

        for tgt in self.targets:
            tgt.build(self)

        logging.debug('Context: Done building targets.')

    ##
    ## Create a Use on this context.
    ##
    def new_use(self, *args, **kwargs):

        # Load the package class.
        pkg_name, args = getarg('package', args, kwargs)
        opts, args = getarg('options', args, kwargs, False)
        pkg_class = load_class(pkg_name)

        # Do we already have this package loaded?
        if pkg_class not in self._pkg_map:

            # Instantiate the package and insert into mapping.
            pkg = pkg_class()
            self._pkg_map[pkg_class] = pkg
            self.packages.append(pkg)

        # Use the existing package.
        else:
            pkg = self._pkg_map[pkg_class]

        use = Use(pkg, opts)
        self.uses.append(use)
        return use

    def new_rule(self, src, use, **kwargs):

        # # We must be able to locate the requested use already
        # # in the graph.
        # assert use in self.uses

        # Create a new rule to encapsulate this.
        rule = Rule(src, use, kwargs)

        # # Source can either be a regular expression, a list
        # # of regular expressions or a RuleList. If we have a rule
        # # list we add edges between the rules.
        # if isinstance(src, RuleList):
        #     rule.sub_rules.extend([s for s in src])

        # # Otherwise make sure we have a list and add the rule
        # # as a node.
        # else:
        rule.source = to_list(src)

        # Store the new rule.
        self.rules.append(rule)
        return rule

    def package(self, name):
        pkg_class = load_class(name)
        return self._pkg_map[pkg_class]
