import os, logging
from .Node import Node
from .Builder import Builder
from .Platform import platform
from .Location import Location
from .Options import Options
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
        self._bins = kwargs.get('binaries', [])
        self._hdrs = kwargs.get('headers', [])
        self._libs = kwargs.get('libraries', [])
        self.features = []

    @property
    def binaries(self):
        return [b[1] for b in self._bins]

    @property
    def headers(self):
        return [h[0] for h in self._hdrs]

    @property
    def libraries(self):
        return [l[0] for l in self._libs]

    @property
    def binary_dirs(self):
        return self.location.binary_dirs

    @property
    def header_dirs(self):
        return self.location.header_dirs

    @property
    def library_dirs(self):
        return self.location.library_dirs

    def __repr__(self):
        text = [
            'binaries: ' + str(self.binaries),
            'headers: ' + str(self.headers),
            'libraries: ' + str(self.libraries)
            ]
        return ', '.join(text)

    ##
    ## Locate any features described by the version.
    ##
    def find_features(self):
        for ftr in self.version.features:
            if ftr.check(self):
                self.features.append(ftr)

    ##
    ## Create productions for nodes.
    ##
    def expand(self, nodes, use_options={}, rule_options={}):
        return self.version.expand(nodes, self, use_options, rule_options)

    ##
    ## Apply this package. An option dictionary will be modified to
    ## have the contents of this package applied to it.
    ##
    def apply(self, prods, use_options={}, rule_options={}):
        for prod in prods:
            bldr = prod[1]
            opts = bldr.options
            if 'compile' in opts:
                self.append_headers(opts)
            else:
                self.append_libraries(opts)

    def append_headers(self, opts):
        hdr_dirs = self.header_dirs
        hdrs = self.headers
        if hdr_dirs:
            dst = opts.setdefault('header_dirs', [])
            for d in hdr_dirs:
                if d not in dst:
                    dst.append(d)
        # if hdrs:
        #     dst = opts.setdefault('headers', [])
        #     for h in hdrs:
        #         if h not in dst:
        #             dst.append(h)

    def append_libraries(self, opts):
        lib_dirs = self.library_dirs
        libs = self.libraries
        if lib_dirs:
            dst = opts.setdefault('library_dirs', [])
            for d in lib_dirs:
                if d not in dst:
                    dst.append(d)
        if libs:
            dst = opts.setdefault('libraries', [])
            for h in libs:
                if h not in dst:
                    dst.append(h)

    def options(self):
        return self.version.options()

##
## Represents a package version. Packages may require
## different methods for configuration depending on
## the version.
##
class Version(object):

    def __init__(self, package):
        self.package = package
        self.installations = []

        # Set my version name.
        if not hasattr(self, 'version'):
            ver = str(self.__class__)
            self.version = ver[ver.rfind('.') + 1:ver.rfind('\'')].lower()

        # Location handling.
        self._potential_installations = []
        self._potential_locations = []
        self._checked_locations = set()
        self._done_mine = False
        
        # If there are any missing fields, add an empty
        # list to prevent errors.
        for field in ['binaries', 'headers', 'libraries']:
            if not hasattr(self, field):
                setattr(self, field, [])

        # Check if patterns have been set.
        if not hasattr(self, 'patterns'):
            self.patterns = '*' + self.package.name + '*'

        # Features describe optional components of a package.
        self.features = []

    def __eq__(self, op):
        return self._ver == op._ver

    def __repr__(self):
        text = []
        for inst in self.installations:
            text.append(str(inst))
        return self.version + '<' + ', '.join(text) + '>'

    ##
    ## Search for locations.
    ##
    def search(self):
        logging.debug('Package: Searching for version: ' + self.version)

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
            logging.debug('Simplified to: ' + str(loc))

            # Make sure we havn't already checked it.
            already_checked = False
            for cl in self._checked_locations:
                if loc == cl:
                    already_checked = True
                    break
            if already_checked:
                logging.debug('Already checked.')
                continue

            # Check now.
            self._checked_locations.add(loc)
            res, bins, hdrs, libs = self.footprint(loc)
            if res:
                logging.debug('Passed footprint.')
                inst = Installation(self, loc,
                                    binaries=zip(self.binaries, bins),
                                    headers=zip(self.headers, hdrs),
                                    libraries=zip(self.libraries, libs[0], libs[1]))
                self._potential_installations.append(inst)
                self.harvest(inst)
            else:
                logging.debug('Failed footprint.')

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
        logging.debug('Package: Checking location: ' + repr(loc))

        # First check if all the required files exist.
        bins = []
        hdrs = []
        libs = []
        res, bins = self.find_binaries(self.binaries, loc.binary_dirs)
        if res:
            res, hdrs = self.find_headers(self.headers, loc.header_dirs)
        if res:
            res = self.find_libraries(self.libraries, loc.library_dirs)
            libs = res[1:]
            res = res[0]

        return (res, bins, hdrs, libs)

    ##
    ## Extract information about other packages. Some packages may contain
    ## some additional information about other packages on the machine. For
    ## example, mpich knows about compilers.
    ##
    def harvest(self, inst):
        pass

    ##
    ## Check locations for validity. The search method will find locations that
    ## pass the footprint test, then check will perform as throrough checking
    ## as is possible to make sure the package is correct.
    ##
    def check(self):
        for inst in self._potential_installations:
            
            # Now check that the version matches.
            res = self.check_version(inst)
            if res:
                logging.debug('Version matches.')
            else:
                logging.debug('Version does not match.')

            # Create an installation and perform any final checks.
            if res:
                if self.check_installation(inst):
                    self.installations.append(inst)
                    logging.debug('Found valid installation: ' + repr(inst))

                    # Now we can search for features of the installation.
                    inst.find_features()

                else:
                    logging.debug('Installation check failed.')

    def check_version(self, loc):
        return True

    ##
    ## Perform full installation check.
    ##
    def check_installation(self, inst):
        return True

    ##
    ##
    ##
    def find_binaries(self, bins, bin_dirs):
        logging.debug('Searching for binaries: ' + repr(bins))
        res = self._find_files(bins, bin_dirs)
        if not res[0]:
            logging.debug('Failed to find binary: ' + str(res[2]))
        else:
            logging.debug('Found all binaries.')
        return res[:-1]

    ##
    ##
    ##
    def find_headers(self, hdrs, hdr_dirs):
        logging.debug('Searching for headers: ' + repr(hdrs))
        res = self._find_files(hdrs, hdr_dirs)
        if not res[0]:
            logging.debug('Failed to find header: ' + str(res[2]))
        else:
            logging.debug('Found all headers.')
        return res[:-1]

    ##
    ##
    ##
    def find_libraries(self, libs, lib_dirs):
        logging.debug('Searching for libraries: ' + repr(libs))
        static_libs = [platform.make_static_library(l) for l in libs]
        shared_libs = [platform.make_shared_library(l) for l in libs]
        static_res = self._find_files(static_libs, lib_dirs)
        shared_res = self._find_files(shared_libs, lib_dirs)

        # If I couldn't find a complete set of static and shared, try
        # and make a complete set out of the partial ones.
        if not static_res[0] and not shared_res[0]:
            combined = []
            for st, sh, lib in zip(static_res[1], shared_res[1], libs):
                if sh:
                    combined.append(sh)
                elif st:
                    combined.append(st)
                else:
                    logging.debug('Failed to find library: ' + lib)
                    return (False, static_res, shared_res)
            logging.debug('Found combination of static and shared.')
            return (True, static_res, shared_res)

        # Clear out any failures.
        if not static_res[0]:
            static_libs = []
        else:
            static_libs = static_res[1]
        if not shared_res[1]:
            shared_libs = []
        else:
            shared_libs = shared_res[1]

        logging.debug('Found all libraries.')
        return (True, static_libs, shared_libs)

    ##
    ## Calculate the products of nodes. By default this
    ## will call the package's productions.
    ##
    def expand(self, nodes, inst, use_options={}, rule_options={}):
        return self.package.expand(nodes, self, inst, use_options, rule_options)

    ##
    ##
    ##
    def _find_files(self, files, dirs):
        files = to_list(files)
        dirs = to_list(dirs)

        # Keep a list of the full path to the found
        # files.
        found_paths = []
        found_all = True
        missing = []

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

            # If we couldn't find it, insert None.
            if not found:
                found_paths.append(None)
                missing.append(fl)
                found_all = False

        # Success, all headers found.
        return (found_all, found_paths, missing)

    ##
    ## Return the options object for this version.
    ##
    def options(self):
        return self.package.options()

    def _builder(self, sources, targets=[]):
        bldr = getattr(self, 'default_builder', self.package.default_builder)
        return bldr(sources, targets, self._actions(sources, targets))

##
## Package configuration. Embodies the process of locating
## specific packages and storing all locations with as much
## information as possible.
##
class Package(object):

    def __init__(self):
        super(Package, self).__init__()
        self.name = self.__class__.__name__
        self.versions = [v(self) for v in self.versions]
        self._opts = Options()

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
        text = []
        for ver in self.versions:
            text.append(str(ver))
        return self.name + '<' + ', '.join(text) + '>'

    def iter_installations(self):
        for ver in self.versions:
            for inst in ver.installations:
                yield inst

    ##
    ## Default productions operation. Each version may have its
    ## own production rules. However they can also just refer to
    ## this default operation.
    ##
    def expand(self, nodes, vers, inst, use_options={}, rule_options={}):
        assert 0, 'Should never get to this one.' 

    def search(self):
        logging.debug('Performing package search for %s'%self.name)
        done = True
        for ver in self.versions:
            if not ver.search():
                done = False
        return done

    def check(self):
        for ver in self.versions:
            ver.check()

    ##
    ## Return the options object for this package.
    ##
    def options(self):
        return self._opts

    def merge_options(self, vers, *args):

        # Make new dictionary out of first argument.
        if isinstance(args[0], dict):
            opts = dict(args[0])
        else:
            opts = vers.options().make_options_dict(args[0])

        # Update with remaining options.
        for o in args[1:]:
            opts.update(vers.options().make_options_dict(o))

        return opts

    ##
    ## Add arguments to parser.
    ##
    def add_arguments(self, parser):
        name = self.name.lower()

        # Add base directory selection.
        parser.add_argument('--' + name + '-dir', dest=name + '-dir',
                            help='Specify base directory for %s.'%self.name)

        # Check for usage of headers, binaries or libraries.
        for attr, arg, help in [('binaries', '-bin-dir', 'Specify binary directory for %s.'),
                                ('headers', '-inc-dir', 'Specify include directory for %s.'),
                                ('libraries', '-lib-dir', 'Specify library directory for %s.')]:
            has = False
            if getattr(self, attr, None):
                has_hdrs = True
            else:
                for ver in self.versions:
                    if getattr(ver, attr, None):
                        has = True
                        break
            if has:
                parser.add_argument('--' + name + arg, dest=name + arg, help=help%self.name)

    ##
    ##
    ##
    def parse_arguments(self, args):
        name = self.name.lower()

        # Get the arguments.
        base = getattr(args, name + '-dir', None)
        inc_dir = getattr(args, name + '-inc-dir', None)
        lin_dir = getattr(args, name + '-lib-dir', None)

# ##
# ##
# ##
# class Search(Node):

#     def __init__(self, package):
#         super(Search, self).__init__()
#         self.package = package

#     ##
#     ## Locate the package. Use the set of versions given to a
#     ## package to search common locations for installations.
#     ##
#     def update(self, graph):
#         logging.debug('Searching for %s'%self.package)

#         # Let the package perform the search operations. This
#         # must be like this because the only the package and
#         # versions know how to search.
#         self.package.search()
#         self.expand(graph)

#     def expand(self, graph):

#         # Get the dependants.
#         dependants = graph.successors(self, source=True)
#         logging.debug('Search: Expanding dependants %s'%dependants)
#         for dep in dependants:
#             graph.remove_edge(self, dep)

#         # Insert new edges from the found installations to the
#         # the old edge destinations.
#         for inst in self.package.iter_installations():
#             graph.add_edge(self, inst, product=True)
#             for dep in dependants:
#                 graph.add_edge(inst, dep, source=True)

#     def __repr__(self):
#         text = 'Search(' + repr(self.package) + ')'
#         return text

# ##
# ##
# ##
# class Install(Builder):
#     pass

# ##
# ##
# ##
# class Download(Builder):
#     pass
