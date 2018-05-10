"""
Example shell script background call to run script to start up several sub processes in series
People often just make bash shell scripts, but I find Python a more flexible language that can do all of the above and better integrate.
    nohup python batchDriver.py &> log/driver.assocAnalysis &

"""

import subprocess;
from medinfo.common.Util import stdOpen, log, ProgressDots;

LOG_FILE_TEMPLATE = "log/exampleQuery.%s.log";

baseArgv = \
    [   "python","ExampleQueryApp.py",
        "-p","0.001",
    ];

DATE_LIMITS = \
    [   
        ["2011-01-01",  "2011-01-02"],
        ["2011-01-02",  "2011-01-03"],
        ["2011-01-03",  "2011-01-04"],
        ["2011-01-04",  "2011-01-05"],
        ["2011-01-05",  "2011-01-06"],
        ["2011-01-06",  "2011-01-07"],
        ["2011-01-07",  "2011-01-08"],
        ["2011-01-08",  "2011-01-09"],
        ["2011-01-09",  "2011-01-10"],
        ["2011-01-10",  "2011-01-11"],
        ["2011-01-11",  "2011-01-12"],
        ["2011-01-12",  "2011-01-13"],
    ];
specificArgvList = \
    [   
    ];

for (startDate, endDate) in DATE_LIMITS:
        specificArgv = ["-s", startDate,"-e", endDate, "results/queryResults.%s.%s.tab.gz" % (startDate, endDate) ];
        specificArgvList.append(specificArgv);

prog = ProgressDots(1,1,"Processes",total=len(specificArgvList));
for specificArgv in specificArgvList:
    key = "%.3d.%s" % (prog.getCounts(), str.join("_",specificArgv) );
    key = key.replace("/","..");    # Don't want to use directory separator in temp log file name
    argv = list(baseArgv)
    argv.extend(specificArgv);
    log.info( "Starting: "+str.join(" ", argv) );
    logFile = stdOpen(LOG_FILE_TEMPLATE % key,"w")
    
    subprocess.call(argv, stderr=logFile);
    # Blocking sub-process call. Can just run multiple instances to parallelize, or consider  subprocess.Popen objects instead
    prog.update();
prog.printStatus();
