use
====

## Description

A Python based build system taking some of the great ideas from SCons, the
well established rule based methods of make, and adding a powerful
configuration system.

Please note that this software is under heavy development and probably won't
work properly right now.

## Basics

The premise of Use is that the build system can do many more useful things
if it is in full possession of the facts. Use is more a declarative style
build system; the user declares the packages they wish to use, the options
that should be supported by packages, the sets of files to be processed
(in the form of rules) and the conditions under which certain rules will
be followed. A graph is constructed of the build, which allows the system
to determine which packages are essential and which are optional, amongst
other things. This makes Use both a configuration and build system in one.

## Installation

The only dependency is Python 2.7. Standard setuptools installation can
be used:

  python setup.py install

## usescript.py

Instructions are given to Use by creating a "usescript.py" file in the
base directory of your project. The general layout of a usescript file
will usually be something like:

  * command-line arguments,
  * option sets (including conditional options),
  * package declarations,
  * use flows,
  * rules.

There is an example usescript in the examples folder.

TODO: Heaps more documentation.

## Testing

`nosetests -w tests`
