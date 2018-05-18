import sys,os;
import shutil;
from medinfo.common.Util import *;

SUFFIX = "\t3106\n"

shutil.copy(sys.argv[1], sys.argv[2]);  # Temp copy

ifs = stdOpen(sys.argv[2]);
ofs = stdOpen(sys.argv[1],"w");

prog = ProgressDots();

for i, line in enumerate(ifs):
    prog.update();
    if not line.endswith(SUFFIX):
        ofs.write(line);
    else:
        print >> sys.stderr, "Skipping Line %d" % i;
prog.printStatus();
