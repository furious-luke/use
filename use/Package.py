import sys, os, pickle, logging
from .Node import Node
from .Builder import Builder
from .Platform import platform
from .Location import Location
from .Options import OptionParser
from .conv import to_list
from .utils import strip_missing, make_dirs

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
        self._ftr_map = {}

    def __repr__(self):
        text = [
            'binaries: ' + str(self.binaries),
            'headers: ' + str(self.headers),
            'libraries: ' + str(self.libraries)
            ]
        return ', '.join(text)

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

    ##
    ## Locate any features described by the version.
    ##
    def find_features(self):
        for ftr in self.version.features:
            if ftr.check(self):
                self.features.append(ftr)
                self._ftr_map[ftr.name] = ftr
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
                if 'shared_lib' in opts:
                    self.append_rpaths(opts)

    def actions(self, *args, **kwargs):
        return self.version.actions(self, *args, **kwargs)

    def append_headers(self, opts):
        hdr_dirs = self.header_dirs
        hdrs = self.headers
        if hdr_dirs:
            dst = opts.setdefault('header_dirs', [])
            for d in hdr_dirs:
                if d not in dst and d not in platform.system_header_dirs:
                    dst.append(d)

    def append_libraries(self, opts):
        lib_dirs = self.library_dirs
        libs = self.libraries
        if lib_dirs:
            dst = opts.setdefault('library_dirs', [])
            for d in lib_dirs:
                if d not in dst and d not in platform.system_library_dirs:
                    dst.append(d)
        if libs:
            dst = opts.setdefault('libraries', [])
            for h in libs:
                if h not in dst:
                    dst.append(h)

    def append_rpaths(self, opts):
        lib_dirs = self.library_dirs
        if lib_dirs:
            dst = opts.setdefault('rpath_dirs', [])
            for d in lib_dirs:
                if d not in dst and d not in platform.system_library_dirs:
                    dst.append(d)

    def feature(self, name):
        return self._ftr_map.get(name)

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

        # Features describe optional components of a package. We store
        # all possible features of the version here.
        if hasattr(self, 'features'):
            self.features = [f(self) for f in self.features]
        else:
            self.features = []

        # Set the possible features on the package class.
        for ftr in self.features:
            self.package.add_feature(ftr)

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

        # If there is nothing to search for then add a base installation
        # and bail.
        if not (self.headers or self.binaries or self.libraries):
            if len(self._potential_installations) == 0:
                logging.debug('Package: Nothing to search for, adding dummy installation.')
                inst = Installation(self)
                self._potential_installations.append(inst)
            return True

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
        logging.debug('Version: Checking.')
        logging.debug('Version: Package: ' + self.package.name + ', version: ' + self.version)

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

        logging.debug('Version: Done checking.')

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
            static_libs = [None]*len(libs)
        else:
            static_libs = static_res[1]
        if not shared_res[1]:
            shared_libs = [None]*len(libs)
        else:
            shared_libs = shared_res[1]

        logging.debug('Found all libraries.')
        return (True, static_libs, shared_libs)

    ##
    ## Calculate the products of nodes. By default this
    ## will call the package's productions.
    ##
    def expand(self, nodes, inst, use_options={}, rule_options={}):
        return self.package.expand(nodes, inst, use_options, rule_options)

    def actions(self, inst, *args, **kwargs):
        return self.package.actions(inst, *args, **kwargs)

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

    def __init__(self, ctx):
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.features = {} # must come before versions
        self.versions = [v(self) for v in self.versions] if hasattr(self, 'versions') else []
        self.sub_packages = [ctx.load_package(n) for n in self.sub_packages] if hasattr(self, 'sub_packages') else []
        self._opts = OptionParser()

    ##
    ## Packages use their class type for comparison. This is
    ## to make sure only one exists in the graph at any time.
    ## The Package object is used to represent ALL packages of
    ## the given type.
    ##
    def __eq__(self, op):
        return self.__class__ == op.__class__

    def __ne__(self, op):
        return not self.__eq__(op)

    def __hash__(self):
        return hash(self.__class__)

    def __repr__(self):
        text = []
        for ver in self.versions:
            text.append(str(ver))
        return self.name + '<' + ', '.join(text) + '>'

    def needs_configure(self):
        return False

    def iter_installations(self):
        for ver in self.versions:
            for inst in ver.installations:
                yield inst

    def add_feature(self, ftr):
        self.features.setdefault(ftr.name, {})[ftr.version] = ftr

    def feature(self, name, use, options=None, cond=None):
        from .Feature import FeatureUse
        ftr_use = FeatureUse(name, use, options, cond)
        self.ctx.uses.append(ftr_use)
        return ftr_use

    ##
    ## Default productions operation. Each version may have its
    ## own production rules. However they can also just refer to
    ## this default operation.
    ##
    def expand(self, nodes, inst, use_options={}, rule_options={}):

        # Don't do anything if there are no sources.
        if not nodes:
            return None

        # Merge any options together.
        opts = self.merge_options(inst.version, use_options, rule_options)

        # Call productions code.
        return self.make_productions(nodes, inst, opts)

    ##
    ## Prepare productions list. By default a list of builders created
    ## from the "default_builder" attribute will be made, one for each
    ## of the nodes.
    ##
    def make_productions(self, nodes, inst, opts, single=False):
        logging.debug('Package: Making productions.')

        # If we don't have a default builder or default target
        # node type then bail.
        default_builder = self._get_attr(inst, 'default_builder')
        default_target_node = self._get_attr(inst, 'default_target_node')
        if not default_builder or not default_target_node:
            return None

        # We need either a destination suffix or a prefix in order
        # to successfully transform a file.
        suf = opts.get('suffix', self._get_attr(inst, 'default_target_suffix', ''))
        pre = opts.get('prefix', '')
        tgt = opts.get('target', '')
        if not suf and not pre and (single and not tgt):
            sys.stdout.write('Package: Can\'t process productions, they would overwrite the original files.\n')
            sys.exit(1)
            return None

        dir_strip = opts.get('target_strip_dirs', 0)

        # Either single or multi.
        prods = []
        if not single:
            for node in nodes:
                src_fn, src_suf = os.path.splitext(node.path)
                src = src_fn + (suf if suf else src_suf)
                new_src = '/'.join([d for i, d in enumerate([d for d in src.split('/') if d]) if i >= dir_strip])
                if src[0] == '/' and dir_strip == 0:
                    new_src = '/' + new_src
                dst = os.path.join(pre, new_src)
                target = default_target_node(dst)
                prods.append(((node,),
                              default_builder(self.ctx, node, target, inst.actions(node, target, opts), opts),
                              (target,)))
        else:
            target = opts.get('target', None)
            target = os.path.join(pre, target)
            target = default_target_node(target)
            prods.append((list(nodes),
                          default_builder(self.ctx, nodes, target, inst.actions(nodes, target, opts), opts),
                          (target,)))

        logging.debug('Package: Done making productions.')
        return prods
                                               

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

    def actions(self, inst, *args, **kwargs):
        for ftr in inst.features:
            acts = ftr(*args, **kwargs)
            if acts is not None:
                return acts
        return None

    ##
    ## Return the options object for this package.
    ##
    def options(self):
        return self._opts

    def merge_options(self, vers, *args):

        # Make new dictionary out of first argument.
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

    def _get_attr(self, inst, attr, default=None):
        val = getattr(inst, attr, None)
        if val is None:
            val = getattr(inst.version, attr, None)
            if val is None:
                val = getattr(self, attr, default)
        return val

    # def save(self, base_dir):
    #     base = os.path.join(base_dir, 'packages')
    #     make_dirs(base)
    #     with open(os.path.join(base, self.name + '.db'), 'w') as out:

    #         # Dump feature names we used.
    #         pickle.dump(self.features.keys(), out)

    #         # Dump the options.
    #         pickle.dump(self._opts, out)

    #         # Dump the versions and installations.
    #         ver_list = []
    #         for ver in self.versions:
    #             cur = [ver.version]
    #             inst_list = []
    #             for inst in ver.installations:
    #                 inst_list.append([inst.location, inst._bins, inst._hdrs, inst._libs, inst._ftr_map.keys()])
    #             cur.append(inst_list)
    #             ver_list.append(cur)
    #         pickle.dump(ver_list, out)

    # def load(self, base_dir):
    #     pass
