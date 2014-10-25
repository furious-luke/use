from .apply import apply

##
## Handles applying packages to productions.
##
class Applier(object):

    def __init__(self, vers):
        self.version = vers

    def apply(self, prods, use_opts={}, rule_opts={}):
        apply(self, prods, use_opts, rule_opts)
