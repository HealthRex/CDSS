"""
Example shell script background call to run script to start up several data conversion processes in series
nohup python scripts/CDSS/driverExtractData.py &> log/log.driverExtractData &
"""

import subprocess;
from medinfo.common.Util import stdOpen, log, ProgressDots;

LOG_FILE_TEMPLATE = "log/extractData.%s";

baseArgv = ["python","scripts/LabTestAnalysis/machine_learning/dataExtraction/extractData.py"];

# Which lab tests to evaluate prediction for. Call these from command-line
#do one lab
LAB_PROC_CODES = \
[
    "LABFER",
    #"LABSPLAC",
    #"LABNTBNP",
    #"LABTSH",
    #"LABLIPS",
    #"LABLAC",
    #"LABLACWB",
    #"LABTNI",
    #"LABABG",
    #"LABPHOS"
    ]
"""
"LABPTT",
#"LABMETC",
"LABMGN",
"LABPT",
"LABCAI",
"LABMB",
"LABCRP",
"LABB12",
"LABESRP",
"LABFOL",
"LABPROCT",
"LABLDH",
"LABA1C",
"LABANAS",
"LABDDIM",
"LABDDIML",
"LABHIVWBL",
#"LABCBCO",
#"LABCBCD",
#"LABMETB",
];
"""

# do one week
DATE_RANGES = \
[("2013-01-01","2013-01-02")]
"""
[   ("2013-01-01","2013-03-01"),
    ("2013-03-01","2013-05-01"),
    ("2013-05-01","2013-07-01"),
    ("2013-07-01","2013-09-01"),
    ("2013-09-01","2013-11-01"),
    ("2013-11-01","2014-01-01"),
]
"""

specificArgvList = \
    [
    ];

for labProcCode in LAB_PROC_CODES:
    for dateRangePair in DATE_RANGES:
        specificArgv = list();
        specificArgv.append(labProcCode);
        specificArgv.extend(dateRangePair);
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
