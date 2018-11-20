# Get all orderset usage instances from 2014-01-01 onwards; based on unique (patient_id, timestamp) pairings

import glob
import sys, os
from cStringIO import StringIO
from datetime import datetime, timedelta
from dateutil import parser

os.chdir('/Users/jwang/Desktop/CDSS/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/CDSS')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;
from medinfo.db.DBUtil import NUMBER, BOOLEAN, STRING, DATETIME;

DATA_QUERY = """
SELECT DISTINCT 
    soom.protocol_id,
    soom.protocol_name,
    som.pat_id, 
    som.ordering_date
FROM 
    stride_order_med AS som 
    JOIN 
        stride_orderset_order_med AS soom 
    ON 
        som.order_med_id = soom.order_med_id
WHERE 
    som.ordering_date::DATE > DATE '2014-01-01'
    AND NOT section_name = 'Ad-hoc Orders'
GROUP BY 
    soom.protocol_id,
    soom.protocol_name,
    som.ordering_date, 
    som.pat_id
UNION 
SELECT DISTINCT 
    soop.protocol_id, 
    soop.protocol_name,
    sop.pat_id, 
    sop.ordering_date
FROM 
    stride_orderset_order_proc AS soop
    JOIN 
        stride_order_proc AS sop 
    ON 
        soop.order_proc_id = sop.order_proc_id
WHERE 
    sop.ordering_date::DATE > DATE '2014-01-01'
    AND NOT section_name = 'Ad-hoc Orders'
GROUP BY 
    soop.protocol_id, 
    soop.protocol_name,
    sop.pat_id, 
    sop.ordering_date
;
"""
DATADIR = "/Users/jwang/Desktop/Chen/OrderSetOptimization/Results/2014-2017"
outf = open("{0}/orderset_usage_instances.csv".format(DATADIR), "w")
outf.write("orderset_id,orderset_name,patient_id,ordering_date\n")

results = DBUtil.execute(DATA_QUERY);
for line in results:
    outf.write("{0},{1},{2},{3}\n".format(line[0], line[1], line[2], line[3]))
outf.close()

