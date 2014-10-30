#!/usr/bin/env python2

import code, os, sys, platform

# If we are unable to import directly, try
# to modify the path to do so.
try:
    from use.Context import Context
except:
    sys.path.insert(0, os.path.join(sys.path[0], '..', '..'))
    from use.Context import Context

from use.Platform import platform
from use.Argument import Argument
from use.Node import Always

no_startup = False

# Set up a dictionary to serve as the environment for the shell, so
# that tab completion works on objects that are imported at runtime.
imported_objects = {}
try:  # Try activating rlcompleter, because it's handy.
    import readline
except ImportError:
    pass
else:
    # We don't have to wrap the following import in a 'try', becausels
    # we already know 'readline' was imported successfully.
    import rlcompleter
    readline.set_completer(rlcompleter.Completer(imported_objects).complete)
    readline.parse_and_bind("tab:complete")

# We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
# conventions and get $PYTHONSTARTUP first then .pythonrc.py.
if not no_startup:
    for pythonrc in (os.environ.get("PYTHONSTARTUP"), '~/.pythonrc.py'):
        if not pythonrc:
            continue
            pythonrc = os.path.expanduser(pythonrc)
            if not os.path.isfile(pythonrc):
                continue
            try:
                with open(pythonrc) as handle:
                    exec(compile(handle.read(), pythonrc, 'exec'), imported_objects)
            except NameError:
                pass

# Where has this been launched from?
launch_dir = os.getcwd()
script = os.path.join(launch_dir, 'usescript.py')
if not os.path.exists(script):
    script = None

# Need a context.
ctx = Context()
ctx.verbose = False
ctx.shell = True

# Insert all the global methods and such I want
# available to the user.
identity = ctx.new_use('identity')
identity.package.explicit = False
files = ctx.new_use('files')
files.package.explicit = False
dummies = type('dummies', (object,), dict(always=Always))
globals_dict = {
    'list_packages': ctx.list_packages,
    'platform': platform,
    'argument': ctx.arguments,
    'options': ctx.new_options,
    'use': ctx.new_use,
    'rule': ctx.new_rule,
    'targets': Argument('targets', ctx),
    'files': files,
    'identity': identity,
    'dummies': dummies,
    'configure': ctx.configure,
    'print_rules': ctx.print_rule_tree,
}

# Try to execute the build script.
locals_dict = {}
if script is not None:
    execfile(script, globals_dict, locals_dict)

imported_objects.update(globals_dict)
imported_objects.update(locals_dict)
code.interact(local=imported_objects)