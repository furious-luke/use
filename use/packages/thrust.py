import use

class default(use.Version):
    headers = ['thrust/device_vector.h']

class thrust(use.Package):
    versions = [default]
