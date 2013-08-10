import os, shlex, errno
from subprocess import Popen, PIPE

def getarg(name, args, kwargs, required=True):
    if name in kwargs:
        return kwargs.pop(name), args
    elif len(args):
        return args[0], args[1:]
    if required:
        raise KeyError
    return None, args

def load_class(module_name, class_name=None):
    if not class_name:
        class_name = module_name[module_name.rfind('.') + 1:]
    try:
        klass = getattr(__import__(module_name, fromlist=[class_name]), class_name)
    except:
        module_name = 'use.packages.' + module_name
        klass = getattr(__import__(module_name, fromlist=[class_name]), class_name)
    return klass

def strip_missing(dirs):
    return [d for d in dirs if os.path.exists(d)]

def run_command(command):
    proc = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE)
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
