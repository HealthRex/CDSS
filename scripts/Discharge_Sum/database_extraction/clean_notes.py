from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import numpy as np
import pandas as pd
import os
import re
try:
    os.chdir("./scripts")
except Exception:
    pass

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../mykeys/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

# Instantiate a client object so you can make queries
client = bigquery.Client()

# Create a connexion to that client
conn = dbapi.connect(client)

various_notes_query = """
SELECT note_type, COUNT(*) as n FROM 
(
SELECT
REPLACE(REPLACE(REPLACE(note_type, ',', '_'), '/', '_'), ' ', '_') AS note_type
FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen`
)
GROUP BY note_type
ORDER BY n DESC
"""

df = pd.read_sql_query(various_notes_query, conn)

# "(" + ", ".join(f"'{i}'" for i in list(df.note_type.values)) + ")"

# List of tuples of note_type and count
notes_n = list(zip(df.iloc[:,0], df.iloc[:,1]))

def get_notes(note_type="Progress Note, Inpatient", i=None):
    """
    Get notes of a certain type
    note_type: valid note_type
    i: most common note_type from 0 to 23
    """
    if i is not None:
        notes_query = f""" 
        SELECT deid_note_text, offest_csn, jittered_note_date, note_type
        FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` 
        WHERE note_type = '{notes_n[i][0]}'
        --AND jittered_note_date > '2019-12-31'     -- THE NEWER NOTES HAVE LESS STRUCTURE / TITLES!!!
        LIMIT 100
        """
    else:
        notes_query = f"""
        SELECT deid_note_text, offest_csn, jittered_note_date, note_type
        FROM `som-nero-phi-jonc101.Deid_Notes_JChen.Deid_Notes_SHC_JChen` 
        WHERE note_type = '{note_type}'
        --AND jittered_note_date > '2019-12-31'     -- THE NEWER NOTES HAVE LESS STRUCTURE / TITLES!!!
        LIMIT 100
        """
    return pd.read_sql_query(notes_query, conn)

def get_title_idx(text, min_title_len=2, max_title_len=10):
    words = text.split()
    all_upper = np.array([i.isupper() for i in words])
    colon_last = np.array([i[-1]==':' for i in words])
    title_end_idx = np.where(all_upper * colon_last)[0]
    title_start_idx = []
    for j in title_end_idx:
        for i in range(1,max_title_len):
            if j-i > 0 and bool(all_upper[j-i]) is True and i == max_title_len-1:
                i = None
            elif bool(all_upper[j-i]) is False:
                break
        if i is not None:
            title_start_idx.append(j-i+1 if j-i+1 > 0 else 0)
        else:
            title_end_idx = np.delete(title_end_idx, np.where(title_end_idx == j))
    title_start_idx = np.array(title_start_idx)
    not_too_short = title_end_idx - title_start_idx >= min_title_len - 1
    title_start_idx = title_start_idx[not_too_short]
    title_end_idx = title_end_idx[not_too_short]
    return title_start_idx, title_end_idx, words

# Check if the function works: get_title_idx("BLA BLA: Blaa bla BLABLA BLABLA BLABLA BLABLA BLA BLA:")

class Notes:
    def __init__(self, df: pd.DataFrame):
        assert isinstance(df, pd.DataFrame), "Input must be a pandas DataFrame"
        assert df['note_type'].nunique() == 1, "All notes must be of the same type"
        self.note_type = re.sub(r'[^a-zA-Z]', '', df.note_type[0])
        self.dss = list(df.deid_note_text)
        self.dates = list(df.jittered_note_date.dt.date.astype(str))
        self.encs = list(df.offest_csn.astype(str))

    def paragraph_to_lines(self):
        self.new_dss = []
        self.n_titles = []
        for ds in self.dss:
            title_start_idx, title_end_idx, words = get_title_idx(ds)
            self.n_titles.append(len(title_start_idx))
            if len(words) == 0:
                self.new_dss.append(" ")
                continue
            modified_text = words[0]
            for i in range(1, len(words)-1):
                    if i in title_start_idx:
                        modified_text += "\n\n" + words[i]
                    elif i in title_end_idx:
                        modified_text += " " + words[i] + "\n"
                    else:
                        modified_text += " " + words[i]    
            self.new_dss.append(modified_text)

    def export_txt(self):
        for i,new_dss in enumerate(self.new_dss):
            if self.n_titles[i] > 5:
                dest = f"../cleaned_notes/{self.note_type}/{self.encs[i]}"
                os.makedirs(str(dest), exist_ok=True)
                with open(f'{dest}/{self.dates[i]}.txt', 'w') as file:
                    file.write(new_dss)

if __name__ == "__main__":
    for i in range(100):
        try:
            df = get_notes(i=i)
            dss_instance = Notes(df)
            dss_instance.paragraph_to_lines()
            dss_instance.export_txt()
            i += 1
        except Exception:
            print(f"Finished cleaning all {i+1} note types")
            break