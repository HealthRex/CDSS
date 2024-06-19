from pivot_features import df, top_features, my_drg
from sklearn.impute import SimpleImputer
from clusterITE import *

# Keep only the rows/patients with features
df = df[~df["anon_id_1"].isna()]

# Where is located the first feature
first_feat_pos = df.columns.get_loc("anon_id_1") + 1

# Keep only the features
X = df.iloc[:, first_feat_pos:]

# Create the imputer object with a strategy of 'most_frequent' to impute by the mode
imputer = SimpleImputer(missing_values=np.nan, strategy='most_frequent')

# Fit the imputer to your data and transform it
X_imputed = pd.DataFrame(imputer.fit_transform(X)).reset_index()
    
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

# Instanciate a ClusterIte model with 2 fold cross-validation
model = ClusterIte(K=2)

# Specify a range for the no. of clusters and fit this model to the data
model.fit(X_imputed, Y)

# Fit mixture of experts
def custom_tf_model(n_clusters):
    model = Sequential()
    ## Write your favorite architecture here...
    model.add(Dense(10, use_bias=True, activation='relu'))
    model.add(Dense(10, use_bias=True, activation='relu'))
    ## ... but make sure to finish the network like so
    model.add(Dense(n_clusters, use_bias=True, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    return model

# For the expert networks, define any sklearn architecture of your choice
# and store both expert and gating network in a dictonary
base_learners = {'experts': RandomForestRegressor(n_estimators=100, max_depth=10, max_features=2),
                 'gating_net': custom_tf_model}

# Instanciate a ClusterIte model with 5 fold cross-validation
cv_model = ClusterIte_cv(nb_folds=5, **base_learners)

# Specify a range for the no. of clusters and fit this model to the data
cv_model.fit(X_imputed, Y, cluster_range = range(1,51,3), maxit=10)

# Plot the result
cv_model.plot()