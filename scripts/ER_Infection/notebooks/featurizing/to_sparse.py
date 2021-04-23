from scipy.sparse import csr_matrix, save_npz
import pdb

def build_vocab(data):
    """Builds vocabulary for of terms from the data. Assigns each unique term to a monotonically increasing integer."""
    vocabulary = {}
    for i, d in enumerate(data):
        for j, term in enumerate(d):
            vocabulary.setdefault(term, len(vocabulary))
    return vocabulary

def create_sparse_feature_matrix(train_data, apply_data):
    """Creates sparse matrix efficiently from long form dataframe.  We build a vocabulary
       from the training set, then apply vocab to the apply_set
       
       Parameters
       ----------
       train_data : long form pandas DataFrame
           Data to use to build vocabulary
       apply_data : long form pandas DataFrame
           Data to transform to sparse matrix for input to ML models
    
       Returns
       -------
       csr_data : scipy csr_matrix
           Sparse matrix version of apply_data to feed into ML models. 
    """
    
    train_features = (train_data
        .groupby('pat_enc_csn_id_coded')
        .agg({'features' : lambda x: list(x),
              'values' : lambda x: list(x)})
        .reset_index()
    )
    train_feature_names = [doc for doc in train_features.features.values]
    train_feature_values = [doc for doc in train_features['values'].values]
    train_csns = [csn for csn in train_features.pat_enc_csn_id_coded.values]
    
    apply_features = (apply_data
        .groupby('pat_enc_csn_id_coded')
        .agg({'features' : lambda x: list(x),
              'values' : lambda x: list(x)})
        .reset_index()
    )
    apply_features_names = [doc for doc in apply_features.features.values]
    apply_features_values = [doc for doc in apply_features['values'].values]
    apply_csns = [csn for csn in apply_features.pat_enc_csn_id_coded.values]

    
    vocabulary = build_vocab(train_feature_names)
    indptr = [0]
    indices = []
    data = []
    for i, d in enumerate(apply_features_names):
        for j, term in enumerate(d):
            if term not in vocabulary:
                continue
            else:
                indices.append(vocabulary[term])
                data.append(apply_features_values[i][j])
            if j == 0:
                # Add zero to data and max index in vocabulary to indices in case max feature indice isn't in apply features.
                indices.append(len(vocabulary)-1)
                data.append(0)
        indptr.append(len(indices))
    
    csr_data = csr_matrix((data, indices, indptr), dtype=float)
    
    return csr_data, apply_csns, vocabulary

# Query Long Feature Sequence
q_features = 
"""
SELECT f.*, EXTRACT(YEAR from f.index_time) year
FROM `mining-clinical-decisions.abx.feature_timeline_long` f
RIGHT JOIN  `mining-clinical-decisions.abx.final_cohort_table` l
USING (pat_enc_csn_id_coded)
"""

query_job = client.query(q_features)
df_features = query_job.result().to_dataframe()

df_features = df_features.sort_values('pat_enc_csn_id_coded')
df_features_val = df_features[~df_features['feature_type'].isin(['Lab Results_test', 'Flowsheet_test'])]
#df_features_test = df_features[~df_features['feature_type'].isin(['Lab Results_train', 'Flowsheet_train'])]

train_csr, train_csns, train_vocab = create_sparse_feature_matrix(training_examples, training_examples)
test_csr, test_csns, test_and_val_vocab = create_sparse_feature_matrix(training_examples, validation_examples)

# Sanity check csn order
for a, b in zip(train_labels['pat_enc_csn_id_coded'].values, train_csns):
    assert a == b
for a, b in zip(validation_labels['pat_enc_csn_id_coded'].values, val_csns):
    assert a == b
for a, b in zip(train_and_val_labels['pat_enc_csn_id_coded'].values, train_and_val_csns):
    assert a == b
for a, b in zip(test_labels['pat_enc_csn_id_coded'].values, test_csns):
    assert a == b

    