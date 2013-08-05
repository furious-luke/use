import logging
from .Options import Options
from .utils import run_command

class CommandFailed(Exception):

    def __init__(self, command):
        self.command = command

    def __str__(self):
        return 'Command failed:\n\n%s\n'%self.command.command_string

##
##
##
class Action(object):
    OKAY = 0
    FAILED = 1

##
##
##
class Command(Action):

    def __init__(self, command):
        self.command = command

    def __call__(self, opts):
        logging.debug('Command: Executing.')

        cmd = self.get_command(opts)
        logging.debug('Command is: ' + cmd)
        self.return_code, self.stdout, self.stderr = run_command(cmd)
        self._set_status(cmd)

        logging.debug('Command: Done executing.')

    def get_command(self, opts):
        if isinstance(self.command, Options):
            return self.command(**opts)
        else:
            return self.command.format(opts)

    def _set_status(self, cmd_str):
        self.command_string = cmd_str
        if self.return_code == 0:
            self.status = self.OKAY
        else:
            self.status = self.FAILED
            raise CommandFailed(self)
