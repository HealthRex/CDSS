def drg_to_imp(my_drg):
    from drg_to_dat import drg_to_dat
    from sklearn.impute import SimpleImputer
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    
    df = drg_to_dat(my_drg)
    
    if len(df) < 400:
        print(f"DRG ID {my_drg} has less than 400 patients")
        return # Skip DRGs with less than 400 patients

    # Keep only the rows/patients with features
    df = df[~df["anon_id_1"].isna()]

    # Drop the variable 'DummyFeature' as it all ones
    df = df.drop('DummyFeature', axis=1)

    # Drop all columns with only one unique value (Nan)
    df = df.drop(columns=list(df.columns[df.isna().all()]))

    ### Data description

    # Where is located the first feature
    first_feat_pos = df.columns.get_loc("anon_id_1") + 1

    # Select columns with only one unique value (eg. 'race_Non-Hispanic', 'race_White', 'sex_Female', etc.)
    columns_with_one_unique_value = df.columns[df.nunique() == 1]

    # Replace NaN values in these columns with 0
    df.loc[:, columns_with_one_unique_value] = df.loc[:, columns_with_one_unique_value].fillna(0)

    # Create Table 1
    feat_0p_names = list(df.columns[first_feat_pos:])[0:15]

    # Sort features by number of missing values
    sorted_features_names = list(df.loc[:,df.columns[first_feat_pos:]].isna().sum().sort_values().index)

    # Four quantiles of cost 
    #q = 4
    #quantiles_data = pd.qcut(df['Cost_Direct_Scaled'], q, labels=[f"Q{i+1}" for i in range(q)])
    #df.insert(1, 'Cost_Adj_Quantiles', quantiles_data)

    #table1 = TableOne(df, columns=sorted_features_names, groupby='Cost_Adj_Quantiles', pval=True)
    #print(table1.tabulate(tablefmt="github"))

    ### Data preparation

    # Keep only the features
    X = df.iloc[:, 1+first_feat_pos:] # (1+ because we added the 'Cost_Adj_Quantiles' column)

    # Cbind a mask for missing values
    X = pd.concat([X, X.isna()], axis=1)

    # Create an imputer object with a strategy of 'most_frequent' to impute by the mode
    imputer = SimpleImputer(missing_values=np.nan, strategy='most_frequent')

    # Fit the imputer to the data and transform it
    X_imputed = pd.DataFrame(imputer.fit_transform(X))
        
    # Boolean vector for features with non-unique values
    non_unique_feat = X_imputed.apply(lambda x: x.nunique()>1, axis=0) 

    # Keep only the features with non-unique values
    X_imputed = np.array(X_imputed.loc[:, non_unique_feat]).astype(float)

    # Normalize the features
    X_imputed = (X_imputed - X_imputed.mean(axis=0)) / X_imputed.std(axis=0)

    # Keep only the target
    Y = np.array(df["Cost_Direct_Scaled"])

    # Normalize the target
    Y = (Y - Y.mean()) / Y.std()
    
    return X_imputed, Y

import os
os.chdir('/Users/grolleau/Desktop/github repos/CDSS/scripts/cost_variability_2024/scripts/pipeline/')

X_imputed, Y = drg_to_imp(2334)

import numpy as np
from mapie.regression import MapieRegressor
from sklearn.ensemble import RandomForestRegressor
clf = RandomForestRegressor(n_estimators=1000,  
                                    min_samples_split=2,  
                                    min_samples_leaf=1, 
                                    max_depth=None,  
                                    max_features=1) 
clf.fit(X_imputed, Y)

mapie_reg = MapieRegressor(estimator=clf, cv="prefit")
mapie_reg = mapie_reg.fit(X_imputed, Y)
y_pred, y_pis = mapie_reg.predict(X_imputed, alpha=0.5)
print(y_pis[:, :, 0])

# Conformalized Quantile Regression to be continued as in 
# https://mapie.readthedocs.io/en/latest/examples_regression/4-tutorials/plot_cqr_tutorial.html
# https://mapie.readthedocs.io/en/latest/quick_start.html#run-mapieregressor