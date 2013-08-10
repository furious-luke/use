import sys
from .Node import Node
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
        logging.debug('Resolving package installations.')

        # Just use the first installation of every package.
        for use in ctx.uses:

            # Don't process feature uses yet.
            if not isinstance(use, FeatureUse):

                # Get the first installation.
                use.selected = None
                for ver in use.package.versions:
                    for inst in ver.installations:
                        use.selected = inst
                        break
                    if use.selected is not None:
                        break

                # Check for missing.
                if use.selected is None:
                    sys.stdout.write('\n    Failed to resolve "' + use.package.name + '".\n')
                    sys.exit(1)

        # Just use the first installation of every package.
        for use in ctx.uses:

            # Feature uses get handled a little differently.
            if isinstance(use, FeatureUse):

                # If there is no selected installation then fail.
                if use.use.selected is None:
                    sys.stdout.write('\n    Failed to resolve "' + use.ftr + '".')
                    sys.exit(1)

                # Take the selected installation and see if we can find this
                # feature in its list.
                use.selected = None
                for ftr in use.use.selected.features:
                    if ftr.name == use.feature_name:
                        use.selected = ftr
                        break
                if use.selected is None:
                    sys.stdout.write('\n    Failed to resolve "' + use.ftr + '".')
                    sys.exit(1)
