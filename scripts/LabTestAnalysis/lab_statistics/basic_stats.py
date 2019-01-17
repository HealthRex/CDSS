
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

def write_new_cnts(labs):
    columns = ['proc_code', 'order_proc_id', 'pat_id', 'order_time', 'abnormal_yn', 'lab_status', 'order_status']

    for lab in labs:
        results = get_cnt(lab=lab, lab_type='panel', columns=columns)

        df = pd.DataFrame(results, columns=columns)
        print "df.shape", df.shape
        df.to_csv('query_lab_results/%s.csv' % lab, index=False)

def get_old_cnts():
    old_cnts = pd.read_csv('LabResultMap.csv')

    old_cnts = old_cnts[['proc_code', 'count']].sort_values('count', ascending=False).drop_duplicates()
    return old_cnts

def get_new_cnts(labs):
    columns = ['lab', '2014 cnt', '2015 cnt', '2016 cnt', 'total cnt']
    years = [2014, 2015, 2016]

    all_rows = []
    for lab in labs:
        cur_res = pd.read_csv('query_lab_results/%s.csv' % lab)

        cur_res_completed = cur_res[cur_res['order_status']=='Completed']
        print "Total cnt of %s is %i, Completed cnt is %i"%(lab, cur_res.shape[0], cur_res_completed.shape[0])

        cur_row = [lab]
        for year in years:

            cur_res_completed_year = cur_res_completed[(cur_res_completed['order_time'] <= '%i-12-31'%year)
                                                    & (cur_res_completed['order_time'] >= '%i-01-01'%year)]
            cur_row += [cur_res_completed_year.shape[0]]

        cur_row.append(sum(cur_row[1:]))

        all_rows.append(cur_row)

    df = pd.DataFrame(all_rows, columns=columns).sort_values('total cnt', ascending=False)
    df.to_csv('panel_cnts/panel_cnts_byYear.csv', index=False)





def compare_cnts():
    ''


if __name__ == '__main__':
    write_new_cnts(['LABMGN'])
    # get_new_cnts(NON_PANEL_TESTS_WITH_GT_500_ORDERS)