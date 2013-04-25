#!/usr/bin/env python

##
## The primary entry point.
##

import os, sys, logging
# from use.Options import options
# from use.Use import use
# from use.Default import default
# from use.Rule import rule
from use.Graph import Graph
from use.Use import use
from use.Rule import rule
# from use.Resolver import Resolver

# Setup logging.
logging.basicConfig(level=logging.DEBUG)

# Where has this been launched from?
launch_dir = os.getcwd()
script = os.path.join(launch_dir, 'build.py')
if not os.path.exists(script):
    print('No "build.py" to execute.')
    sys.exit(1)

# I need to create a global graph object to
# be used.
graph = Graph()

# Insert all the global methods and such I want
# available to the user.
globals_dict = {

    # Use shortcuts to insert the graph.
    'use': lambda *a,**k: use(graph,*a,**k),
    'rule': lambda *a,**k: rule(graph,*a,**k),
}

# Try to execute the build script.
locals_dict = {}
# exec(open(script).read(), globals(), locals_dict)
execfile(script, globals_dict, locals_dict)

# Update the graph.
graph.update()

# # Prepare the rules.
# graph.compile()
# graph.search()
# graph.setup_packages()
# graph.build_packages()

# # With the packages having been built we can now
# # try and resolve which versions to use.
# resolver = Resolver()
# resolver(graph)

# # Now we can go back and expand all the productions
# # to have both the correct names and the correct
# # multiplicity.
# graph.post_package_expand()

# # # Get the task master going.
# # task_master = TaskMaster(graph)
# # task_master()

graph.draw_graph()
