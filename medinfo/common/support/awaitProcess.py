#!/usr/bin/env python
"""
Wait for another process to finish.  After doing so, execute the given command.
"""

import sys, os;
import time;
import subprocess;
from optparse import OptionParser
from medinfo.common.Util import ProgressDots;

def main(argv):
    """Main method, callable from command line"""
    usageStr =  "usage: %prog -p <pid> -c <commandStr>\n"
    parser = OptionParser(usage=usageStr)
    parser.add_option("-p", "--pid",  dest="pid",  help="Process ID to monitor.  As soon as it is no longer found by Unix signal (os.kill(pid,0)), will proceed to execute the given command");
    parser.add_option("-i", "--interval", dest="interval", default="1", help="How many seconds to wait before checking if the PID is still active.  Default to 1 second.");
    parser.add_option("-c", "--commandStr",  dest="commandStr",  help="Command string to execute after the specified PID is longer found.  Will just pass whole string to subprocess");
    (options, args) = parser.parse_args(argv[1:])

    print >> sys.stderr, "Starting: "+str.join(" ", argv)
    timer = time.time();
    if options.pid and options.commandStr:
        pid = int(options.pid);
        interval = float(options.interval);
        
        prog = ProgressDots(60,1,"intervals");
        while pidExists(pid):
            time.sleep(interval);
            prog.update();
        prog.printStatus();
        
        print >> sys.stderr, "Executing: ", options.commandStr;
        process = subprocess.Popen(options.commandStr);
        print >> sys.stderr, "Started process: ", process.pid;
    else:
        parser.print_help()
        sys.exit(-1)

    timer = time.time() - timer;
    print >> sys.stderr, ("%.3f seconds to complete" % timer);

def pidExists(pid):
    """Return True/False whether the given PID exists / is active"""
    exists = True;
    try:
        os.kill(pid,0); # 0 is Unix signal to just check if process exists, doesn't actually kill anything
    except OSError:
        exists = False;
    return exists;
        

if __name__ == "__main__":
    main(sys.argv);
