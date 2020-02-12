from google.cloud import bigquery
from medinfo.db.bigquery import bigQueryUtil
import datetime
import pandas
import time

bq_client = bigQueryUtil.BigQueryClient()
sql = "select * from  `datalake_47618.order_med` where med_description =  'ZOLOFT PO' "
query1 = bq_client.queryBQ(sql)
df = query1.to_dataframe()

for row_index,row in df.iterrows():
   print '\nrow number:',row_index, '\n-------------' 
   time.sleep(1)
   print row 
