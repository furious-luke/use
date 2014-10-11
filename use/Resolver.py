import sys
from .Node import Node
from .Use import UseGroup
import logging

##
## Resolve which packages will be used. When searching
## for packages there will likely be several options for
## many. The Resolver's job is to determine which of the
## packages may work in tandem and update all Use objects
## to reflect this selection. This will be a compilcated
## operation, generally, as it will depend on what options
## each use has requested of the same package and also
## what dependencies each package is built against.
##
class Resolver(Node):

    def __init__(self):
        # TODO: Why am I a subclass of Node??
        super(Resolver, self).__init__()

    def __eq__(self, op):
        return self.__class__ == op.__class__

    def __ne__(self, op):
        return not self.__eq__(op)

    def __repr__(self):
        return 'resolver'

    ##
    ##
    ##
    def __call__(self, ctx):
        from .Feature import FeatureUse
        logging.debug('Resolver: Resolving package installations.')

        # Setup caches.
        self._conflicts = {}
        self._inst_iters = {}

        # Build a set of use roots. A root is any use with no parents.
        # Uses have parents as a result of the "use tree", which is
        # built from adding, and-ing and or-ing uses.
        logging.debug('Resolver: Finding root uses.')
        roots = set()
        for rule in ctx.rules:
            self.find_roots(rule.use, roots)
        logging.debug('Resolver: Found: ' + str(roots));

        # Traverse each tree and check, storing results accordingly.
        all_use_sets = []
        for root in roots:
            logging.debug('Resolver: Starting at root: ' + str(root))
            state, use_sets = self.walk(root)
            logging.debug('Resolver: Done walking root: ' + str(root))
            logging.debug('Resolver: Root success: ' + str(state))
            logging.debug('Resolver: Root use sets: ' + str(use_sets))
            all_use_sets.append(use_sets)
            if not state:
                missing = self.find_missing(root)
                sys.stdout.write('\n    Failed to resolve package')
                if len(missing) > 1:
                    sys.stdout.write('s, need at least one of the following:')
                else:
                    sys.stdout.write(':')
                for use in missing:
                    sys.stdout.write('\n      %s'%use.package.name)
                sys.stdout.write('\n    This kind of error can usually be resolved by\n')
                sys.stdout.write('    specifying the location of missing packages on\n')
                sys.stdout.write('    the command line. Check available options with:\n')
                sys.stdout.write('      use -h\n')
                sys.exit(1)

        # Now we need to examine each set of uses and determine if
        # the selected installations can work together.
        for root, use_sets in zip(roots, all_use_sets):

            # We need to ask each Use in each of the Use sets to
            # tell us which tests need to be run in order to confirm
            # they work.
            for use_set in use_sets:
                logging.debug('Resolver: Analysing use set: ' + str(use_set))
                for use in use_set:
                    if not use.resolve_set(root, use_set):
                        logging.debug('Resolver: Failed.')
                        sys.exit(1)

        # Delete caches.
        del self._conflicts
        del self._inst_iters

        logging.debug('Resolver: Done resolving package installations.')
        return True

    def check_use(self, use):
        from .Feature import FeatureUse
        logging.debug('Resolver: Checking Use: ' + str(use))

        # Don't process feature uses.
        if not isinstance(use, FeatureUse):

            # Only proceed if the Use is flagged to need resolving.
            if use.selected is None:
                use.selected = self.check_package(use)
                use._found = use.selected is not None
            else:
                logging.debug('Resolver: Use already has selected installation.')
        else:
            logging.debug('Resolver: Not checking FeatureUse.')

        logging.debug('Resolver: Done checking Use: ' + str(use))

    def check_package(self, use):
        pkg = use.package
        logging.debug('Resolver: Checking package: ' + str(pkg))

        # Search for a valid installation.
        sel = None
        inst_iter = self._inst_iters.get(use, pkg.iter_installations())
        for inst in inst_iter:
            logging.debug('Resolver: Checking installation: ' + str(inst))

            # The resolve method will return a list of packages that
            # failed to resolve against this one.
            if inst.resolve():
                sel = inst
                logging.debug('Resolver: Using installation: ' + str(inst))
                break
            else:
                logging.debug('Resolver: Failed.')

        # Store the iterator, unless the iterator is done, in which
        # case we need to erase it.
        if sel is not None:
            self._inst_iters[use] = inst_iter
        else:
            try:
                del self._inst_iters[use]
            except:
                pass

        logging.debug('Resolver: Done checking package: ' + str(pkg))
        return sel

    def check_feature(self, use):
        if use.use.enabled:
            for ftr in use.use.selected.features:
                if ftr.name == use.feature_name:
                    use.selected = ftr
                    break

    def find_roots(self, use, roots):
        if not use.parents:
            roots.add(use)
        for par in use.parents:
            self.find_roots(par, roots)

    def walk(self, use):
        from .Feature import FeatureUse
        logging.debug('Resolver: Walking: ' + str(use))

        if isinstance(use, UseGroup):
            logging.debug('Resolver: Have UseGroup.')

            have_left, use_set_left = self.walk(use.left) if use.left is not None else False
            have_right, use_set_right = self.walk(use.right) if use.right is not None else False
            logging.debug('Resolver: Have left: ' + str(have_left))
            logging.debug('Resolver: Have right: ' + str(have_right))

            if not have_left:
                if use.op == 'or':
                    use._found = have_right
                    return have_right, use_set_right
                else:
                    use._found = False
                    if use.op == 'add':
                        return False, self.add_sets(use_set_left, use_set_right)
                    else: # 'and'
                        return False, use_set_left + use_set_right

            if use.op != 'or':
                use._found = have_right
                if use.op == 'add':
                    return have_right, self.add_sets(use_set_left, use_set_right)
                else: # 'and'
                    return have_right, use_set_left + use_set_right
            else:
                use._found = True
                return True, use_set_left

        elif isinstance(use, FeatureUse):
            logging.debug('Resolver: Have FeatureUse.')
            self.check_use(use.use)
            self.check_feature(use)
            return use.selected is not None, [[use]]

        else:
            logging.debug('Resolver: Have Use.')
            self.check_use(use)
            return use.selected is not None, [[use]]

    def find_missing(self, use):
        from .Feature import FeatureUse
        missing = []
        if not isinstance(use, FeatureUse):
            if not use._found:
                if isinstance(use, UseGroup):
                    if use.op == 'or':
                        missing.extend(self.find_missing(use.left))
                        missing.extend(self.find_missing(use.right))
                    else:
                        missing.extend(self.find_missing(use.left))
                        if not missing:
                            missing.extend(self.find_missing(use.right))
                else:
                    missing.append(use)
        else:
            if use.selected is None:
                missing.append(use)
        return missing

    def add_sets(self, left, right):
        res = []
        for l in left:
            for m in right:
                res.append(l + m)
        return res
