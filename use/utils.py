import sys, os, shlex, errno, tempfile
from subprocess import Popen, PIPE
from Argument import ArgumentCheck

def getarg(name, args, kwargs, required=True):
    if name in kwargs:
        return kwargs.pop(name), args
    elif len(args):
        return args[0], args[1:]
    if required:
        raise KeyError
    return None, args

def split_class(path):
    idx = path.rfind('.')
    cls = path[idx + 1:path.rfind("'")]
    path = path[:idx]
    mod = path[path.find("'") + 1:]
    return mod, cls

def load_class(module_name, class_name=None):
    if not class_name:
        class_name = module_name[module_name.rfind('.') + 1:]
    try:
        tmp_module_name = 'use.packages.' + module_name
        cls = getattr(__import__(tmp_module_name, fromlist=[class_name]), class_name)
    except:
        cls = getattr(__import__(module_name, fromlist=[class_name]), class_name)
    return cls

def strip_missing(dirs):
    return [d for d in dirs if os.path.exists(d)]

def run_command(command, show_stdout=False):
    proc = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE)
    if show_stdout:
        while proc.poll() is None:
            sys.stdout.write(proc.stdout.read())
            sys.stdout.flush()
    stdout, stderr = proc.communicate()
    return (proc.returncode, stdout, stderr)

def make_dirs(path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def conditions_equal(x, y):
    if type(x) != type(y):
        return False
    elif isinstance(x, ArgumentCheck):
        if not x.compare(y):
            return False
    elif isinstance(y, ArgumentCheck):
        if not y.compare(x):
            return False
    else:
        return x == y
    return True
