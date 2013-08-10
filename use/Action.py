import sys, os, shutil, logging
from .Options import OptionParser
from .utils import run_command, make_dirs
from .conv import to_list

__all__ = ['Command', 'Copy']

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

    def __init__(self, command, create_dirs=True):
        self.command = command
        self.create_dirs = create_dirs

    def __call__(self, opts):
        logging.debug('Command: Executing.')

        if self.create_dirs:
            self._create_dirs(opts)

        cmd = self.get_command(opts)
        logging.debug('Command is: ' + cmd)
        sys.stdout.write(cmd + '\n')
        self.return_code, self.stdout, self.stderr = run_command(cmd)
        self._set_status(cmd)

        logging.debug('Command: Done executing.')

    def get_command(self, opts):
        if isinstance(self.command, OptionParser):
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

    def _create_dirs(self, opts):
        targets = opts.get('targets', None)
        if targets is None:
            targets = opts.get('target', [])
        targets = to_list(targets)
        for tgt in targets:
            make_dirs(os.path.dirname(tgt.path))

##
##
##
class Copy(Action):

    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __call__(self, opts):
        logging.debug('Copy: Copying file.')
        src = opts.get('source', self.source)
        dst = opts.get('target', self.target)
        logging.debug('Copy: Source: ' + str(src))
        logging.debug('Copy: Destination: ' + str(dst))
        sys.stdout.write('Copying: ' + str(src) + ' -> ' + str(dst) + '\n')
        make_dirs(os.path.dirname(dst.path))
        shutil.copy(src.path, dst.path)
        logging.debug('Copy: Done copying file.')
