#!/usr/bin/env python

##
## The primary entry point.
##

import os, sys, logging
from use.Context import Context

# Setup logging.
logging.basicConfig(level=logging.DEBUG)

# Where has this been launched from?
launch_dir = os.getcwd()
script = os.path.join(launch_dir, 'build.py')
if not os.path.exists(script):
    print('No "build.py" to execute.')
    sys.exit(1)

# Create the global context.
ctx = Context()

# Insert all the global methods and such I want
# available to the user.
globals_dict = {

    # Use shortcuts to insert 
    'use': ctx.new_use,
    'rule': ctx.new_rule,
}

# Try to execute the build script.
locals_dict = {}
# exec(open(script).read(), globals(), locals_dict)
execfile(script, globals_dict, locals_dict)

# Handle arguments.
ctx.parse_arguments()

# Perform configuration.
ctx.configure()

# Scan for source files.
ctx.scan()

# Expand into products.
ctx.expand()

# If there is a 'post_configure' callable in the locals
# dictionary call it now.
post_cfg = locals_dict.get('post_configure', None)
if post_cfg and callable(post_cfg):
    post_cfg(ctx)

# Find targets to build.
ctx.find_targets()

# Build targets.
ctx.build()
