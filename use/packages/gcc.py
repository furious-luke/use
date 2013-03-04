import re
import Build
from Build.utils import getarg
from Build.conv import to_list

##
##
##
class Builder(Build.Builder):

    _prog = re.compile('(' + ')|('.join([
    ]) + ')')

    def _parse(self):
        assert len(self.sources) == 1 and len(self.targets) == 1, 'Can\'t run "file" on multiple sources/targets.'
        match = self._prog.search(self.actions[0].stdout)
        assert match and match.lastindex > 0
        self.targets[0].file_type = match.lastindex - 1

##
##
##
class Version(Build.Version):

    version = 'default'
    binaries = ['gcc']

    def _actions(self, sources, targets=[]):
        return [Build.Action('%s -c -o %s %s'%(
            self.binaries[0].path,
            targets[0].path,
            ' '.join([s.path for s in sources]),
        ))]

##
## GNU "gcc" tool.
##
class gcc(Build.Package):
    default_target_node = Build.File
    default_builder = Builder
    versions = [Version]

