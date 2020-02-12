from google.cloud import bigquery
from medinfo.db.bigquery import bigQueryUtil
import datetime
import pandas

bq_client = bigQueryUtil.BigQueryClient()
sql = "select * from  `datalake_47618_sample.order_med` where med_description =  'CELEXA 20 MG PO TABS' "
query1 = bq_client.queryBQ(sql)
df = query1.to_dataframe()
file_name = str(datetime.datetime.now()) + '.csv'
df.to_csv(file_name, encoding='utf-8', index=False)
print query1.to_dataframe()

#  ZOLOFT PO
#  SULFACETAMIDE SODIUM 10 %   DROP
#  ALBUTEROL IN
#  ATIVAN PO
#  ERYTHROMYCIN 5 MG/GRAM (0.5 %) OPHT OINT
#  CELEXA 20 MG PO TABS
#  AMOXICILLIN-POT CLAVULANATE 875-125 MG PO TABS
#  ASPIRIN-CALCIUM CARBONATE 81 MG-300 MG CALCIUM(777 MG) PO TABS
#  ONE TOUCH ULTRA TEST MISC STRP
#  VITAMIN D 1,000 UNIT PO TABS
