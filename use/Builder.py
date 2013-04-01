from .conv import to_list

class Builder(object):

    def __init__(self, sources, targets, actions=[]):
        self.sources = sources
        self.targets = targets
        self.actions = actions

    def __call__(self):
        for action in self.actions:
            action(self.sources, self.targets)
            if action.status == action.FAILED:
                pass
        self._parse()
