#!/usr/bin/env python
"""
Support module to manage (multiple) shell processes.
For example, enable batch run of multiple in series, or in parallel, or
monitor existing process and wait to finish before activating next.
"""

import sys, os;
import time;
import subprocess;
from optparse import OptionParser
import math;
from datetime import datetime;
from medinfo.common.Util import stdOpen, ProgressDots;
from Util import log;

class ProcessManager:
    def __init__(self, parallelProcessCount=1):
        self.parallelProcessCount = parallelProcessCount
        self.availableThreads = parallelProcessCount
        self.processCount = 0
        self.completedProcessCount = 0
        self.completed = False

    def parseArgList(self, argvList):
        # initiate self.processCount
        pass

    def update(self, argvList):
        # poll
        # update globals
        pass


    def batchProcess(self, argvList, numParallel=1):
        """Given a list of argv command string lists, spawn
        subprocesses to run each argv as if run from the command-line.
        Option to specify running multiple processes in parallel, and
        only continuing to spawn more as previous processes complete.
        """
        commandStringList = self.parseArgList(argvList);

        #############???????????????##############
        """See scripts/CDSS/assocAnalysis.py for example.
        Top part is just nested loops to generate lists of argv parameters.
        Bottom section is part to reproduce/generalize so will run all given argv,
        but should create subprocess.Popen objects instead so can print out Popen.pid as
        part of progress log, and allow for multiple processes running in parallel.
        I believe you can do something like Popen.poll() to check if a current subprocess
        is still running or if it's completed.
        """

        while(processesRemain):
            self.update()
            if self.completed:
                print "All processes have completed.\n"
                break
            if availableThreads > 0:
                # run an unprocessed command string
                pass


    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog -p <pid> -c <commandStr>\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-p", "--pid",  dest="pid",  help="Process ID to monitor.  As soon as it is no longer found by Unix signal (os.kill(pid,0)), will proceed to execute the given command");
        parser.add_option("-i", "--interval", dest="interval", default="1", help="How many seconds to wait before checking if the PID is still active.  Default to 1 second.");
        parser.add_option("-c", "--commandStr",  dest="commandStr",  help="Command string to execute after the specified PID is longer found.  Will just pass whole string to subprocess");
        (options, args) = parser.parse_args(argv[1:])


        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();

        ###########---From medinfo/common/support/awaitProcess.py)---#############
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
        ###---END awaitProcess method---###

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

def pidExists(pid):
    """Return True/False whether the given PID exists / is active"""
    exists = True;
    try:
        os.kill(pid,0); # 0 is Unix signal to just check if process exists, doesn't actually kill anything
    except OSError:
        exists = False;
    return exists;

if __name__ == "__main__":
    instance = ProcessManager();
    instance.main(sys.argv);
