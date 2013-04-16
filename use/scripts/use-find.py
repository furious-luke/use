#!/usr/bin/env python

##
## The primary entry point.
##

import os, sys, logging
from use.utils import load_class

# Setup logging.
#logging.basicConfig(level=logging.DEBUG)

# Load the package class
try:
    pkg_class = load_class(sys.argv[1])
except ImportError:
    print 'Unable to find a package class for "%s".'%sys.argv[1]
    sys.exit(1)
pkg = pkg_class()

# Search for installations.
pkg.build()

# Report results.
insts = list(pkg.iter_installations())
print 'Search for package %s yielded %d result%s.'%(sys.argv[1], len(insts), '' if len(insts) == 1 else 's')
for inst in insts:
    print 2*' ' + inst.version.version
    print 4*' ' + str(inst.location)
    if inst.binaries:
        print 4*' ' + 'binaries: ' + str(inst.binaries)
    if inst.headers:
        print 4*' ' + 'headers: ' + str(inst.headers)
    if inst.libraries:
        print 4*' ' + 'libraries: ' + str(inst.libraries)
