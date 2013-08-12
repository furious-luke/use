import use

class Default(use.Version):
    version = 'default'
    headers = ['pugixml.hpp']
    libraries = ['pugixml']

class pugixml(use.Package):
    default_target_node = use.File
    default_builder = use.Builder
    versions = [Default]
