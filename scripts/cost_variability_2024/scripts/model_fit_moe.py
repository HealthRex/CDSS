from pivot_features import df, top_features, my_drg
from tableone import TableOne
from sklearn.impute import SimpleImputer
from clusterITE import *

# Keep a copy of the original data
ori_df = df.copy(deep=True)

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
q = 4
quantiles_data = pd.qcut(df['Cost_Adj'], q, labels=[f"Q{i+1}" for i in range(q)])
df.insert(1, 'Cost_Adj_Quantiles', quantiles_data)

table1 = TableOne(df, columns=sorted_features_names, groupby='Cost_Adj_Quantiles', pval=True)
print(table1.tabulate(tablefmt="github"))

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
Y = np.array(df["Cost_Adj"])

# Normalize the target
Y = (Y - Y.mean()) / Y.std()

# Fit mixture of experts
def custom_tf_model(n_clusters):
    model = Sequential()
    model.add(Dense(10, use_bias=True, activation='relu'))
    model.add(Dense(10, use_bias=True, activation='relu'))
    model.add(Dense(10, use_bias=True, activation='relu'))
    model.add(Dense(10, use_bias=True, activation='relu'))
    model.add(Dense(10, use_bias=True, activation='relu'))
    model.add(Dense(n_clusters, use_bias=True, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    return model

# For the expert networks, define any sklearn architecture of your choice
# and store both expert and gating network in a dictonary
base_learners = {'experts': RandomForestRegressor(n_estimators=100, max_depth=100, max_features='sqrt'),
                 'gating_net': custom_tf_model}

# Instanciate a ClusterIte model with 5 fold cross-validation
cv_model = ClusterIte_cv(nb_folds=5, **base_learners)

# Specify a range for the no. of clusters and fit this model to the data
cv_model.fit(X_imputed, Y, cluster_range = range(1,11), epsi=1e-3, maxit=10)

# Plot the result
cv_model.plot()

cv_model.r_sq_train.mean()
cv_model.r_sq.mean()

# Instanciate a ClusterIte model with 2 fold cross-validation
model = ClusterIte(K=3) #ClusterIte(K=cv_model.best_K_within_se, **base_learners)

# Specify a range for the no. of clusters and fit this model to the data
model.fit(X_imputed, Y, verbose=True, epsi=1e-9, maxit=100)

## In sample
# Caculate TSS
tss = np.sum((Y - Y.mean())**2)

# Calculate RSS
rss = np.sum((Y - model.predict(X_imputed))**2)

# Calculate R2
1-rss/tss

# Feature importances
importances = model.experts['ex_mod_0'].feature_importances_
std = np.std([tree.feature_importances_ for tree in model.experts['ex_mod_0'].estimators_], axis=0)

var_names = list(df.columns[first_feat_pos:])
all_var_names = var_names + list(map(lambda x: f"mis_{x}", var_names))
all_selected_var_names = list(pd.Series(all_var_names)[non_unique_feat])

forest_importances = pd.DataFrame({'value': importances, 'std': std}, index=all_selected_var_names).sort_values('value', ascending=False)
fig, ax = plt.subplots(figsize=(10, 10))
forest_importances['value'][:20].plot.bar(yerr=forest_importances['std'][:20], ax=ax)
ax.set_title("Feature importances using MDI")
ax.set_ylabel("Mean decrease in impurity")
fig.tight_layout()
