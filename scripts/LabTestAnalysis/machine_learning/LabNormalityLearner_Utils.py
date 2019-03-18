
from sklearn import model_selection

def split_rows(data_matrix):
    '''
    In the future, if want to re-use the column info that separates the matrix,
    can make this into a class

    :param data_matrix:
    :return:
    '''
    return model_selection.train_test_split(data_matrix)

def split_Xy(data_matrix, ylabel):
    X = data_matrix.copy()
    y = X.pop(ylabel)
    return X, y

def do_impute_sx(matrix, means):
    '''
    sxu new implementation

    Input: train_df, but does not change it
    Output: dictionary {order_proc_id: {feature: imputation value}}
    '''
    import datetime
    # TODO: alert: changes row order and indices of matrix!

    datetime_format = "%Y-%m-%d %H:%M:%S"

    matrix_sorted = matrix.sort_values(['pat_id', 'order_time']).reset_index()
    count_time_suffixs = ['preTimeDays', 'postTimeDays']  # TODO: postTimeDays should really not appear!
    stats_numeric_suffixs = ['min', 'max', 'median', 'mean', 'std', 'first', 'last', 'diff', 'slope',
                             'proximate']
    stats_time_suffixs = ['firstTimeDays', 'lastTimeDays', 'proximateTimeDays']

    impute_train = {}

    nega_inf_days = -1000000
    for i in range(0, matrix_sorted.shape[0]):
        cur_episode_id = matrix_sorted.ix[i, 'order_proc_id']
        impute_train[cur_episode_id] = {}
        for column in matrix_sorted.columns.values.tolist():
            '''
            Value not missing
            '''
            if matrix_sorted.ix[i, column] == matrix_sorted.ix[i, column]:
                continue

            '''
            Value missing
            '''
            column_tail = column.split('.')[-1].strip()

            if column in means:
                popu_mean = means[column]  # TODO: pre-compute with dict

            if column_tail in stats_numeric_suffixs:
                '''
                impute with the previous episode if available; otherwise population mean
                '''
                if i == 0 or (matrix_sorted.ix[i, 'pat_id'] != matrix_sorted.ix[i - 1, 'pat_id']) or (
                        matrix_sorted.ix[i - 1, column] != matrix_sorted.ix[i - 1, column]):
                    matrix_sorted.ix[i, column] = popu_mean  # impute_train[cur_episode_id][column] = popu_mean
                else:
                    matrix_sorted.ix[i, column] = matrix_sorted.ix[
                        i - 1, column]  # impute_train[cur_episode_id][column] = train_df_sorted.ix[i-1, column]

            elif column_tail in stats_time_suffixs:
                '''
                use the previous + time difference if available; otherwise -infinite
                '''
                if i == 0 or (matrix_sorted.ix[i, 'pat_id'] != matrix_sorted.ix[i - 1, 'pat_id']) or (
                        matrix_sorted.ix[i - 1, column] != matrix_sorted.ix[i - 1, column]):
                    # impute_train[cur_episode_id][column] = nega_inf_days
                    matrix_sorted.ix[i, column] = nega_inf_days
                else:
                    day_diff = (datetime.datetime.strptime(matrix_sorted.ix[i, 'order_time'], datetime_format) -
                                datetime.datetime.strptime(matrix_sorted.ix[i - 1, 'order_time'],
                                                           datetime_format)).days
                    # impute_train[cur_episode_id][column] = train_df_sorted.ix[i-1, column] - day_diff # TODO!

                    matrix_sorted.ix[i, column] = matrix_sorted.ix[i - 1, column] - day_diff

            elif column_tail in count_time_suffixs:
                '''
                -infinite
                '''
                # impute_train[cur_episode_id][column] = nega_inf_days
                matrix_sorted.ix[i, column] = nega_inf_days

            else:
                '''
                In all other cases, just use mean to impute
                '''
                matrix_sorted.ix[i, column] = popu_mean
                pass

    return matrix_sorted.set_index('index')

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

