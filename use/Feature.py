from Package import Version

class Feature(Version):

    def __init__(self, *args, **kwargs):
        super(Feature, self).__init__(*args, **kwargs)

        # Swap version name to feature name.
        del self.version
        if not hasattr(self, 'name'):
            name = str(self.__class__)
            self.name = name[name.rfind('.') + 1:name.rfind('\'')].lower()

    ##
    ## Check for existence of this feature.
    ##
    def check(self, inst):
        return False
