import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
sync_environment = "/Users/jonc101/Box Sync/Jonathan Chiang's Files/mining-clinical-decisions/stroke/"
# using venv in biomedical data science folder for version control
df = pd.read_csv(sync_environment + "stroke_cohort.csv")
#print(df.tail())

for col in df.columns:
    print(col)

y_val = df["tpaOrderTime"]
x_val = df.drop(columns=['jc_uid',
                        'tpaOrderTime',
                        'event_type',
                        'pat_enc_csn_id_coded',
                        'pat_class',
                        'jc_uid'])

print(x_val.tail())

x_train, x_test, y_train, y_test = train_test_split(x_val,
                                                    y_val,
                                                    test_size = 0.25,
                                                    random_state = 0)

print(x_train)
print(x_test)
