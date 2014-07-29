import copy, os
from collections import OrderedDict
from .Argument import ArgumentCheck, Argument
from .conv import to_list

##
## Convert argument based options. Options may be dependent
## on arguments, this method repopulates the option values in
## the dictionary with evaluated arguments.
##
def parse(opts):

    # First replace any argument instances.
    for k, v in opts.iteritems():
        if isinstance(v, (Argument, ArgumentCheck)):
            opts[k] = str(v)

    # Now evaluate any values that need to be replaced. Keep
    # track of whether any substitutions were made in order to
    # recursively expand.
    done = False
    while not done:
        done = True
        for k, v in opts.iteritems():
            if isinstance(v, basestring):
                opts[k] = v.format(**opts)
                if opts[k] != v:
                    done = False

##
## Merge combination of OptionDicts and dicts.
##
def merge(x, y):
    if isinstance(x, OptionDict):
        x = x.get()
    elif x is None:
        x = {}
    else:
        x = dict(x)
    if isinstance(y, OptionDict):
        y = y.get()
    elif y is None:
        y = {}
    x.update(y)
    return x

##
##
##
class Option(object):

    def __init__(self, name=None, short_opts=None, long_opts=None, **kwargs):
        assert short_opts or long_opts
        self.name = name
        self.short_opts = to_list(short_opts)
        self.long_opts = to_list(long_opts)
        if self.name is None:
            if self.short_opts:
                self.name = self.short_opts[0]
            else:
                self.name = self.long_opts[0]
        self.space = kwargs.get('space', True)
        self.text = kwargs.get('text', None)
        self.abspath = kwargs.get('abspath', False)

    def __eq__(self, op):
        if isinstance(op, Option):
            return self.name == op.name
        else:
            return self.name == op or op in self.short_opts or op in self.long_opts

    def __hash__(self):
        return hash(self.name)

    def __call__(self, value, opts={}, short=True):
        opt = self._opt(short)
        str_list = []
        if isinstance(value, bool):
            if value:
                if self.text is not None:
                    str_list.append(self.text.format(**opts))
                else:
                    str_list.append(opt)
        elif isinstance(value, list):
            for v in value:
                self._append(str_list, opt, v)
        else:
            self._append(str_list, opt, value)
        return str_list

    def _append(self, str_list, opt, val):
        if isinstance(val, tuple):
            self._assign(str_list, opt, val[0], val[1])
        else:
            if self.abspath:
                if not os.path.isabs(val):
                    val = os.path.join(os.getcwd(), val)
            if opt:
                if not self.space:
                    str_list.append(opt + str(val))
                else:
                    str_list.append(opt)
            if self.space:
                str_list.append(str(val))

    def _assign(self, str_list, opt, key, val):
        space_bak = self.space
        self.space = False
        if self.space:
            sub_opt = opt + ' ' + key + '='
        else:
            sub_opt = opt + key + '='
        self._append(str_list, sub_opt, val)
        self.space = space_bak

    def _opt(self, short):
        if short and self.short_opts:
            return self.short_opts[0]
        elif self.long_opts:
            return self.long_opts[0]
        return None

##
##
##
class OptionParser(object):

    def __init__(self):
        self._opts = OrderedDict()

    def add(self, opt):
        self._opts[opt.name] = opt

    def __call__(self, bin, *args, **kwargs):

        # Start with the binary name.
        str_list = [bin]

        # The user may have given us a string to process
        # instead of an option dictionary.
        options = {}
        if len(args):
            options = self.make_options_dict(args[0])

        # Insert keyword options.
        options.update(kwargs)

        # Process each option.
        for name, opt in self._opts.iteritems():
            val = options.get(name, None)
            if val is not None:
                str_list.extend(opt(val, options))

        return ' '.join(str_list)

    def make_options_dict(self, opt_str):
        if isinstance(opt_str, (OptionDict, OptionJoin)):
            return opt_str.get()
        elif isinstance(opt_str, dict):
            return dict(opt_str)
        elif opt_str is None:
            return {}
        assert 0, 'Not implemented yet.'

class OptionDict(object):

    def __init__(self, cond=True, **kwargs):
        self.condition = cond
        self._opts = kwargs

    def __repr__(self):
        return str(self.get())

    def __eq__(self, op):
        if type(self) != type(op):
            return False

        # TODO: Fix this condition compare.
        if type(self.condition) != type(op.condition):
            return False
        if isinstance(self.condition, ArgumentCheck):
            if not self.condition.compare(op.condition):
                return False
        elif isinstance(op.condition, ArgumentCheck):
            if not op.condition.coimpare(self.condition):
                return False
        elif self.condition != op.condition:
            return False

        return self._opts == op._opts;

    def __ne__(self, op):
        return not self.__eq__(op)

    def __add__(self, op):
        return OptionJoin(self, op)

    ##
    ## Get a copy of our options. We need to parse the
    ## resulting options if we are the first entry.
    ##
    def get(self, depth=0):

        # Copy our options if we are enabled.
        if bool(self.condition):
            opts = copy.deepcopy(self._opts)
        else:
            opts = {}

        # If we're the ground level, parse the options.
        if depth == 0:
            parse(opts)

        return opts

class OptionJoin(object):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return str(self.get())

    def __eq__(self, op):
        if type(self) != type(op):
            return False
        if self.left != op.left:
            return False
        if self.right != op.right:
            return False
        return True

    def __ne__(self, op):
        return not self.__eq__(op)

    def __add__(self, op):
        return OptionJoin(self, op)

    def get(self, depth=0):

        # Combine children, remembering that the right
        # side trumps the left.
        merged = {}
        self._update(merged, self.left)
        self._update(merged, self.right)

        # If we're the ground level, parse the options.
        if depth == 0:
            parse(merged)

        return merged

    def _update(self, merged, op):
        for k, v in op.get().iteritems():
            if k in merged:
                my_val = merged[k]
                if isinstance(my_val, list):
                    for x in to_list(v):
                        my_val.append(copy.deepcopy(x))
                else:
                    merged[k] = copy.deepcopy(v)
            else:
                merged[k] = copy.deepcopy(v)
