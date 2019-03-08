

def extract_imputation_dict(matrix):
    imputation_dict = {}

    ''' 
    
    2.For the "time since the most recent test", if no prior value exists, then we impute with 
    negative infinity. 
    '''



    return imputation_dict



def impute_by_carry_forward(matrix, impute_dict={}): # TODO: optimize list
    '''
    Why:
    Numerical results (e.g. mean and standard deviation) could be missing if an individual
    patient episode did not have those in the recent time window.
        In those cases, we carry forward the most recent statistic from the patient's record.
        If no prior values exist for that patient, then we impute with the val of each key.

    Args:
        matrix:

    Returns:

    '''
    columns_to_impute = impute_dict.keys() # TODO

    columns_relevant = ['pat_id', 'order_time', 'order_proc_id'] + columns_to_impute
    '''
    Impute for this temporary df. 
    '''
    matrix_relevant_sorted = matrix[columns_relevant].copy().sort_values(['pat_id','order_time']).reset_index()

    for i in range(0, matrix_relevant_sorted.shape[0]):
        for column in columns_to_impute:
            if matrix_relevant_sorted.ix[i, column] == matrix_relevant_sorted.ix[i, column]:
                # value not missing
                pass

            elif (i==0) or (matrix_relevant_sorted.ix[i,'pat_id'] != matrix_relevant_sorted.ix[i-1,'pat_id']):
                # no prior order
                matrix_relevant_sorted.ix[i, column] = impute_dict[column]

            else:
                matrix_relevant_sorted.ix[i, column] = matrix_relevant_sorted.ix[i-1, column]

    '''
    Use tmp df to impute the input df. 
    '''
    matrix_imputed = matrix.copy()
    for column in columns_to_impute:
        curr_impute_dict = dict(zip(matrix_relevant_sorted['order_proc_id'].values,
                                    matrix_relevant_sorted[column].values))
        matrix_imputed[column] = matrix_imputed[column].fillna(matrix_imputed['order_proc_id'].map(curr_impute_dict))

    return matrix_imputed

