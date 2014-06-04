import os, subprocess, shlex, shutil, tempfile, logging

__all__ = ['Installer']

##
## Handles installation of a specific package version. To
## use common installation code we can inherit installer
## classes.
##
class Installer(object):
    build_success_fname = 'build_success.use'
    install_success_fname = 'build_success.use'

    def __init__(self):
        self.set_dirs()

    def __call__(self):
        pkg_path = self.download_package(self.url)
        src_dir = self.extract_package(pkg_path)
        self.run_commands(self.commands)

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
            os.mkdir(self._tmp_dir)
            os.mkdir(self._src_dir)
            os.mkdir(self._bld_dir)
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
            urllib.urlretrieve(url, tmp_path)
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

    def run_commands(self, cmds, env={}):
        logging.debug('Installer: running commands')
        self._check()

        # Update the environment with some things.
        if self.install_dir is not None:
            env['prefix'] = self.install_dir

        # Make a file to log all commands.
        with open(os.path.join(self._work_dir, 'use_build.log'), 'a') as log:

            # Process each command in turn.
            for cmd in cmds:

                # It's possible to have a tuple, indicating a function and arguments.
                if isinstance(cmd, tuple):
                    func = cmd[0]
                    args = cmd[1:]

                    # Perform substitutions.
                    args = [env.subst(a.replace('${PREFIX}', dst_path)) for a in args]

                    # Call the function.
                    func(*args)

                else:
                    logging.debug('Installer: command "%s"'%cmd)

                    # If the first character in a command is an "!", then it means we allow
                    # errors from this command.
                    allow_errors = False
                    if cmd[0] == '!':
                        allow_errors = True
                        cmd = cmd[1:]

                    # Perform substitutions.
                    cmd = cmd.format(**env)

                    try:
                        subprocess.check_call(shlex.split(cmd), stdout=log, stderr=subprocess.STDOUT)
                    except:
                        logging.debug('Installer: error')
                        if not allow_errors:
                            return False

        return True
