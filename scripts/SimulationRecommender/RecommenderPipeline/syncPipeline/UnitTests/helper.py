# recommender pipeline helper


def state_split(state_names, df):
    df2 = df[df['name_x'].isin(state_names)]
    return(df2)

def grade_sum(case):
    return case['grade_mean'].sum(axis = 0, skipna = True)
