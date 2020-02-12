from google.cloud import bigquery
from medinfo.db.bigquery import bigQueryUtil
import datetime
import pandas

bq_client = bigQueryUtil.BigQueryClient()
sql = "select * from  `datalake_47618_sample.order_med` where med_description =  'ALBUTEROL IN' "
query1 = bq_client.queryBQ(sql)
df = query1.to_dataframe()
file_name = str(datetime.datetime.now()) + '.csv'
df.to_csv(file_name, encoding='utf-8', index=False)
print query1.to_dataframe()
