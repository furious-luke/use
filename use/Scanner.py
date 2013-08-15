import os, re
from File import File

class Scanner(object):

    def __init__(self, ctx):
        self.ctx = ctx

class CScanner(Scanner):

    hdr_re = r'#\s*include\s*(?:<([^>]*)>|"([^"]*)")'
    hdr_prog = re.compile(hdr_re)

    def find_all(self, node, data, bldr):
        for hdr in re.findall(self.hdr_prog, data):
            hdr = hdr[0] or hdr[1]

            # Must be able to locate the header somewhere on
            # the filesystem. Start locally.
            node_base = os.path.dirname(str(node))
            path = os.path.join(node_base, hdr)
            if os.path.exists(path):
                yield self.ctx.file(path)

            # Next try all header dirs.
            else:
                for hdr_dir in bldr.options.get('header_dirs', []):
                    path = os.path.join(hdr_dir, hdr)
                    if os.path.exists(path):
                        yield self.ctx.file(path)
                        break
