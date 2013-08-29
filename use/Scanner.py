import os, re
from File import File

class Scanner(object):

    def __init__(self, ctx):
        self.ctx = ctx

class CScanner(Scanner):

    hdr_re = r'#\s*include\s*(?:<([^>]*)>|"([^"]*)")'
    hdr_prog = re.compile(hdr_re)

    def find_all(self, node, data, bldr, found=None):
        if found is None:
            found = set()
        for hdr in re.findall(self.hdr_prog, data):
            hdr = hdr[0] or hdr[1]

            # Must be able to locate the header somewhere on
            # the filesystem. Start locally.
            node_base = os.path.dirname(str(node))
            path = os.path.join(node_base, hdr)
            cur_node = self.ctx.find_node(path)
            if cur_node is not None:
                if cur_node in found:
                    continue
                yield cur_node

            # Next try all header dirs.
            else:
                for hdr_dir in bldr.options.get('header_dirs', []):
                    path = os.path.join(hdr_dir, hdr)
                    cur_node = self.ctx.find_node(path)
                    if cur_node is not None:
                        if cur_node in found:
                            cur_node = None
                            break
                        yield cur_node
                        break

            # If we found it, rip out all the headers in THIS header
            # too.
            if cur_node is not None:

                # Add to the found set.
                found.add(cur_node)

                # If the node has sources, scan those instead.
                if cur_node.builder is not None:
                    srcs = cur_node.builder.sources
                else:
                    srcs = [cur_node]

                # Scan sub-headers of existing sources.
                for src in srcs:
                    hdr_data = None
                    try:
                        with open(str(src), 'r') as hdr_file:
                            hdr_data = hdr_file.read()
                    except IOError:
                        pass
                    if hdr_data is not None:
                        for f in self.find_all(cur_node, hdr_data, bldr, found):
                            yield f
