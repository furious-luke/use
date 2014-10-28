from Options import OptionParser
from conv import to_list
from utils import findattr

##
## Handles creation of productions.
##
class Producer(object):

    def __init__(self, version):
        self.version = version
        self.source_pattern = findattr('source_pattern', self, [])
        self.target_pattern = findattr('target_pattern', self, [])
        self.option_parser = OptionParser()

    def __repr__(self):
        s = self.source_pattern
        if s:
            s = ', '.join(to_list(s))
        else:
            s = '?'
        t = self.target_pattern
        if t:
            t = ', '.join(to_list(t))
        else:
            t = '?'
        return '"%s" -> "%s"'%(s, t)

    def __call__(self, nodes, inst, use_opts={}, rule_opts={}):

        # Don't do anything if there are no sources.
        if not nodes:
            return None

        # Merge any options together.
        opts = self.merge_options(inst.version, use_opts, rule_opts)

        # Call productions code.
        return self.make_productions(nodes, inst, opts)

    def __eq__(self, op):
        return self.__class__ == op.__class__

    def match(self, nodes):
        for node in nodes:
            okay = False
            for sp in to_list(self.source_pattern):
                prog = re.compile(sp)
                if prog.match(str(node)):
                    okay = True
                    break
            if not okay:
                return False
        return True

    def option(self, *args, **kwargs):
        return self.option_parser.add(*args, **kwargs)

    ##
    ## Transform sources to production tuples.
    ##
    def make_productions(self, nodes, inst, opts, single=False, **kwargs):

        # Modify the single flag by any single option.
        single = opts.get('single', single)

        # If we don't have a default builder or default target
        # node type then bail.
        default_builder     = self._findattr('default_builder')
        default_target_node = self._findattr('default_target_node')
        if not default_builder or not default_target_node:
            return None

        # We need either a destination suffix or a prefix in order
        # to successfully transform a file.
        suf = opts.get('suffix', self._findattr('default_target_suffix'))
        pre = opts.get('prefix', '')
        tgt = opts.get('target', '')
        if not suf and not pre and (single and not tgt):
            sys.stdout.write('Package: Can\'t process productions, they would overwrite the original files.\n')
            sys.exit(1)
            return None

        dir_strip     = opts.get('target_strip_dirs',     0)
        suf_dir_strip = opts.get('target_strip_suf_dirs', None)
        tgt_pre       = opts.get('target_prefix',         None)

        # Either single or multi.
        prods = []
        if not single:
            target = opts.get('target', None)
            opts['targets'] = [target] if target is not None else []
            for node in nodes:
                if target is None:
                    src_fn, src_suf = os.path.splitext(node.path)
                    src = src_fn + (suf if suf is not None else src_suf)
                    new_src_lst = [d for i, d in enumerate([d for d in src.split('/') if d]) if i >= dir_strip]
                    if suf_dir_strip is not None:
                        new_src_lst = new_src_lst[:-1 - suf_dir_strip] + [new_src_lst[-1]]
                    new_src = '/'.join(new_src_lst)
                    if src[0] == '/' and dir_strip == 0:
                        new_src = '/' + new_src
                    if tgt_pre is not None:
                        new_src = os.path.join(tgt_pre, new_src)
                    dst = os.path.join(pre, new_src)
                    cur_target = self.ctx.node(default_target_node, dst)
                    opts['targets'].append(cur_target)
                else:
                    cur_target = target()
                prods.append(((node,),
                              default_builder(self.ctx, node, cur_target, inst.actions(node, cur_target, opts), opts, **kwargs),
                              (cur_target,)))
        else:
            target = opts.get('target', None)
            target = os.path.join(pre, target)
            target = self.ctx.node(default_target_node, target)
            opts['target'] = target
            prods.append((list(nodes),
                          default_builder(self.ctx, nodes, target, inst.actions(nodes, target, opts), opts, **kwargs),
                          (target,)))

        logging.debug('Package: Done making productions.')
        return prods

    def _findattr(self, name):
        return findattr(name, (self, inst, self.version, self.version.package))
