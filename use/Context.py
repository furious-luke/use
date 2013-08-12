import sys, os, argparse, pickle
from utils import getarg, load_class
from .Use import Use
from .Rule import *
from .Resolver import Resolver
from .Argument import Arguments
from .Options import OptionDict
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
        self.crcs = {}
        self.src_crcs = {}
        self.old_bldrs = {}
        self.parser = argparse.ArgumentParser('"Use": Software configuration and build.')

    def __eq__(self, op):

        # Must have the same packages.
        for pkg in self.packages:
            if pkg not in op.packages:
                return False

        # # Must have same rules.
        # for rule in self.rules:
        #     if rule not in op.rules:
        #         return False

        # Must have same uses.
        for use in self.uses:
            if use not in op.uses:
                return False

        # # Must be using the same resolver.
        # if self.resolver != op.resolver:
        #     return False

        return True

    def __ne__(self, op):
        return not self.__eq__(op)

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

        # Only continue if there is a need to reconfigure.
        if not self.needs_configure():
            return

        sys.stdout.write('Configuring...\n')
        sys.stdout.write('  Packages to be configured:\n')
        for pkg in self.packages:
            sys.stdout.write('    ' + pkg.name + '\n')

        # Repeat the 'search' operation on each package until all return
        # True, indicating there are no new potential locations.
        sys.stdout.write('  Searching for candidates...')
        sys.stdout.flush()
        done = False
        while not done:
            done = True
            for pkg in self.packages:
                if not pkg.search():
                    done = False
        sys.stdout.write(' done.\n')

        # Now we have a list of all locations that passed the footprint
        # testing. Perform thorough checks.
        sys.stdout.write('  Checking candidates...')
        sys.stdout.flush()
        for pkg in self.packages:
            pkg.check()
        sys.stdout.write(' done.\n')

        # We have our list of available packages now. Analyse the entire build
        # graph to determine which packages need to be able to build with each
        # other.
        if self.resolver is not None:
            sys.stdout.write('  Resolving installations...')
            sys.stdout.flush()
            self.resolver(self)
            sys.stdout.write(' done.\n')

        # Clear CRCs and old builders.
        self.crcs = {}
        self.src_crcs = {}
        self.old_bldrs = {}

        # Save configuration results.
        self.save()

        sys.stdout.write('  Success.\n')

    ##
    ##
    ##
    def needs_configure(self):

        # Check if the user requested configuration.
        if 'configure' in self.arguments.targets:
            sys.stdout.write('User requested configuration.\n')
            return True

        # If we have not run before then definitely configure.
        if not os.path.exists('.use.db'):
            sys.stdout.write('No prior configuration to use.\n')
            return True

        # Check if anything has changed in the build structure.
        with open('.use.db', 'r') as inf:
            old_ctx = pickle.load(inf)
        if self != old_ctx:
            sys.stdout.write('Build structure has changed.\n')
            return True
        self._use_old_ctx(old_ctx)

        # Check each package for reconfiguration requests.
        for pkg in self.packages:
            if pkg.needs_configure():
                sys.stdout.write(pkg.name + ' has changed.\n')
                return True

        return False

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

        # Save state.
        self.update_node_crcs()
        self.save()

        logging.debug('Context: Done building targets.')

    def new_arguments(self):
        return Arguments(self)

    def new_options(self, *args, **kwargs):
        return OptionDict(*args, **kwargs)

    def load_package(self, pkg_name):

        # Load the package class.
        pkg_class = load_class(pkg_name)

        # Do we already have this package loaded?
        if pkg_class not in self._pkg_map:

            # Instantiate the package and insert into mapping.
            pkg = pkg_class(self)
            self._pkg_map[pkg_class] = pkg
            self.packages.append(pkg)

        # Use the existing package.
        else:
            pkg = self._pkg_map[pkg_class]

        return pkg

    ##
    ## Create a Use on this context.
    ##
    def new_use(self, pkg_name, opts=None, cond=None, **kwargs):
        pkg = self.load_package(pkg_name)
        if opts and kwargs:
            opts = opts + self.new_options(**kwargs)
        elif kwargs:
            opts = self.new_options(**kwargs)
        use = Use(pkg, opts, cond)
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
        # rule.source = to_list(src)

        # Store the new rule.
        self.rules.append(rule)
        return rule

    def package(self, name):
        pkg_class = load_class(name)
        return self._pkg_map[pkg_class]

    def exit(self):
        self.update_node_crcs()
        self.save()
        sys.exit(1)

    def node_crc(self, node):
        return self.crcs.get(repr(node), None)

    def node_source_crcs(self, node):
        return self.src_crcs.get(repr(node), None)

    def update_node_crcs(self):
        for rule in self.rules:
            for n in rule.nodes:
                self.update_node_crc(n)

        to_del = [k for k, v in self.crcs.iteritems() if v is None]
        for k in to_del:
            del self.crcs[k]

        to_del = [k for k, v in self.src_crcs.iteritems() if v is None]
        for k in to_del:
            del self.src_crcs[k]

    def update_node_crc(self, node):
        self.crcs[repr(node)] = node.current_crc(self)
        self.src_crcs[repr(node)] = node.current_source_crcs(self)

    ##
    ## Store context state to file.
    ##
    def save(self):
        parser = self.parser
        del self.parser
        # old_bldrs = getattr(self, 'old_bldrs', None)
        # if old_bldrs is not None:
        #     del self.old_bldrs
        with open('.use.db', 'w') as out:
            pickle.dump(self, out)
        self.parser = parser
        # if old_bldrs is not None:
        #     self.old_bldrs = old_bldrs

    ##
    ## Load context from file.
    ##
    def load(self, base_dir):
        pass

    def _use_old_ctx(self, old_ctx):

        # Copy over all the package contents.
        for pkg in self.packages:
            other_pkg = old_ctx._pkg_map[pkg.__class__]
            for ver, other_ver in zip(pkg.versions, other_pkg.versions):
                ver.installations = other_ver.installations
                for inst in ver.installations:

                    # Update version.
                    inst.version = ver

                    # Update features.
                    ftr_names = [f.name for f in inst.features]
                    inst.features = []
                    inst._ftr_map = {}
                    for ftr in ver.features:
                        if ftr.name in ftr_names:
                            inst.features.append(ftr)
                            inst._ftr_map[ftr.name] = ftr

        # Copy over CRCs.
        self.crcs = old_ctx.crcs
        self.src_crcs = old_ctx.src_crcs

        # Build a suite of old builders.
        self.old_bldrs = old_ctx.old_bldrs
        for rule in old_ctx.rules:
            for n in rule.product_nodes:
                if n.builder is not None:
                    self.old_bldrs[repr(n)] = n.builder

        # Run the resolver again.
        if self.resolver is not None:
            self.resolver(self)
