from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd
import re
import os
try:
    os.chdir("./scripts")
except:
    try:
        os.chdir("./discharge_sum_proj/scripts")
    except:
        pass

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../mykeys/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

# Instantiate a client object so you can make queries
client = bigquery.Client()

# Create a connexion to that client
conn = dbapi.connect(client)

querry = """
WITH my_tab_notes AS (
SELECT offest_csn, 
LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(note_type_desc, ',', '_'), '/', '_'), ' ', '_'), '(', '_'), ')', '_'), '-', '_'), '`', '_')) AS note_type_desc
FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen`
),
my_tab_proc AS (
SELECT pat_enc_csn_id_coded AS offest_csn,
LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(description, ',', '_'), '/', '_'), ' ', '_'), '(', '_'), ')', '_'), '-', '_'), '`', '_')) AS note_type_desc
FROM `som-nero-phi-jonc101-secure.shc_core_2023.proc_note`
), 
my_tab AS (
SELECT * FROM my_tab_notes
UNION ALL
SELECT * FROM my_tab_proc
),
offest_tab AS (
SELECT DISTINCT offest_csn
FROM my_tab
),
my_tab_filtered AS (
SELECT *
FROM my_tab RIGHT JOIN offest_tab
ON my_tab.offest_csn = offest_tab.offest_csn
)
SELECT note_type_desc, COUNT(*) AS count_n,
FROM my_tab_filtered
GROUP BY note_type_desc
ORDER BY count_n DESC
"""

df_res = pd.read_sql_query(querry, conn)

def in_sql_ready(series, n_items):
    top_notes = series[:n_items].tolist()
    top_notes_str = ', '.join(list(map(lambda x: f"'{x}'", top_notes)))
    my_notes = f'({top_notes_str})' # my_notes takes the form: "('progress_notes', 'sign_out_note', 'discharge_summary', 'h&p', 'inpatient_consult')"
    return my_notes

# pivot the 125 most common note types
pivoted_notes = f"""
WITH modified_note AS (
SELECT offest_csn, 
CONCAT("JITTERED NOTE DATE: ", jittered_note_date, " \\n ", deid_note_text) AS deid_note_text,
LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(note_type_desc, ',', '_'), '/', '_'), ' ', '_'), '(', '_'), ')', '_'), '-', '_'), '`', '_')) AS note_type_desc
FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen`
),
modified_proc AS (
SELECT pat_enc_csn_id_coded AS offest_csn, 
CONCAT("JITTERED NOTE DATE: ", proc_start_time, " \\n ", report) AS deid_note_text,
LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(description, ',', '_'), '/', '_'), ' ', '_'), '(', '_'), ')', '_'), '-', '_'), '`', '_')) AS note_type_desc
FROM `som-nero-phi-jonc101-secure.shc_core_2023.proc_note`
), 
modified_note_type AS (
SELECT * FROM modified_note
UNION ALL
SELECT * FROM modified_proc
),
pivoted_notes AS (
SELECT * FROM 
modified_note_type
PIVOT(STRING_AGG(deid_note_text, "\\n ---NEXT NOTE---\\n" ORDER BY deid_note_text DESC) FOR note_type_desc IN {in_sql_ready(df_res['note_type_desc'], 125)})
),
full_res AS (
SELECT *, 
PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', SUBSTRING(d_c_summaries, 21, 19)) AS jittered_date_d_c_summaries
FROM pivoted_notes
),
recent_res AS (
SELECT *,
STRPOS(d_c_summaries, 'Additional Instructions   Order Comments') > 0 AS d_c_sum_truncation
FROM full_res
WHERE jittered_date_d_c_summaries > '2022-12-31'
)
SELECT *,
    CASE 
        WHEN d_c_sum_truncation
        THEN SUBSTR(d_c_summaries, 1, STRPOS(d_c_summaries, 'Additional Instructions   Order Comments') - 1)
        ELSE d_c_summaries
    END AS truncated_d_c_summaries
FROM recent_res;
"""

df = pd.read_sql_query(pivoted_notes, conn)

def quality_eval(x):
    x = [i.lower() for i in x]
    reason = ["reason for hospitalization" in i for i in x]
    history = ["history of present illness" in i for i in x]
    comorbidities = ["comorbidities" in i for i in x]
    short =  [len(i) < 10000 for i in x]
    return pd.DataFrame({"reason": reason, "history": history, "comorbidities": comorbidities, "short": short})
    
quality_res = quality_eval(df['truncated_d_c_summaries'])
final_df = df[quality_res.sum(axis=1)==4]

# Remove_multiple_spaces
final_df['truncated_d_c_summaries'] = final_df['truncated_d_c_summaries'].apply(lambda x: re.sub(r'\s+', ' ', x))

if __name__ == "__main__":
    # Check memory usage
    def memory_usage(df):
        memory_usage_bytes = df.memory_usage(deep=True).sum()
        if memory_usage_bytes < 1024 ** 3:
            memory_usage_mb = memory_usage_bytes / (1024 ** 2)
            print(f"Dataframe has {df.shape[0]} rows and {df.shape[1]} columns")
            print(f"Memory usage: {memory_usage_mb:.2f} MB")
        else:
            memory_usage_gb = memory_usage_bytes / (1024 ** 3)
            print(f"Dataframe has {df.shape[0]} rows and {df.shape[1]} columns")
            print(f"Memory usage: {memory_usage_gb:.2f} GB")
    memory_usage(df)
    print("---")
    memory_usage(final_df)