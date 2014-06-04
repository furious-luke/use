import os, os.path, tempfile, tarfile, zipfile
from time import sleep
from nose.tools import *
from use.Installer import *

def test_init():
    inst = Installer()
    assert_equals(inst.work_dir, None)
    assert_equals(inst.install_dir, None)

def test__check_auto():
    inst = Installer()
    inst._check()
    assert_not_equals(inst.work_dir, None)
    assert_equals(inst._tmp_dir, os.path.join(inst.work_dir, 'tmp'))
    assert_equals(inst._src_dir, os.path.join(inst.work_dir, 'src'))
    assert_equals(inst._bld_dir, os.path.join(inst.work_dir, 'bld'))
    assert_equals(inst._bld_succ_path, os.path.join(inst.work_dir, inst.build_success_fname))
    assert_equals(inst._ins_succ_path, os.path.join(inst.work_dir, inst.install_success_fname))

def test__check_changed():
    inst = Installer()
    dir = tempfile.mkdtemp()
    inst.work_dir = dir
    inst._check()
    assert_equals(inst.work_dir, dir)
    assert_equals(inst._tmp_dir, os.path.join(inst.work_dir, 'tmp'))
    assert_equals(inst._src_dir, os.path.join(inst.work_dir, 'src'))
    assert_equals(inst._bld_dir, os.path.join(inst.work_dir, 'bld'))
    assert_equals(inst._bld_succ_path, os.path.join(inst.work_dir, inst.build_success_fname))
    assert_equals(inst._ins_succ_path, os.path.join(inst.work_dir, inst.install_success_fname))

def test_download_package_auto():
    inst = Installer()

    # Create a test file for downloading.
    with tempfile.NamedTemporaryFile(delete=False) as file:
        name = file.name
        file.write('test')

    path = inst.download_package('file://' + os.path.abspath(name))
    assert_not_equals(path, None)
    with open(path) as file:
        assert_equals(file.readline(), 'test')

def test_download_package_named():
    inst = Installer()

    # Create a test file for downloading.
    with tempfile.NamedTemporaryFile(delete=False) as file:
        name = file.name
        file.write('test')

    path = inst.download_package('file://' + os.path.abspath(name), 'myfile')
    assert_equals(path, os.path.join(inst.work_dir, 'myfile'))
    with open(path) as file:
        assert_equals(file.readline(), 'test')

def test_download_package_exists():
    inst = Installer()

    # Create a test file for downloading.
    with tempfile.NamedTemporaryFile(delete=False) as file:
        name = file.name
        file.write('test')

    # Create overlapping file.
    inst._check()
    myfile = os.path.join(inst.work_dir, 'myfile')
    with open(myfile, 'w') as file:
        file.write('test')

    # Cache timestamp.
    mtime = os.path.getmtime(myfile)
    sleep(0.1)

    path = inst.download_package('file://' + os.path.abspath(name), 'myfile')
    assert_equals(path, myfile)
    with open(path) as file:
        assert_equals(file.readline(), 'test')
    assert_equals(mtime, os.path.getmtime(myfile))

def test_download_package_force():
    inst = Installer()

    # Create a test file for downloading.
    with tempfile.NamedTemporaryFile(delete=False) as file:
        name = file.name
        file.write('test')

    # Create overlapping file.
    inst._check()
    myfile = os.path.join(inst.work_dir, 'myfile')
    with open(myfile, 'w') as file:
        file.write('test')

    # Cache timestamp and wait a few milliseconds.
    mtime = os.path.getmtime(myfile)
    sleep(0.1)

    path = inst.download_package('file://' + os.path.abspath(name), 'myfile', True)
    assert_equals(path, myfile)
    with open(path) as file:
        assert_equals(file.readline(), 'test')
    assert_not_equals(mtime, os.path.getmtime(myfile))

def test_extract_package_tar():
    inst = Installer()

    # Create a test file.
    with tempfile.NamedTemporaryFile(delete=False) as file:
        name = file.name
        file.write('test')

    # Create tar file.
    dir = tempfile.mkdtemp()
    pkg_path = os.path.join(dir, 'tf')
    with tarfile.open(pkg_path, 'w:gz') as tf:
        tf.add(name, arcname=os.path.basename(name))

    path = inst.extract_package(pkg_path)
    assert_equals(path, os.path.join(inst._src_dir, 'tf'))
    entries = os.listdir(path)
    assert_in(os.path.basename(name), entries)

def test_extract_package_zip():
    inst = Installer()

    # Create a test file.
    with tempfile.NamedTemporaryFile(delete=False) as file:
        name = file.name
        file.write('test')

    # Create zip file.
    dir = tempfile.mkdtemp()
    pkg_path = os.path.join(dir, 'zf.zip')
    with zipfile.ZipFile(pkg_path, 'w') as zf:
        zf.write(name, arcname=os.path.basename(name))

    path = inst.extract_package(pkg_path)
    assert_equals(path, os.path.join(inst._src_dir, 'zf.zip'))
    entries = os.listdir(path)
    assert_in(os.path.basename(name), entries)

def test_extract_package_named():
    assert_equals(1, 0)

def test_extract_package_exists():
    inst = Installer()

    # Create a test file.
    with tempfile.NamedTemporaryFile(delete=False) as file:
        name = file.name
        file.write('test')

    # Create tar file.
    dir = tempfile.mkdtemp()
    pkg_path = os.path.join(dir, 'tf')
    with tarfile.open(pkg_path, 'w:gz') as tf:
        tf.add(name, arcname=os.path.basename(name))

    # Create existing directory.
    inst._check()
    dir = os.path.join(inst._src_dir, 'tf')
    os.mkdir(dir)
    mtime = os.path.getmtime(dir)
    sleep(0.1)

    path = inst.extract_package(pkg_path)
    assert_equals(path, os.path.join(inst._src_dir, 'tf'))
    assert_equals(mtime, os.path.getmtime(path))

def test_extract_package_force():
    assert_equals(1, 0)
