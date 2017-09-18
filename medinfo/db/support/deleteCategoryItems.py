from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;
from medinfo.common.Util import ProgressDots;
from medinfo.common.Util import log;

conn = DBUtil.connection();
try:
    results = DBUtil.execute("select clinical_item_id from clinical_item where clinical_item_category_id = 161",conn=conn);
    clinicalItemIds = tuple([row[0] for row in results]);
    log.info("Deleting for %s Clinical Items" % len(clinicalItemIds) );

    query = SQLQuery();
    query.addSelect("patient_item_id");
    query.addFrom("patient_item");
    query.addWhereIn("clinical_item_id", clinicalItemIds );
    
    prog = ProgressDots();
    prog.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];
    
    # Go ahead and load full result set into memory, so don't have potential concurrency issues with deleting items as traversing them
    results = DBUtil.execute(query, conn=conn );
    for row in results:
        patientItemId = row[0];
        DBUtil.execute("delete from patient_item where patient_item_id = %s", (patientItemId,), conn=conn);
        prog.update();
    prog.printStatus();
finally:
    conn.close();
