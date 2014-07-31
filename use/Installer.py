import os, subprocess, shlex, shutil, tempfile, logging, sys
from Options import OptionParser, Option, OptionDict
from utils import make_dirs

__all__ = ['Installer']

##
## Handles installation of a specific package version. To
## use common installation code we can inherit installer
## classes.
##
class Installer(object):
    build_success_fname = 'build_success.use'
    install_success_fname = 'build_success.use'

    def __init__(self, url, prog=False):
        self.url = url
        self._prog = prog
        self.set_dirs()
        self.name = self.name if hasattr(self, 'name') else self.__class__.__name__

        # Prepare commands with options.
        self.commands = {}

        self.commands['configure'] = op

        self.commands['make'] = op

        # Prepare basic GNU actions.
        self.commands = []
        op = OptionParser()
        op.add('prefix', long_opts='--prefix')
        self.commands.append(Command(op, 'configure'))
        op = OptionParser()
        op.add('install', long_opts='install')
            ('make', OptionDict()),
            ('make', OptionDict(install=True)),
            ]

    def __call__(self):
        logging.debug('Installer: Installing using %s.'%self.name)
        pkg_path = self.download_package(self.url)
        src_dir = self.extract_package(pkg_path)
        self.run_actions()
        logging.debug('Installer: Done installing using %s.'%self.name)

    def set_dirs(self, work_dir=None, install_dir=None):
        self.work_dir = work_dir
        self.install_dir = install_dir

    def _check(self):
        if self.work_dir is None:
            self.work_dir = tempfile.mkdtemp()
        if not hasattr(self, '_old_work_dir') or self._old_work_dir != self.work_dir:
            self._old_work_dir = self.work_dir
            self._tmp_dir = os.path.join(self.work_dir, 'tmp')
            self._src_dir = os.path.join(self.work_dir, 'src')
            self._bld_dir = os.path.join(self.work_dir, 'bld')
            make_dirs(self._tmp_dir)
            make_dirs(self._src_dir)
            make_dirs(self._bld_dir)
            self._bld_succ_path = os.path.join(self.work_dir, self.build_success_fname)
            self._ins_succ_path = os.path.join(self.work_dir, self.install_success_fname)

    def download_package(self, url, fname=None, force=False):
        logging.debug('Installer: downloading package %s'%url)
        assert fname is None or not os.path.isabs(fname)
        self._check()

        # Use a default filename if one wasn't given.
        if fname is None:
            fname = os.path.basename(url)
        path = os.path.join(self.work_dir, fname)
        logging.debug('Installer: path "%s"'%path)

        # Check if the package already exists.
        if not force and os.path.exists(path):
            logging.debug('Installer: already exists')
            return path

        # Remove existing file.
        tmp_path = os.path.join(self._tmp_dir, fname)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        # Attempt to download the package.
        try:
            logging.debug('Installer: retrieving "%s" to "%s"'%(url, tmp_path))
            import urllib
            if self._prog:
                sys.stdout.write('Downloading "%s":\n'%url)
                sys.stdout.write('  |----------------------------------------------------------------------|\n')
                sys.stdout.write('  |')
                sys.stdout.flush()
                self._perc = 0.0
                self._incr = 1.0/70.0
                urllib.urlretrieve(url, tmp_path, self._progress)
            else:
                urllib.urlretrieve(url, tmp_path)
            if self._prog:
                sys.stdout.write('|\n')
        except Exception as e:
            logging.debug('Installer: failed to download file: %s'%str(e))
            return None

        # Move the package to the final path and touch it.
        os.rename(tmp_path, path)
        os.utime(path, None)
        logging.debug('Installer: success')
        return path

    def extract_package(self, pkg_path, dst_dir=None, force=False):
        logging.debug('Installer: extracting package %s'%pkg_path)
        assert os.path.exists(pkg_path)
        self._check()

        # Use the given destination directory or create one.
        if not dst_dir:
            dst_dir = os.path.join(self._src_dir, os.path.basename(pkg_path))
        logging.debug('Installer: destination "%s"'%dst_dir)

        # Check if the contents are already there.
        if not force and os.path.exists(dst_dir):
            logging.debug('Installer: already exists')
            return dst_dir

        # Remove the destination entirely.
        tmp_dst_dir = os.path.join(self._tmp_dir, os.path.basename(pkg_path))
        if os.path.exists(tmp_dst_dir):
            shutil.rmtree(tmp_dst_dir)

        if os.path.splitext(pkg_path)[1] == '.zip':
            try:
                import zipfile
                zf = zipfile.ZipFile(pkg_path)
                zf.extractall(tmp_dst_dir)
                zf.close()
            except Exception as e:
                logging.debug('Installer: zip failed: %s'%str(e))
                return None
        else:
            try:
                import tarfile
                tf = tarfile.open(pkg_path)
                tf.extractall(tmp_dst_dir)
            except:
                return None

        # Move directory.
        os.rename(tmp_dst_dir, dst_dir)
        logging.debug('Installer: success')
        return dst_dir

    def run_actions(self):
        logging.debug('Installer: running actions')
        self._check()

        # Update the environment with some things.
        for act in self.actions:
            opts = act[1]
            if opts and 'prefix' not in opts:
                opts._opts['prefix'] = self.install_dir

        # Make a file to log all commands.
        with open(os.path.join(self._work_dir, 'use_build.log'), 'a') as log:

            # Process each command in turn.
            for act in self.actions:
                cmd, opts = act

                logging.debug('Installer: command "%s"'%cmd)

                # Perform substitutions.
                cmd = cmd.format(**env)

                    try:
                        subprocess.check_call(shlex.split(cmd), stdout=log, stderr=subprocess.STDOUT)
                    except:
                        logging.debug('Installer: error')
                        if not allow_errors:
                            return False

        return True
    
    def _progress(self, n_blocks, block_size, total_size):
        perc = (n_blocks*block_size)/float(total_size)
        while perc >= self._perc + self._incr:
            sys.stdout.write('=')
            sys.stdout.flush()
            self._perc += self._incr
