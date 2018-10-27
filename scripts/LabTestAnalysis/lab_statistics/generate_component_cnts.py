

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery

# Function aim:
# Count the num of component orders for each of years after 2010 (2010-2017)

# Output:
# WBC, 2017, 2016, ..., 2010
# HGB, 2017, 2016, ..., 2010

# Obtained from CNPP
COMPONENT_TESTS = ['WBC', 'HGB', 'PLT', 'NA', 'K', 'CL',
                       'CR', 'BUN', 'GLU', 'CO2', 'CA', 'HCO3', # good, from 'LABMETB'
                        'TP', 'ALB', 'ALKP', 'TBIL', 'AST', 'ALT',
                       'DBIL', 'IBIL', 'PHA', 'PCO2A', 'PO2A']

def get_orders_per_year(lab_name, lab_col, table_name, years):

    query = SQLQuery()
    query.addSelect('base_name')
    query.addSelect('result_date')
    query.addFrom('stride_order_results')
    query.addWhere('base_name=\'%s\''%lab_name)
    query.addWhere("result_date >= '2010-01-01'")
    query.addWhere("result_date <= '2017-12-31'")
    # query.setLimit(100)

    all_recs = DBUtil.execute(query)

    cnts = [0] * len(years)
    for one_rec in all_recs:
        ind = one_rec[1].year - years[0]
        cnts[ind] += 1

    f.write(lab_name+'\t')
    for cnt in cnts:
        f.write(str(cnt)+'\t')
    f.write('\n')

f = open('component_cnts_over_years.txt', 'w')
f.write('Base\t')
time_range = range(2010,2018,1)
for time in time_range:
    f.write(str(time)+'\t')
f.write('\n')
f.close()

for component in COMPONENT_TESTS:
    f = open('tmp.txt', 'a')
    get_orders_per_year(lab_name=component,
                        lab_col='base_name',
                        table_name='stride_order_results',
                        years=time_range)
    f.close()

# get_orders_per_year(lab_name='HGB',
#                     lab_col='base_name',
#                     table_name='stride_order_results',
#                     years=time_range)