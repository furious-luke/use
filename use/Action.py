import logging
from .utils import run_command

class CommandFailed(Exception):

    def __init__(self, command):
        self.command = command

    def __str__(self):
        return 'Command failed:\n\n%s\n'%self.command

class Action(object):

    OKAY = 0
    FAILED = 1

    def __init__(self, command):
        self.command = command

    def __call__(self, sources, targets):
        self.return_code, self.stdout, self.stderr = run_command(self.command)
        self._set_status()

    def _set_status(self):
        if self.return_code == 0:
            self.status = self.OKAY
        else:
            self.status = self.FAILED
