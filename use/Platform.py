import os, platform
from .Location import Location
from .utils import strip_missing, run_command

class Platform(object):

    def __init__(self):
        self.base_dirs = []
        self.search_dirs = []
        self.binary_sub_dirs = []
        self.header_sub_dirs = []
        self.library_sub_dirs = []
        self._set_os(platform.system())

    def iter_locations(self, patterns=[]):
        for base in self.base_dirs:
            for bin_dirs in self.binary_sub_dirs:
                for hdr_dirs in self.header_sub_dirs:
                    for lib_dirs in self.library_sub_dirs:
                        yield Location(base, bin_dirs, hdr_dirs, lib_dirs)
        for sd in self.search_dirs:
            for pattern in patterns:
                # TODO: Make this a node.
                ec, stdout, stderr = run_command('find ' + sd + ' -type d -iname "' + pattern + '"')
                for base in stdout.splitlines():
                    yield Location(base, self.binary_sub_dirs, self.header_sub_dirs, self.library_sub_dirs)

    def _set_os(self, os_name):
        getattr(self, '_' + os_name.lower())()

    def _linux(self):
        self._unix()

    def _unix(self):
        self.base_dirs = strip_missing(['/usr', '/opt'])
        self.search_dirs = strip_missing(['/usr/local', '/opt/local', os.environ['HOME']])
        self.binary_sub_dirs = [['bin']]
        self.header_sub_dirs = [['include']]
        self.library_sub_dirs = [['lib'], ['lib64']]

platform = Platform()
