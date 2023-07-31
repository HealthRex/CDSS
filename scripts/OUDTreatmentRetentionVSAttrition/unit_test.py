import pdb
import sys
import os
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
from datetime import datetime, timedelta
import csv


pdb.set_trace()
client = bigquery.Client('som-nero-phi-jonc101');
conn = dbapi.connect(client);

query_string = '''
  SELECT distinct B.concept_name , A.*
  FROM `som-rit-phi-starr-prod.starr_omop_cdm5_deid_2022_08_10.drug_exposure` A
  JOIN `som-rit-phi-starr-prod.starr_omop_cdm5_deid_2022_08_10.concept` B on A.drug_concept_id = B.concept_id
  where B.concept_name like '%buprenorphine%naloxone%'
  and A.person_id = 30289451
  order by person_id, A.drug_exposure_start_date
'''

exposures = pd.read_sql_query(query_string, conn)
exposures = exposures.sort_values(by=['person_id', 'drug_exposure_start_DATE'])


print('The end')