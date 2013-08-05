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

    def __repr__(self):
        return 'resolver'

    ##
    ##
    ##
    def __call__(self, ctx):
        logging.debug('Resolving package installations.')

        # Just use the first installation of every package.
        for use in ctx.uses:

            # Get the first installation.
            use.selected = None
            for ver in use.package.versions:
                for inst in ver.installations:
                    use.selected = inst
                    break
                if use.selected:
                    break

            # Check for missing.
            if not use.selected:
                print 'Could not find valid installation.'
                sys.exit(1)
