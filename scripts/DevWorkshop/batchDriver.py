"""
Example shell script background call to run script to start up several sub processes
People often just make bash shell scripts, but I find Python a more flexible language that can do all of the above and better integrate.
    nohup python batchDriver.py &> driver.log &

"""

import subprocess;
from medinfo.common.Util import stdOpen, log, ProgressDots;

LOG_FILE_TEMPLATE = "log/exampleQuery.%s.log";

baseArgv = \
    [   "python","ExampleQueryApp.py",
        "-p","1",
    ];

CATEGORY_LIST = \
    [   "Med (Oral)", "Med (Intravenous)", "Diagnosis (ADMIT_DX)", "Lab","Lab Result",
    ];
ITEM_PREFIXES = \
    [   "A","B","C","D","E","F","G","H","I",        
    ];
specificArgvList = \
    [   
    ];

for categoryName in CATEGORY_LIST:
    for itemPrefix in ITEM_PREFIXES:
        specificArgv = ["-c", categoryName, "-i", itemPrefix, "results/queryResults.%s.%s.tab.gz" % (itemPrefix, categoryName) ];
        specificArgvList.append(specificArgv);

prog = ProgressDots(1,1,"Processes",total=len(specificArgvList));
for specificArgv in specificArgvList:
    key = "%.3d.%s" % (prog.getCounts(), str.join("_",specificArgv) );
    key = key.replace("/","..");    # Don't want to use directory separator in temp log file name
    argv = list(baseArgv)
    argv.extend(specificArgv);
    log.info( "Starting: "+str.join(" ", argv) );
    logFile = stdOpen(LOG_FILE_TEMPLATE % key,"w")
    
    # Blocking sub-process call if want serial processes.
    #subprocess.call(argv, stderr=logFile);

    # Non-blocking subprocess.Popen to spawn parallel processes
    process = subprocess.Popen(argv, stderr=logFile);
    log.info("Process ID: %s" % process.pid);

    # Print command lines to effectively generate a .sh script
    #print "nohup",
    #print str.join(" ", argv),
    #print "&>", LOG_FILE_TEMPLATE % key,"&"
 
    prog.update();
prog.printStatus();
