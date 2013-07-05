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

    def expand(self, nodes, options={}):
        return self.version.expand(nodes, options)

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

        # Location handling.
        self.locations = []
        self._potential_locations = []
        self._checked_locations = set()
        self._mine_done = False
        
        # If there are any missing fields, add an empty
        # list to prevent errors.
        for field in ['binaries', 'headers', 'libraries']:
            if not hasattr(self, field):
                setattr(self, field, [])

    def __eq__(self, op):
        return self._ver == op._ver

    ##
    ## Search for locations.
    ##
    def search(self):
        logging.debug('Searching for version ' + self.version)

        # If we havn't already done mine, add them in now.
        if not self._done_mine:
            logging.debug('Adding my own locations.')
            self._done_mine = True
            mine = list(self.iter_locations())
            self._potential_locations.extend(mine)
            logging.debug('Added: ' + str(mine))

        # If there are no new potential locations, return
        # true to indicate we are done.
        if not self._potential_locations:
            return True

        # Search all potential locations.
        while self._potential_locations:
            loc = self._potential_locations.pop(0)
            logging.debug('Starting with location: ' + str(loc))
            self.simplify_location(loc)
            logging.debug('Simplified to: ' + str(loc) )
            if loc not in self._checked_locations:
                self._checked_locations.add(loc)
                if self.footprint(loc):
                    logging.debug('Passed footprint.')
                    self.harvest(loc)
                    self.locations.append(loc)
                else:
                    logging.debug('Failed footprint.')
            else:
                logging.debug('Already checked.')

        # Return false to indicate we had to do some
        # processing. This indicates we need to run search
        # on all the packages again.
        return False

    ##
    ## Iterate over locations. Use this to customise how we search
    ## for installations. By default it will iterate over usual
    ## system locations.
    ##
    def iter_locations(self):
        for loc in platform.iter_locations(self.patterns):
            yield loc

    ##
    ## Reduce location to canonical form. Use this to determine
    ## how best to simplify locations.
    ##
    def simplify_location(self, loc):
        if not self.binaries:
            loc.binary_dirs = []
        if not self.headers:
            loc.header_dirs = []
        if not self.libraries:
            loc.library_dirs = []

    ##
    ## Check if location matches a footprint for this version.
    ##
    def footprint(self, loc):
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

        # # Now check that the version matches.
        # if res:
        #     res = self.check_version(location)
        #     if res:
        #         logging.debug('Version matches.')
        #     else:
        #         logging.debug('Version does not match.')

        # # Create an installation and perform any final checks.
        # if res:
        #     inst = Installation(self, location, binaries=bins, headers=hdrs, libraries=libs)
        #     if self.check_installation(inst):
        #         self.installations.append(inst)
        #         logging.debug('Found valid installation at ' + repr(location))
        #     else:
        #         logging.debug('Installation check failed.')

        return res

    def check_version(self, loc):
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
    def expand(self, nodes, options={}):
        return self.package.expand(nodes, options)

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
    def expand(self, nodes, options={}):
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
        self.expand(graph)

    def expand(self, graph):

        # Get the dependants.
        dependants = graph.successors(self, source=True)
        logging.debug('Search: Expanding dependants %s'%dependants)
        for dep in dependants:
            graph.remove_edge(self, dep)

        # Insert new edges from the found installations to the
        # the old edge destinations.
        for inst in self.package.iter_installations():
            graph.add_edge(self, inst, product=True)
            for dep in dependants:
                graph.add_edge(inst, dep, source=True)

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
