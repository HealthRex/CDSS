"""Helped script for parallel process debugging. Just takes one parameter, sleeps for that many seconds, then completes"""

import sys;
from medinfo.common.Util import ProgressDots;
import time;

duration = int(sys.argv[1]);

progress = ProgressDots();
for i in xrange(duration):
	progress.update();
progress.printStatus();
