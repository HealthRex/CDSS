"""
Example shell script background call to run script to start up several data conversion processes in series
nohup python scripts/CDSS/dataConversion.py &> log/log.driverDataConversion &
"""

import subprocess;
from medinfo.common.Util import stdOpen, log, ProgressDots;

LOG_FILE_TEMPLATE = "log/dataConversion.%s";

baseArgv = ["python","-m"];

DATE_LIMITS = \
    [   ["2008-01-01",  "2009-01-01"],
        ["2009-01-01",  "2010-01-01"],
        ["2010-01-01",  "2011-01-01"],
        ["2011-01-01",  "2012-01-01"],
        ["2012-01-01",  "2013-01-01"],
        ["2013-01-01",  "2014-01-01"],
        ["2014-01-01",  "2015-01-01"],
    ];
MODULE_PARAMS = \
    [   #("medinfo.dataconversion.STRIDEOrderMedConversion",),
        #("medinfo.dataconversion.STRIDEDxListConversion",),
        #("medinfo.dataconversion.STRIDEOrderProcConversion",),
        #("medinfo.dataconversion.STRIDEOrderResultsConversion",),
        #("medinfo.dataconversion.STRIDEPreAdmitMedConversion",),
        #("medinfo.dataconversion.STRIDETreatmentTeamConversion","-a"),
    ];

specificArgvList = \
    [   
        #["medinfo.dataconversion.STRIDEDemographicsConversion"],
    ];

for moduleParam in MODULE_PARAMS:
    for (startDate, endDate) in DATE_LIMITS:
            specificArgv = list(moduleParam);
            specificArgv.extend(["-s", startDate,"-e", endDate]);
            specificArgvList.append(specificArgv);

prog = ProgressDots(10,1,"Processes",total=len(specificArgvList));
for specificArgv in specificArgvList:
    key = "%.3d.%s" % (prog.getCounts(), str.join("_",specificArgv) );
    argv = list(baseArgv)
    argv.extend(specificArgv);
    log.info( LOG_FILE_TEMPLATE % key );
    logFile = stdOpen(LOG_FILE_TEMPLATE % key,"w")
    subprocess.call(argv, stderr=logFile);
    prog.update();
prog.printStatus();
