import logging
from Package import Version
from Use import Use
from .apply import apply

class Feature(Version):

    def __init__(self, version, *args, **kwargs):
        super(Feature, self).__init__(version.package, *args, **kwargs)

        # Swap version name to feature name.
        del self.version
        if not hasattr(self, 'name'):
            name = str(self.__class__)
            self.name = name[name.rfind('.') + 1:name.rfind('\'')].lower()

        # Add the version as an attribute.
        self.version = version

        # No need for patterns.
        del self.patterns

    def __repr__(self):
        return self.name

    ##
    ## Check for existence of this feature.
    ##
    def check(self, inst):
        logging.debug('Feature: Checking ' + self.name)
        if inst.location is not None:
            res, bins, hdrs, libs = self.footprint(inst.location)
            if res:
                inst._bins.extend(zip(self.binaries, bins))
                inst._hdrs.extend(zip(self.headers, hdrs))
                inst._libs.extend(zip(libs[0], libs[1][0], libs[1][1]))
        else:
            res = True
        logging.debug('Feature: Done checking ' + self.name)
        return res

    def expand(self, nodes, use_options={}, rule_options={}):
        return self.version.expand(nodes, self, use_options, rule_options)

    def apply(self, prods, use_options={}, rule_options={}):
        # NOTE: Not applying because now we add the libraries and such
        #       directly to the installation object.
        # apply(self, prods, use_options, rule_options)
        pass

    def actions(self, node, target, opts):
        return []

    def resolve_set(self, root, use_set):
        logging.debug('Feature: Resolving set for: ' + str(self))
        return True

class FeatureUse(Use):

    def __init__(self, name, use, options=None, cond=None):
        self.feature_name = name
        self.use = use
        super(FeatureUse, self).__init__(use.package, options, cond)
