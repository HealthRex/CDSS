from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import os
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/grolleau/Desktop/github repos/Cost variability/json_credentials/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

# Instantiate a client object so you can make queries
client = bigquery.Client()

# Create a connexion to that client
conn = dbapi.connect(client)

feature_query = """
WITH
feat_mat AS 
(
    SELECT
      REGEXP_REPLACE(
        CASE 
          WHEN STRPOS(feature, '_') > 0 THEN SPLIT(feature, '_')[SAFE_OFFSET(0)] 
          ELSE feature 
        END,
      r'[(),/%.]', '') as mod_feature,
      pre_feat_mat.*, cohort.anon_id
    FROM `som-nero-phi-jonc101.francois_db.baseline_inpatientmortality_feature_matrix_bow` as pre_feat_mat LEFT JOIN
        `som-nero-phi-jonc101.francois_db.20240604_costvariability_grolleau_baseline_inpatientmortality_cohort` AS cohort
      ON pre_feat_mat.observation_id = cohort.observation_id
)

SELECT mod_feature, COUNT(mod_feature) as count
FROM feat_mat
GROUP BY mod_feature
ORDER BY count DESC
"""

df = pd.read_sql_query(feature_query, conn)

# turn column into list
top_features = df[:1000]['mod_feature'].tolist()
top_features_str = ', '.join(list(map(lambda x: f"'{x}'", top_features)))
my_features = f'({top_features_str})' # my_features takes the form: "('race', 'SpO2', 'Resp', 'Pulse', 'Temp', 'GLU')"

my_drg = 2259
# 2259 is "psychoses": 937 unique patients in the cost database
# 2592 is "septicemia and disseminated infections": 2418 unique patients in the cost database

pivot_merge_query = f"""
WITH 
one_drg AS
(SELECT *
FROM `som-nero-phi-jonc101-secure.proj_IP_variation.matched_drg_cost_adms`
WHERE drg_id = '{my_drg}'),

one_drg_first_hospi AS
(SELECT anon_id, MIN(adm_date_jittered) AS date_first_hosp
FROM one_drg
GROUP BY anon_id),

cost_drg AS 
(SELECT cost.*
FROM one_drg_first_hospi LEFT JOIN one_drg AS cost
ON one_drg_first_hospi.anon_id = cost.anon_id AND one_drg_first_hospi.date_first_hosp = cost.adm_date_jittered),

feat_mat AS 
(
    SELECT
      REGEXP_REPLACE(
        CASE 
          WHEN STRPOS(feature, '_') > 0 THEN SPLIT(feature, '_')[SAFE_OFFSET(0)] 
          ELSE feature 
        END,
      r'[(),/%.]', '') as mod_feature,
    pre_feat_mat.*, cohort.anon_id
    FROM `som-nero-phi-jonc101.francois_db.baseline_inpatientmortality_feature_matrix_bow` as pre_feat_mat LEFT JOIN
        `som-nero-phi-jonc101.francois_db.20240604_costvariability_grolleau_baseline_inpatientmortality_cohort` AS cohort
      ON pre_feat_mat.observation_id = cohort.observation_id
),

time_feat_mat AS
(SELECT feat_mat_drg.*, TIMESTAMP_DIFF(TIMESTAMP(feat_mat_drg.index_time), TIMESTAMP(cost_drg.adm_date_jittered), HOUR) AS time_to_feature 
FROM (SELECT *
FROM feat_mat
WHERE anon_id IN (SELECT anon_id FROM cost_drg)) AS feat_mat_drg LEFT JOIN cost_drg
ON feat_mat_drg.anon_id = cost_drg.anon_id
),

selected_feat_mat AS 
(SELECT anon_id, mod_feature, value
FROM (SELECT anon_id, mod_feature, time_to_feature, ROW_NUMBER() OVER(PARTITION BY anon_id, mod_feature ORDER BY time_to_feature) AS occ,
        value
FROM (SELECT * 
FROM time_feat_mat
WHERE time_to_feature > 0 AND time_to_feature <= 48)
)
WHERE occ = 1 AND mod_feature IN {my_features}
),

pivoted_feat_mat AS 
(SELECT * FROM selected_feat_mat
PIVOT(SUM(value) FOR mod_feature IN {my_features} ))

SELECT * FROM cost_drg LEFT JOIN pivoted_feat_mat
ON cost_drg.anon_id = pivoted_feat_mat.anon_id
"""

df = pd.read_sql_query(pivot_merge_query, conn)

# count the number of patients with matched features
df["anon_id_1"].describe()

## Problems:
# Few unique patients in the cost database even for the most common DRGs: 937 for "psychoses" and 2418 for "septicemia and disseminated infections"

# After joining on som-nero-phi-jonc101, we find that only ~6% of these patients (56/937, 139/2418) have features measured in the first 48 hours of their hospital stay

## Possible solutions:
# Ask for an updated version of the cost database 

# Make sure that jitter is the same in cost and feature tables! If not, need to know how can we unjitter the tables?
# See line: TIMESTAMP_DIFF(TIMESTAMP(feat_mat_drg.index_time), TIMESTAMP(cost_drg.adm_date_jittered), HOUR) AS time_to_feature 