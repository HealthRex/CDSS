
import LocalEnv
import os
import numpy as np
np.set_printoptions(threshold=np.nan)
np.set_printoptions(linewidth=np.nan)
np.set_printoptions(precision=3)
import pandas as pd
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.precision', 3)
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

data_folder = os.path.join(LocalEnv.PATH_TO_CDSS,
                           "scripts/LabTestAnalysis/machine_learning/data-panels/")

def jitter_processed_matrix(lab, pat_num_limit=100):
    data_file = "%s-normality-matrix-10000-episodes-processed.tab"%lab
    data_path = os.path.join(data_folder, lab, data_file)
    fm_io = FeatureMatrixIO()
    df = fm_io.read_file_to_data_frame(data_path)

    '''
    Reset the pat ids
    '''
    pat_ids = sorted(set(df['pat_id'].values.tolist()))

    pat_ids = pat_ids[:pat_num_limit]

    pat2pat = {}
    for i, pat_id in enumerate(pat_ids):
        pat2pat[pat_id] = i
    df['pat_id'] = df['pat_id'].apply(lambda x: pat2pat[x] if x in pat2pat else None)
    df = df.dropna()

    print(np.array_repr(df.values))
    print(df.columns)

    #fm_io.write_data_frame_to_file(df, data_path.replace('processed', 'processed-jittered'))


if __name__ == '__main__':
    # print inspect.getfile(inspect.currentframe())
    jitter_processed_matrix("LABA1C", pat_num_limit=100)