from Package import Version
from Use import Use

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

    ##
    ## Check for existence of this feature.
    ##
    def check(self, inst):
        return True

    def expand(self, nodes, use_options={}, rule_options={}):
        return self.version.expand(nodes, self, use_options, rule_options)

    def apply(self, prods, use_options={}, rule_options={}):
        pass

    def actions(self, node, target, opts):
        return []

class FeatureUse(Use):

    def __init__(self, name, use, cond=None, options=None):
        self.feature_name = name
        self.use = use
        super(FeatureUse, self).__init__(use.package, cond, options)
