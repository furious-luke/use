import use
from ..Platform import platform

# class regex(use.Feature):
#     libraries = ['boost_regex']

# class iostreams(use.Feature):
#     libraries = ['boost_iostreams']

# class filesystem(use.Feature):
#     libraries = ['boost_filesystem']

class Default(use.Version):
    version = 'default'
    headers = ['boost/optional.hpp']
    libraries = ['boost_system', 'boost_regex', 'boost_iostreams', 'boost_filesystem']
    # features = [regex, iostreams, filesystem]

    def __init__(self, *args, **kwargs):
        super(Default, self).__init__(*args, **kwargs)
        if platform.os_name == 'darwin':
            self.libraries = [l + '-mt' for l in self.libraries]

class boost(use.Package):
    default_builder = use.Builder
    versions = [Default]
