from .conv import to_list
import logging

class Builder(object):

    def __init__(self, sources, targets, actions=[], options={}):
        self.sources = to_list(sources)
        self.targets = to_list(targets)
        self.actions = to_list(actions)
        self.options = dict(options)
        self.options['sources'] = self.sources
        self.options['targets'] = self.targets

    def build_sources(self, ctx):
        logging.debug('Builder: Building sources.')

        invalid = False
        for src in self.sources:
            this = src.build(ctx)
            invalid = invalid or this

        logging.debug('Builder: Done building sources.')
        return invalid

    def update(self, ctx):
        logging.debug('Builder: Updating.')

        for action in self.actions:
            action(self.options)
            if action.status == action.FAILED:
                pass
        self.post_update(ctx)

        logging.debug('Builder: Done updating.')

    def post_update(self, ctx):
        pass
