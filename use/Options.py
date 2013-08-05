from collections import OrderedDict
from .conv import to_list

##
##
##
class Option(object):

    def __init__(self, name=None, short_opts=None, long_opts=None, **kwargs):
        self.name = name
        self.short_opts = to_list(short_opts)
        self.long_opts = to_list(long_opts)
        if self.name is None:
            if self.short_opts:
                self.name = self.short_opts[0]
            else:
                self.name = self.long_opts[0]
        self.space = kwargs.get('space', True)

    def __eq__(self, op):
        if isinstance(op, Option):
            return self.name == op.name
        else:
            return self.name == op or op in self.short_opts or op in self.long_opts

    def __hash__(self):
        return hash(self.name)

    def __call__(self, value, short=True):
        opt = self._opt(short)
        str_list = []
        if isinstance(value, bool) and value:
            str_list.append(opt)
        elif isinstance(value, (list, tuple)):
            for v in value:
                self._append(str_list, opt, v)
        else:
            self._append(str_list, opt, value)
        return str_list

    def _append(self, str_list, opt, val):
        if opt:
            if not self.space:
                str_list.append(opt + str(val))
            else:
                str_list.append(opt)
        if self.space:
            str_list.append(str(val))

    def _opt(self, short):
        if short and self.short_opts:
            return self.short_opts[0]
        elif self.long_opts:
            return self.long_opts[0]
        return None

    # def _expand(self, vals, flag):
    #     return [flag + v for v in vals]

##
##
##
class Options(object):

    def __init__(self, binary=''):
        self.binary = binary
        self._opts = OrderedDict()

    def add(self, opt):
        self._opts[opt.name] = opt

    def __call__(self, *args, **kwargs):

        # Start with the binary name.
        str_list = [self.binary]

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
                str_list.extend(opt(val))

        return ' '.join(str_list)

    def make_options_dict(self, opt_str):
        if isinstance(opt_str, dict):
            return opt_str
        opt_dict = {}
        for o in opt_str.split():
            for opt in self._opts.itervalues():
                if opt == o:
                    opt_dict[opt.name] = True
                    break
        return opt_dict
