import os

class Location(object):

    def __init__(self, base, bin_dirs, hdr_dirs, lib_dirs):
        self.base = base
        self.binary_dirs = list(self._iter_dirs(bin_dirs))
        self.header_dirs = list(self._iter_dirs(hdr_dirs))
        self.library_dirs = list(self._iter_dirs(lib_dirs))

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, op):
        return (self.base == op.base and
                self.binary_dirs == op.binary_dirs and
                self.header_dirs == op.header_dirs and
                self.library_dirs == op.library_dirs)

    def __repr__(self):
        text = {
            'base': self.base,
            'binary_dirs': self.binary_dirs,
            'header_dirs': self.header_dirs,
            'library_dirs': self.library_dirs
        }
        return repr(text)

    def _iter_dirs(self, dirs):
        for d in dirs:
            if os.path.isabs(d):
                path = d
            else:
                path = os.path.join(self.base, d)
            if os.path.exists(path):
                yield path
