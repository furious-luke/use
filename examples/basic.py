from Build.utils import load_class
from Build import *

pkg = load_class('Build.packages.file')()

src = File('basic.py')
dst = pkg.FileType()

bldr = pkg(src, dst)
bldr()

print dst.file_type
