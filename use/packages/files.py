import use

class Copy(use.Feature):
    def actions(self, sources, targets=[], options={}):
        return [use.actions.Copy(sources, targets)]

class Default(use.Version):
    version = 'default'
    features = [Copy]

class files(use.Package):
    default_target_node = use.File
    default_builder = use.Builder
    versions = [Default]
