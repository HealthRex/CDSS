#!/usr/bin/python
"""
Batch driver script for running LabChangePredictionPipeline.py for various lab
orders in parallel.
"""

import subprocess;
from medinfo.common.Util import stdOpen, log, ProgressDots;

LOG_FILE_TEMPLATE = "data/log/LabChangePrediction.%s.log";

TOP_NON_PANEL_TESTS_BY_VOLUME = set([
    "LABMGN", "LABPTT", "LABPHOS", "LABTNI", "LABLACWB",
    "LABA1C", "LABHEPAR", "LABPLTS", "LABLAC","LABLIPS",
    "LABTSH", "LABHCTX", "LABLDH", "LABK", "LABNTBNP",
    "LABCRP", "LABCK", "LABESRP", "LABNA", "LABFER",
    "LABUSPG", "LABB12", "LABURNA", "LABFT4", "LABFIB",
    "LABURIC", "LABPALB", "LABUOSM", "LABNH3", "LABUCR",
    "LABTRIG", "LABFE", "LABALB", "LABUPREG", "LABHAP",
    # "LABNONGYN", # No base names.
])

# Listed as non panel, but have multiple results??
TOP_MULTI_RESULT_TESTS_BY_VOLUME = [
    "LABPT", "LABBLC", "LABBLC2", "LABCAI", "LABURNC",
    "LABCDTPCR", "LABPCTNI", "LABRESP", "LABMB", "LABGRAM",
    "LABFCUL", "LABFLDC", "LABSPLAC", "LABANER", "LABBLCTIP",
    "LABBLCSTK", "LABPCCR", "LABTRFS", "LABAFBD", "LABSTOBGD",
    "LABCSFGL", "LABCSFTP", "LABAFBC", "LABCMVQT", "LABCSFC",
    "LABLIDOL", "LABRETIC", "LABBXTG", "LABHIVWBL"
]

NON_PANEL_TESTS_WITH_GT_500_ORDERS = [
    'LABA1C', 'LABAFBC', 'LABAFBD', 'LABALB', 'LABANER', 'LABB12', 'LABBLC', 'LABBLC2',
    'LABBLCSTK', 'LABBLCTIP', 'LABBUN', 'LABBXTG', 'LABCA', 'LABCAI', 'LABCDTPCR', 'LABCK',
    'LABCMVQT', 'LABCORT', 'LABCRP', 'LABCSFC', 'LABCSFGL', 'LABCSFTP', 'LABDIGL', 'LABESRP',
    'LABFCUL', 'LABFE', 'LABFER', 'LABFIB', 'LABFLDC', 'LABFOL', 'LABFT4', 'LABGRAM',
    'LABHAP', 'LABHBSAG', 'LABHCTX', 'LABHEPAR', 'LABHIVWBL', 'LABK', 'LABLAC', 'LABLACWB',
    'LABLDH', 'LABLIDOL', 'LABLIPS', 'LABMB', 'LABMGN', 'LABNA', 'LABNH3', 'LABNONGYN',
    'LABNTBNP', 'LABOSM', 'LABPALB', 'LABPCCG4O', 'LABPCCR', 'LABPCTNI', 'LABPHOS', 'LABPLTS',
    'LABPROCT', 'LABPT', 'LABPTEG', 'LABPTT', 'LABRESP', 'LABRESPG', 'LABRETIC', 'LABSPLAC',
    'LABSTLCX', 'LABSTOBGD', 'LABTNI', 'LABTRFS', 'LABTRIG', 'LABTSH', 'LABUCR', 'LABUOSM',
    'LABUA', 'LABUAPRN', 'LABUPREG', 'LABURIC', 'LABURNA', 'LABURNC', 'LABUSPG'
]
labs_to_test = ['LABPHOS', 'LABMGN']

baseArgv = \
    ["python","LabChangePredictionPipeline.py"]

prog = ProgressDots(1,1,"Processes",total=len(labs_to_test));
for lab_name in labs_to_test:
    key = "%.3d.%s" % (prog.getCounts(), lab_name )
    key = key.replace("/","..")    # Don't want to use directory separator in temp log file name
    argv = list(baseArgv)
    argv.append(lab_name)
    log.info("Starting: " + str.join(" ", argv))
    logFile = stdOpen(LOG_FILE_TEMPLATE % key,"w")

    p = subprocess.Popen(argv, stderr=logFile);
    # Blocking sub-process call. Can just run multiple instances to parallelize, or consider  subprocess.Popen objects instead
