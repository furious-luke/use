#!/usr/bin/env python

##
## The primary entry point.
##

import os, sys, logging
from use.Options import options
from use.Use import use
from use.Default import default
from use.Rules import Rules

# Setup logging.
logging.basicConfig(level=logging.DEBUG)

# Where has this been launched from?
launch_dir = os.getcwd()
script = os.path.join(launch_dir, 'build.py')
if not os.path.exists(script):
    print('No "build.py" to execute.')
    sys.exit(1)

# Setup the locals dictionary.
locals_dict = {
    'options': options,
}

# Try to execute the build script.
locals_dict = {}
exec(open(script).read(), globals(), locals_dict)

# Prepare the rules.
rules = Rules()
rules.compile(locals_dict['rules'])
rules.search()
rules.setup_packages()
rules.build_packages()

rules.draw_graph()
