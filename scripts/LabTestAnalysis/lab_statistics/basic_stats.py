
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_column', 500)

from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS

def get_cnt(lab, lab_type, columns):


    if lab_type == 'panel':
        query = SQLQuery()
        for column in columns:
            query.addSelect(column)

        query.addFrom('stride_order_proc')
        query.addWhere("proc_code='%s'"%lab)
        query.addWhere("order_time >= '%s-01-01'"%str(2014))
        query.addWhere("order_time <= '%s-12-31'"%str(2016))
        # query.addWhere("order_status = 'Completed'") # TODO: what about ""


    results = DBUtil.execute(query)
    return results

def write_new_cnts():
    columns = ['proc_code', 'order_proc_id', 'pat_id', 'order_time', 'abnormal_yn', 'lab_status', 'order_status']

    for lab in NON_PANEL_TESTS_WITH_GT_500_ORDERS:
        results = get_cnt(lab=lab, lab_type='panel', columns=columns)

        df = pd.DataFrame(results, columns=columns)
        df.to_csv('cnts/%s.csv' % lab, index=False)

def get_old_cnts():
    old_cnts = pd.read_csv('LabResultMap.csv')

    old_cnts = old_cnts[['proc_code', 'count']].sort_values('count', ascending=False).drop_duplicates()
    return old_cnts

def get_new_cnts(labs):
    columns = ['lab', '2014 cnt', '2015 cnt', '2016 cnt', 'total cnt']
    df = pd.DataFrame()
    for lab in labs[1:]:
        cur_res = pd.read_csv('cnts/%s.csv' % lab)

        cur_res_completed = cur_res[cur_res['order_status']=='Completed']

        print "Total cnt of %s is %i, Completed cnt is %i"%(lab, cur_res.shape[0], cur_res_completed.shape[0])
        print cur_res[''].head()
        quit()

def compare_cnts():
    ''


if __name__ == '__main__':
    get_new_cnts(NON_PANEL_TESTS_WITH_GT_500_ORDERS)