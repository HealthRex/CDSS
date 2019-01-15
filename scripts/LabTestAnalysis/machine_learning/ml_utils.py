

'''

Only operational functions
Not aware of file system organization

'''
import pandas as pd

def test_get_baseline():
    df_1 = pd.DataFrame([[123, '2014-01-01', 1, 2]], columns=['pat_id', 'order_time', 'actual', 'predict'])
    df_2 = pd.DataFrame([[456, '2015-01-01', 3]], columns=['pat_id', 'order_time', 'actual'])
    print get_baseline(df_1, df_2)
    # assert df's not changed


def get_baseline(df_train, df_test, y_label):
    df_res = df_test[['pat_id', 'order_time', y_label]].copy().rename(columns={y_label:'actual'}) # Not change the input

    prevalence = float(df_train[y_label].values.sum()) / float(df_train.shape[0])

    df_res['predict'] = df_res['actual'].apply(lambda x: prevalence) # use any column to create an extra column

    df_res = df_res.sort_values(['pat_id', 'order_time']).reset_index()
    for i in range(1, df_res.shape[0]):
        if df_res.ix[i-1, 'pat_id'] == df_res.ix[i, 'pat_id']:
            df_res.ix[i, 'predict'] = df_res.ix[i-1, 'actual']

    return df_res[['actual', 'predict']]

if __name__ == '__main__':
    test_get_baseline()
