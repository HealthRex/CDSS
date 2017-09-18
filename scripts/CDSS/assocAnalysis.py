"""
Example shell script background call to run script to start up several data conversion processes in series
nohup python scripts/CDSS/assocAnalysis.py &> log/driver.assocAnalysis &
Not much DB resources required, just some memory.  Bottle neck is more IO operations
"""

import subprocess;
from medinfo.common.Util import stdOpen, log, ProgressDots;

LOG_FILE_TEMPLATE = "log/assocAnalysis.%s";
BUFFER_FILENAME = "results/assocAnalysis.buffer.%s";

baseArgv = \
    [   "python","-m","medinfo.cpoe.AssociationAnalysis",
        "-u","10000",
        "-a","2000000",    # 1000000 seems to just fit with 7.5GB memory.  Running batches of 3000 patients yields ~5M associations requiring ~25GB memory
        #"-p","1000",
    ];

PATIENT_ID_FILES = \
    [   
        #"sourceData/patientIds.5year.0.tab.gz",
        #"sourceData/patientIds.5year.1.tab.gz",
        #"sourceData/patientIds.5year.2.tab.gz",
        #"sourceData/patientIds.5year.3.tab.gz",
        #"sourceData/patientIds.5year.4.tab.gz",
        #"sourceData/patientIds.5year.5.tab.gz",
        #"sourceData/patientIds.5year.6.tab.gz",
        #"sourceData/patientIds.5year.7.tab.gz",
        #"sourceData/patientIds.5year.8.tab.gz",
        #"sourceData/patientIds.5year.9.tab.gz",
        #"sourceData/patientIds.5year.-1.tab.gz",
        #"sourceData/patientIds.5year.-2.tab.gz",
        #"sourceData/patientIds.5year.-3.tab.gz",
        #"sourceData/patientIds.5year.-4.tab.gz",
        #"sourceData/patientIds.5year.-5.tab.gz",
        #"sourceData/patientIds.5year.-6.tab.gz",
        #"sourceData/patientIds.5year.-7.tab.gz",
        #"sourceData/patientIds.5year.-8.tab.gz",
        #"sourceData/patientIds.5year.-9.tab.gz",
    ];
DATE_LIMITS = \
    [   
        ["2010-01-01",  "2014-01-01"],

        #["2012-12-01",  "2013-01-01"], # 1 month
        #["2012-11-01",  "2013-01-01"], # 2 month
        #["2012-10-01",  "2013-01-01"], # 3 month
        #["2012-07-01",  "2013-01-01"], # 6 month
        #["2012-01-01",  "2013-01-01"], # 12 month
        #["2011-01-01",  "2013-01-01"], # 24 month
        #["2009-01-01",  "2013-01-01"], # 48 month
        
        #["2008-01-01",  "2009-01-01"],
        #["2009-01-01",  "2010-01-01"],
        #["2010-01-01",  "2011-01-01"],
        #["2011-01-01",  "2012-01-01"],
        #["2012-01-01",  "2013-01-01"],
        #["2013-01-01",  "2014-01-01"],
        #["2014-01-01",  "2015-01-01"],
    ];
specificArgvList = \
    [   
    ];

for patientIdFilename in PATIENT_ID_FILES:
    for (startDate, endDate) in DATE_LIMITS:
            specificArgv = ["-i", patientIdFilename, "-s", startDate,"-e", endDate, "-b", "results/assocBuffer.%s.%s.%s" % (patientIdFilename.replace("/","_"), startDate, endDate) ];
            specificArgvList.append(specificArgv);

prog = ProgressDots(1,1,"Processes",total=len(specificArgvList));
for specificArgv in specificArgvList:
    key = "%.3d.%s" % (prog.getCounts(), str.join("_",specificArgv) );
    key = key.replace("/","..");
    argv = list(baseArgv)
    argv.extend(specificArgv);
    log.info( LOG_FILE_TEMPLATE % key );
    logFile = stdOpen(LOG_FILE_TEMPLATE % key,"w")
    subprocess.call(argv, stderr=logFile);
    prog.update();
prog.printStatus();
