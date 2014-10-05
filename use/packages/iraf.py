import use

class default_inst(use.Installer):
    url = 'ftp://iraf.noao.edu/iraf/v216/PCIX/iraf-src.tar.gz'
    commands = [
        "find . -type f -exec grep -Il . {} \; | xargs grep -l '/usr/include/iraf.h' | xargs -n 1 sed -i 's=/usr/include/iraf.h=/usr/local/x86_64/iraf-2.16/include/iraf.h=g'",
        "find . -type f -exec grep -Il . {} \; | xargs grep -l '/iraf/iraf' | xargs -n 1 sed -i 's=/iraf/iraf=/usr/local/x86_64/iraf-2.16/iraf=g'",
        "find . -type f -exec grep -Il . {} \; | xargs grep -l '/iraf/imdirs' | xargs -n 1 sed -i 's=/iraf/imdirs=/usr/local/x86_64/iraf-2.16/imdirs=g'",
        "find . -type f -exec grep -Il . {} \; | xargs grep -l '/iraf/cache' | xargs -n 1 sed -i 's=/iraf/cache=/usr/local/x86_64/iraf-2.16/cache=g'",
        "sed -i 's=/usr/local/bin=/usr/local/x86_64/iraf-2.16/bin=g' ./install",
        "sed -i 's=/usr/local/bin=/usr/local/x86_64/iraf-2.16/bin=g' ./unix/boot/spp/xc.c",

        "cd unix",
        "find . -type f -exec grep -Il . {} \; | xargs grep -l '\"xc\"' | xargs -n 1 sed -i 's=\"xc\"=\"/usr/local/x86_64/iraf-2.16/bin/xc\"=g'",
        "sed -i 's=\"generic\"=\"/usr/local/x86_64/iraf-2.16/bin/generic\"=g' ./boot/mkpkg/mkpkg.h",
        "sed -i 's=\"libmain.o\"=\"/usr/local/x86_64/iraf-2.16/iraf/bin/libmain.o\"=g' ./boot/spp/xc.c",
        "sed -i 's=\"libVO.a\"=\"/usr/local/x86_64/iraf-2.16/iraf/bin/libVO.a\"=g' ./boot/spp/xc.c",
        "cd ..",

        "cd sys/osb",
        "ln -sf /usr/local/x86_64/iraf-2.16/iraf/unix/hlib/d1mach.f d1mach.f",
        "ln -sf /usr/local/x86_64/iraf-2.16/iraf/unix/hlib/i1mach.f i1mach.f",
        "ln -sf /usr/local/x86_64/iraf-2.16/iraf/unix/as/bytmov.c bytmov.c",
        "ln -sf /usr/local/x86_64/iraf-2.16/iraf/unix/hlib/r1mach.f r1mach.f",
        "cd ../..",

        "cd vendor/voclient",
        "sed -i 's=\ make=make=g' ./common/Makefile",
        "Edit voapps/Makefile and remove recursive LFLAGS problem.",
        "Edit voapps/Makefile and add expat into LIBS.",
        "Edit libvo/Makefile and copy libVO.a to ../lib.",
        "Edit libvo/Makefile and add expat to libVO.a.",
        "cd ../..",

        "setenv iraf `pwd`/",
        "./install",
        "setenv PATH /usr/local/x86_64/iraf-2.16/bin:$PATH",

        "cd unix",
        "sh -x mkpkg.sh > & spool",
        "Check for errors.",
        "cd ..",

        "mkpkg sysgen >& spool",
        "Check for errors.",

        "Only if bin.linux64 has no binaries.",
        "rm -rf bin.linux64",
        "ln -s bin.generic bin.linux64"
    ]

class default(use.Version):
    headers = ['iraf.h']
    installer = default_inst

class iraf(use.Package):
    versions = [default]
