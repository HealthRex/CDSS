# python file that accepts arguments  passed in commandline as sql

from google.cloud import bigquery
import shlex
import  sys 
from sys import argv 
cmdline = " ".join(map(shlex.quote, sys.argv[1:]))
client = bigquery.Client(project='mining-clinical-decisions')
project_id = 'mining-clinical-decisions'
sql = str(cmdline)
# Run a Standard SQL query using the environment's default project
df = client.query(sql).to_dataframe()
df = client.query(sql, project=project_id).to_dataframe()
print(df)
