# quiver_auth
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
sync_environemnt  = "/Users/jonc101/Box Sync/Jonathan Chiang's Files/mining-clinical-decisions/"

#gcp = pd.read_csv("/Users/jonc101/Box Sync/Jonathan Chiang's Files/mining-clinical-decisions/gcp.csv")
#print(gcp.head)

#gcp_parquet = gcp.to_parquet
#print(gcp_parquet)
#table = pa.Table.from_pandas(gcp)
#pq.write_table(table, sync_environemnt + 'gcp.parquet')

table2 = pq.read_table(sync_environemnt + 'gcp.parquet')


print(table2.to_pandas())
