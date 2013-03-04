from Build.utils import load_class
from Build import *

pkg = load_class('Build.packages.gcc')()

src = File('source.c')
dst = File('source.o')

bldr = pkg(src, dst)
bldr()
