from google.cloud import bigquery
from medinfo.db.bigquery import bigQueryUtil
import datetime
import pandas
import sys 
import time

bq_client = bigQueryUtil.BigQueryClient()

# letter that you searching for  first 
a1 = sys.argv[1]

# number of rows
a2 = sys.argv[2]

sql = ["select count(med_description) as med_count, med_description from datalake_47618.order_med where lower(med_description) like \'"  , a1 , "%' group by med_description order by med_count  desc limit", a2 ]
sql1 = ''.join(sql)
query1 = bq_client.queryBQ(sql1)
df = query1.to_dataframe()

for row_index,row in df.iterrows():
   print '\nrow number:',row_index, '\n-------------' 
   time.sleep(1)
   print row
