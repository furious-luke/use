#!/usr/bin/env python

##
## The primary entry point.
##

import os, sys, logging
from Build.Options import options
from Build.Use import use
from Build.Default import default
from Build.Rules import Rules

# Setup logging.
logging.basicConfig(level=logging.DEBUG)

# Where has this been launched from?
launch_dir = os.getcwd()
script = os.path.join(launch_dir, 'build.py')
if not os.path.exists(script):
    print 'No "build.py" to execute.'
    sys.exit(1)

# Setup the locals dictionary.
locals_dict = {
    'options': options,
}

# Try to execute the build script.
locals_dict = {}
execfile(script, globals(), locals_dict)

# Prepare the rules.
rules = Rules()
rules.compile(locals_dict['rules'])
rules.search()
rules.setup_packages()
rules.build_packages()

# rules.draw_graph()
