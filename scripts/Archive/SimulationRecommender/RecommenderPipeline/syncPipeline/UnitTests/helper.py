# recommender pipeline helper
import pandas as pd


def state_split(state_names, df):
    df2 = df[df['name_x'].isin(state_names)]
    return(df2)

def grade_sum(case):
    return case['grade'].sum(axis = 0, skipna = True)

def sim_grader(case, grading_key):
    dt = pd.merge(case, grading_key, how = 'left', on = ['clinical_item_name', 'case', 'sim_state_name'])
    gd0 = pd.DataFrame(rFilter(dt, 'group_dependent', False))
    gd1 = rFilter(dt, 'group_dependent', True)
    gd2 = rFilter(gd1, 'group', 'abx')
    gd3 = rSort(gd2, 'score', False)
    gd4 = pd.DataFrame(gd3.iloc[[0]])
    gd5 = pd.concat([gd0, gd4])
    return sum(gd5['score'])

def rFilter(df,col, condition):
    return df[df[col]==condition]

def rSort(df, col, boolean):
    return df.sort_values(by=[col], ascending = boolean)

def rRows(df, single_row_index):
    return pd.DataFrame(df.iloc[[single_row_index]])
