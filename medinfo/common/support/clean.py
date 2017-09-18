#!/usr/bin/env python
# Simple macro.  Can take one command line argument specifying a directory,
#   otherwise defaults to the current directory.  Then just traverses that
#   directory and all subdirectories, deleting and file that ends with ".pyc"

import sys,os

basedir = '.'
if len(sys.argv) > 1:
    basedir = sys.argv[1]

for root, dirs, files in os.walk(basedir):
    for file in files:
        if file.endswith('.pyc'):
            filepath = os.path.join(root,file)
            print "Removing %s" % filepath
            os.remove(filepath)
