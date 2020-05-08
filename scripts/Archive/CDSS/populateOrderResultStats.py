"""
"""
import sys;
import subprocess;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Model import RowItemFieldComparator, columnFromModelList;
from medinfo.db import DBUtil;
from medinfo.dataconversion.STRIDEOrderResultsConversion import STRIDEOrderResultsConversion;


def main(argv):
    conversionProcessor = STRIDEOrderResultsConversion();
    
    conn = DBUtil.connection();
    try:
        # Pull out list of result names to look for that are not already in the calculated
        nameTable = DBUtil.execute("select name from sim_result    except    select base_name from order_result_stat", conn=conn);
        prog = ProgressDots(big=1,small=1,total=len(nameTable));
        for row in nameTable:
            baseName = row[0];
            print("Calculating Stats for %s" % baseName, file=sys.stderr);
            statModel = conversionProcessor.calculateResultStats( baseName, conn=conn );
            DBUtil.insertRow("order_result_stat", statModel, conn=conn );
            prog.update();
        prog.printStatus();
        conn.commit();
    finally:
        conn.close();

if __name__ == "__main__":
    main(sys.argv);
