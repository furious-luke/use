import os, logging
from .Node import Node
from .Builder import Builder
from .Platform import platform
from .Location import Location
from .conv import to_list
from .utils import strip_missing

##
## A package installation. Packages may have multiple
## installations on a single machine. We need an object
## to represent each installation.
##
class Installation(Node):

    def __init__(self, version=None, location=None, **kwargs):
        super(Installation, self).__init__()
        self.version = version
        self.location = location
        self.binaries = kwargs.get('binaries', [])
        self.headers = kwargs.get('headers', [])
        self.libraries = kwargs.get('libraries', [])

    def __repr__(self):
        return 'Installation'

    def productions(self, nodes, options={}):
        return self.version.productions(nodes, options)

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
        
        # If there are any missing fields, add an empty
        # list to prevent errors.
        for field in ['binaries', 'headers', 'libraries']:
            if not hasattr(self, field):
                setattr(self, field, [])

    def __eq__(self, op):
        return self._ver == op._ver

    ##
    ## Search for installations.
    ##
    def search(self):
        logging.debug('Searching for version ' + self.version)
        for loc in self.iter_locations():
            self.simplify_location(loc)
            if loc not in self._checked_locations:
                self.check_location(loc)
                self._checked_locations.add(loc)

    def iter_locations(self):
        for loc in platform.iter_locations(self.patterns):
            yield loc

    def simplify_location(self, location):
        if not self.binaries:
            location.binary_dirs = []
        if not self.headers:
            location.header_dirs = []
        if not self.libraries:
            location.library_dirs = []

    def check_location(self, location):
        logging.debug('Checking location ' + repr(location))

        # First check if all the required files exist.
        bins = []
        hdrs = []
        libs = []
        res, bins = self.find_binaries(self.binaries, location.binary_dirs)
        if res:
            res, hdrs = self.find_headers(self.headers, location.header_dirs)
        if res:
            res, libs = self.find_libraries(self.libraries, location.library_dirs)

        # Now check that the version matches.
        if res:
            res = self.check_version(location)
            if res:
                logging.debug('Version matches.')
            else:
                logging.debug('Version does not match.')

        # Create an installation and perform any final checks.
        if res:
            inst = Installation(self, location, binaries=bins, headers=hdrs, libraries=libs)
            if self.check_installation(inst):
                self.installations.append(inst)
                logging.debug('Found valid installation at ' + repr(location))
            else:
                logging.debug('Installation check failed.')

        return res

    def check_version(self, location):
        return True

    def check_installation(self, inst):
        return True

    ##
    ##
    ##
    def find_binaries(self, bins, bin_dirs):
        logging.debug('Searching for binaries: ' + repr(bins))
        res = self._find_files(bins, bin_dirs)
        if not res[0]:
            logging.debug('Failed to find binary: ' + res[1])
        else:
            logging.debug('Found all binaries.')
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
        if not res[0]:
            logging.debug('Failed to find header: ' + res[1])
        else:
            logging.debug('Found all headers.')
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
        if not res[0]:
            logging.debug('Failed to find library: ' + res[1])
        else:
            logging.debug('Found all libraries.')
        # if not res[0]:
        #     inst.set_missing_library(res[1])
        # else:
        #     inst.set_library_dirs(res[1])
        return res

    ##
    ## Calculate the products of nodes. By default this
    ## will call the package's productions.
    ##
    def productions(self, nodes, options={}):
        return self.package.productions(nodes, options)

    ##
    ##
    ##
    def _find_files(self, files, dirs):
        files = to_list(files)
        dirs = to_list(dirs)

        # Keep a list of the full path to the found
        # files.
        found_paths = []

        # Must be able to find all required headers.
        for fl in files:

            # Each directory needs to be checked.
            found = False
            for dr in dirs:

                # Does the file exist in this directory?
                path = os.path.join(dr, fl)
                logging.debug('Checking for ' + path)
                if os.path.exists(path):
                    logging.debug('Found it.')
                    found = True
                    found_paths.append(os.path.join(dr, fl))
                    break

            # If we failed to find this header we
            # need to fail and store which header
            # we couldn't find.
            if not found:
                return (False, fl)

        # Success, all headers found.
        return (True, found_paths)

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
        super(Package, self).__init__()
        self.name = self.__class__.__name__
        self.installs = []
        self.versions = [v(self) for v in self.versions]

    ##
    ## Packages use their class type for comparison. This is
    ## to make sure only one exists in the graph at any time.
    ## The Package object is used to represent ALL packages of
    ## the given type.
    ##
    def __eq__(self, op):
        return self.__class__ == op.__class__
    def __hash__(self):
        return hash(self.__class__)

    ##
    ## Default package usage. Try to determine the correct
    ## action for the provided source/s. By default it will
    ## just return an instantiation of the class 'Builder'
    ## attached to this object.
    ##
    # def __call__(self, source, target=None):
    #     sources = to_list(source)
    #     targets = to_list(target)
    #     return self.versions[-1]._builder(sources, targets)

    def __repr__(self):
        text = self.name
        return text

    def iter_installations(self):
        for ver in self.versions:
            for inst in ver.installations:
                yield inst

    def binaries(self):
        pass

    def libraries(self):
        pass

    def headers(self):
        pass

    ##
    ## Default productions operation. Each version may have its
    ## own production rules. However they can also just refer to
    ## this default operation.
    ##
    def productions(self, nodes, options={}):
        assert 0, 'Should never get to this one.' 

    def search(self):
        logging.debug('Performing package search for %s'%self.name)
        for ver in self.versions:
            ver.search()

##
##
##
class Search(Node):

    def __init__(self, package):
        super(Search, self).__init__()
        self.package = package

    ##
    ## Locate the package. Use the set of versions given to a
    ## package to search common locations for installations.
    ##
    def update(self, graph):
        logging.debug('Searching for %s'%self.package)

        # Let the package perform the search operations. This
        # must be like this because the only the package and
        # versions know how to search.
        self.package.search()

        # # Set the products in the graph.
        # graph.set_products(self, self.package.installations)

    def __repr__(self):
        text = 'Search(' + repr(self.package) + ')'
        return text

##
##
##
class Install(Builder):
    pass

##
##
##
class Download(Builder):
    pass
