import os, logging
from Node import Node
from Builder import Builder
from Platform import platform
from Location import Location
from conv import to_list
from utils import strip_missing

##
## A package installation. Packages may have multiple
## installations on a single machine. We need an object
## to represent each installation.
##
class Installation(object):

    def __init__(self, version, location, **kwargs):
        self.version = version
        self.location = location
        self.binaries = []
        self.headers = []
        self.libraries = []

##
## Represents a package version. Packages may require
## different methods for configuration depending on
## the version.
##
class Version(object):

    def __init__(self, package):
        self.package = package
        self.installations = []
        self.patterns = []
        self._checked_locations = set()

    def __eq__(self, op):
        return self._ver == op._ver

    ##
    ## Search for installations.
    ##
    def search(self):
        logging.debug('Searching for version ' + self.version)
        for loc in self.iter_locations():
            if loc not in self._checked_locations:
                self.check_location(loc)
                self._checked_locations.add(loc)

    def iter_locations(self):
        for loc in platform.iter_locations(self.patterns):
            yield loc

    def check_location(self, location):
        logging.debug('Checking location ' + repr(location))

        # First check if all the required files exist.
        res = self.find_binaries(getattr(self, 'binaries', []), location.binary_dirs)
        if res[0]:
            res = self.find_headers(getattr(self, 'headers', []), location.header_dirs)
        if res[0]:
            res = self.find_libraries(getattr(self, 'libraries', []), location.library_dirs)

        # Now check that the version matches.
        if res[0]:
            res = self.check_version(location)

        # Create an installation and perform any final checks.
        if res[0]:
            inst = Installation(self, location)
            if self.check_installation(inst):
                self.installations.append(inst)
                logging.debug('Found valid installation at ' + repr(location))

        return res[0]

    def check_version(self, location):
        return (True, None)

    def check_installation(self, inst):
        return True

    ##
    ##
    ##
    def find_binaries(self, bins, bin_dirs):
        logging.debug('Searching for binaries: ' + repr(bins))
        res = self._find_files(bins, bin_dirs)
        if not res:
            logging.debug('Failed to find binary: ', res[1])
        # if not res[0]:
        #     inst.set_missing_binary(res[1])
        # else:
        #     inst.set_binary_dirs(res[1])
        return res

    ##
    ##
    ##
    def find_headers(self, hdrs, hdr_dirs):
        logging.debug('Searching for headers: ' + repr(hdrs))
        res = self._find_files(hdrs, hdr_dirs)
        if not res:
            logging.debug('Failed to find header: ', res[1])
        # if not res[0]:
        #     inst.set_missing_header(res[1])
        # else:
        #     inst.set_header_dirs(res[1])
        return res

    ##
    ##
    ##
    def find_libraries(self, libs, lib_dirs):
        logging.debug('Searching for libraries: ' + repr(libs))
        res = self._find_files(libs, lib_dirs)
        if not res:
            logging.debug('Failed to find library: ', res[1])
        # if not res[0]:
        #     inst.set_missing_library(res[1])
        # else:
        #     inst.set_library_dirs(res[1])
        return res

    ##
    ##
    ##
    def _find_files(self, files, dirs):
        files = to_list(files)
        dirs = to_list(dirs)

        # Track all directories that contain these files.
        found_dirs = {}

        # Must be able to find all required headers.
        for fl in files:

            # Each directory needs to be checked.
            found = False
            for dr in dirs:

                # Does the file exist in this directory?
                path = os.path.join(dr, fl)
                if os.path.exists(path):
                    found = True
                    found_dirs[fl] = dr
                    break

            # If we failed to find this header we
            # need to fail and store which header
            # we couldn't find.
            if not found:
                return (False, fl)

        # Success, all headers found.
        return (True, found_dirs)

    def _builder(self, sources, targets=[]):
        bldr = getattr(self, 'default_builder', self.package.default_builder)
        return bldr(sources, targets, self._actions(sources, targets))

##
## Package configuration. Embodies the process of locating
## specific packages and storing all locations with as much
## information as possible.
##
class Package(Node):

    def __init__(self):
        self.name = self.__class__.__name__
        self.installs = []
        self.versions = [v(self) for v in self.versions]

    ##
    ## Default package usage. Try to determine the correct
    ## action for the provided source/s. By default it will
    ## just return an instantiation of the class 'Builder'
    ## attached to this object.
    ##
    def __call__(self, source, target=None):
        sources = to_list(source)
        targets = to_list(target)
        return self.versions[-1]._builder(sources, targets)

    def __repr__(self):
        text = self.name
        return text

    def binaries(self):
        pass

    def libraries(self):
        pass

    def headers(self):
        pass

    def build(self):
        logging.debug('Building package ' + self.name)
        for ver in self.versions:
            ver.search()

##
##
##
class PackageBuilder(Builder):

    def __init__(self, package):
        self.package = package

    ##
    ## Locate the package. Use the set of versions given to a
    ## package to search common locations for installations.
    ##
    def __call__(self):
        for ver in self.pkg.versions:
            ver.search()

    def __repr__(self):
        text = 'PackageBuilder(' + repr(self.package) + ')'
        return text
