import use

class default(use.Version):
    headers = ['Eigen/Eigen']

class eigen(use.Package):
    versions = [default]
