'''
Regression:
predict glucose level at current time stamp
Files of input data are stored under directory "../data/preprocessed".
Output files (patient IDs) are stored under directory ""../data/plots/patients".
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import preprocessing, metrics
from sklearn.utils import shuffle
from sklearn.feature_selection import SelectFromModel, SelectKBest, f_regression
from sklearn.svm import SVR
from sklearn.linear_model import RidgeCV, LassoCV, Ridge, Lasso, LinearRegression, BayesianRidge, ElasticNet
from sklearn.ensemble import AdaBoostRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.tree import DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.impute import SimpleImputer
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel, RBF, ConstantKernel, Matern, RationalQuadratic, ExpSineSquared

from skgarden import RandomForestQuantileRegressor


PATH_TO_OUTPUT = "../data/plots/patients/"

feature_names = ['pat_idx', 'gender','age', 'closest_weight', 'npo', 'prev_glu_lvl',
                      'avg_24h_glu', 'var_24h_glu', 'weighted_sum_glu_lvl_24h', 'cur_glu_lvl', 'glu_lvl_1d_before',
                      'steroids_24h_total', 'steroids_3d_total', 'closest_a1c',
                      'since_midnight_sine', 'since_midnight_cosine',
                      'closest_crea', 'closest_crea_time_h', 'cur_ts',
                      'next_glu_time_diff_h', 'next_glu_lvl']
# time difference since short/long-acting insulin doses
short_enum = [0.5,1,3]
long_enum = [6,12,24]
for dose_time_diff in [str(i) for i in short_enum]:
    feature_names.append('short_'+dose_time_diff+'h')
for dose_time_diff in [str(i) for i in long_enum]:
    feature_names.append('long_'+dose_time_diff+'h')
feature_names.append('cur_glu_lvl')


df = pd.read_csv('../data/preprocessed/data.csv', sep=',')
df.head()

df = df.drop(df.columns[0], axis=1)  # drop first unused column
y = df["cur_glu_lvl"]

######################
# Feature Selection

selected_features = ['avg_24h_glu', 'steroids_24h_total', 'steroids_3d_total', 'closest_a1c',
                     'gender','age', 'closest_weight', 'npo',
                     'var_24h_glu', 'glu_lvl_1d_before',
                     'closest_crea', 'closest_crea_time_h',
                     'since_midnight_sine', 'since_midnight_cosine']
for dose_time_diff in [str(i) for i in short_enum]:
    selected_features.append('short_'+dose_time_diff+'h')
for dose_time_diff in [str(i) for i in long_enum]:
    selected_features.append('long_'+dose_time_diff+'h')
features = df[selected_features]


# time stamps
time = df['cur_ts']

data_IDs = df['pat_idx'].values.tolist()
data_IDs = [int(i) for i in data_IDs]


######################
# Data Process
# check for irregular data: remove nans

labels = y.values.tolist()
X = np.array(features.values.tolist())

# remove nans
X_rmnan = X
y_rmnan = labels
time_rmnan = np.array(time.tolist())
for i in range(len(selected_features)):
    nan_glu_idx = np.where(np.isnan(X_rmnan[:,i]))[0]
    X_rmnan = np.delete(X_rmnan, nan_glu_idx, 0)
    y_rmnan = np.delete(y_rmnan, nan_glu_idx, 0)
    data_IDs = np.delete(data_IDs, nan_glu_idx, 0)
    time_rmnan = np.delete(time_rmnan,nan_glu_idx)
nan_glu_idx = np.where(np.isnan(y_rmnan))[0]
X_rmnan = np.delete(X_rmnan, nan_glu_idx, 0)
y_rmnan = np.delete(y_rmnan, nan_glu_idx, 0)
data_IDs = np.delete(data_IDs, nan_glu_idx, 0)
time_rmnan = np.delete(time_rmnan,nan_glu_idx)
data_idx = range(len(data_IDs))

# dimension of feature matrix
print("dimension of feature matrix", X_rmnan.shape)


'''
# feature selection - uncomment to use, can be pipelined

fs = SelectKBest(f_regression, k=5)
# feature selection based on univariate linear regression tests
# The correlation between each regressor and the target is computed,
# ((X[:, i] - mean(X[:, i])) * (y - mean_y)) / (std(X[:, i]) * std(y)).
# It is converted to an F score then to a p-value.
# The F score is defined as the weighted harmonic mean of the test's precision and recall
#
X_new = fs.fit_transform(X_rmnan, y_rmnan)
print(X_new.shape)
# print(fs.scores_)
idx = np.argsort(-fs.scores_)[:5]
print("")
kb_features = np.array(selected_features)[idx]
print("features in order of KB Selection", kb_features)

# selected_features_target = np.copy(kb_features).tolist()
# selected_features_target.append("cur_glu_lvl")
# selected_features_target = df[selected_features_target]
#
# # df2 = df[["cur_glu_lvl"]]
# sns.pairplot(selected_features_target, diag_kind = 'kde')
# plt.savefig(PATH_TO_OUTPUT+"pairplot.png", bbox_inches='tight')

X_rmnan = X_new

'''


######################
# Train-Test-Split

tr_te_split = 0.7

unique_IDs = np.unique(data_IDs)
print("Number of unique patients: ", len(unique_IDs))

num_pat = 500  # number of patients used | len(unique_IDs)
print("Patient used:", num_pat)

unique_IDs = unique_IDs[0:num_pat]


tr_num = int(tr_te_split*len(unique_IDs))
train_IDs = unique_IDs[0:tr_num]
test_IDs = unique_IDs[tr_num:]

last_train = np.where(data_IDs==train_IDs[-1])[0][-1]
last_test = np.where(data_IDs==test_IDs[-1])[0][-1]


train_idx = np.array(data_idx)[0:last_train+1]
test_idx = np.array(data_idx)[last_train+1:last_test+1]
test_IDs = np.array(data_IDs)[last_train+1:last_test+1]

print("Try training...")
X_train = X_rmnan[train_idx,:]
y_train = y_rmnan[train_idx]
time_train = time_rmnan[train_idx]
X_test = X_rmnan[test_idx,:]
y_test = y_rmnan[test_idx]
time_test = time_rmnan[test_idx]


print("train data", X_train.shape)
print("test data", X_test.shape)


# Validation Set
# val_IDs = unique_IDs[num_pat:num_pat+int(0.1*num_pat)]
# last_val = np.where(data_IDs==val_IDs[-1])[0][-1]
# val_idx = np.array(data_idx)[last_test+1:last_val+1]
# X_val = X_rmnan[val_idx,:]
# y_val = y_rmnan[val_idx]


######################
# Data Normalization/Rescaling
scaler = preprocessing.MinMaxScaler()
X_train_rescale = scaler.fit_transform(X_train)
X_test_rescale = scaler.transform(X_test)
# X_val = scaler.transform(X_val)


######################
# Regression Models: uncomment corresponding regressor to use

# ElasticNet (LASSO)
# clf = ElasticNet(alpha=1.0, l1_ratio=1, fit_intercept=True)  # l1_ratio=1 -> LASSO
# clf.fit(X_train_rescale, y_train)


# SVR (default)
# clf = SVR(kernel='linear', gamma='scale', C=1.0, epsilon=0.1)
# clf.fit(X_train_rescale, y_train)


# SVR with validation (parameter tuning)
# # parameters tuning
# C_range = np.logspace(-3, 4, 8)
# gamma_range = np.logspace(-7, 3, 11)
# C_tested = list()
# gamma_tested = list()
# score_tested = list()
#
# print("tuning parameters...")
# num_rdm_sample = 20
# for i in range(num_rdm_sample):
#     C_i = random.choice(C_range)
#     gamma_i = random.choice(gamma_range)
#     clf = SVR(kernel='rbf', gamma=gamma_i, C=C_i, epsilon=0.1)
#     clf.fit(X_rescale, y_train)
#     R2 = clf.score(X_val, y_val)
#     print(C_i, gamma_i, R2)
#     score_tested.append(R2)
#     C_tested.append(C_i)
#     gamma_tested.append(gamma_i)
#
# for C_i in C_range:
#     for gamma_i in gamma_range:
#         clf = SVR(kernel='rbf', gamma=gamma_i, C=C_i, epsilon=0.1)
#         clf.fit(X_rescale, y_train)
#         R2 = clf.score(X_val, y_val)
#         print(C_i, gamma_i, R2)
#         score_tested.append(R2)
#         C_tested.append(C_i)
#         gamma_tested.append(gamma_i)
#
# opt_idx = np.argmax(score_tested)
# opt_C = C_tested[opt_idx]
# opt_gamma = gamma_tested[opt_idx]
# print("opt", opt_C, opt_gamma)

# clf = SVR(kernel='linear', gamma='scale', C = 10, epsilon=0.1) #gamma='scale'


# SVR with tuned parameter
# opt_C, opt_gamma = 10000, 0.1
# clf = SVR(kernel='rbf', gamma=opt_gamma, C=opt_C, epsilon=0.1) #gamma='scale'
# clf.fit(X_train_rescale, y_train)


# Random Forest Regressor
clf = RandomForestRegressor(random_state=0, n_estimators=100)  #max_depth=10,
clf.fit(X_train_rescale, y_train)


# Gaussian process regression (GPR)
# kernel = DotProduct() + WhiteKernel()
# kernel = ConstantKernel(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2))
# kernel = None
# kernel = ConstantKernel(0.1, (1e-23, 1e5)) * \
#          RBF(0.1*np.ones(X_train_rescale.shape[1]), (1e-23, 1e10) ) + \
#          WhiteKernel(0.1, (1e-23, 1e5))
# kernel = WhiteKernel()
# kernel = ConstantKernel(0.1, (0.01, 10.0))
#                * (DotProduct(sigma_0=1.0, sigma_0_bounds=(0.1, 10.0)) ** 2)
# clf = GaussianProcessRegressor(kernel=DotProduct()) #normalize_y=True , n_restarts_optimizer=2
# print("initial paras:", clf.get_params())
# clf.fit(X_train_rescale, y_train)
# print("after fitting:", clf.get_params())
# y_pred, sigma = clf.predict(X_test_rescale, return_std=True)


# Linear Regression
# clf = LinearRegression(n_jobs=-1)
# clf.fit(X_train_rescale, y_train)


# Bayesian Ridge Regression
# clf = BayesianRidge(normalize = True)
# clf.fit(X_train_rescale, y_train)
# y_pred, y_std = clf.predict(X_test_rescale, return_std=True)
# lower = y_pred - 1.645 * y_std
# upper = y_pred + 1.645 * y_std


# KRR (squared error loss combined with l2 regularization)
# clf = KernelRidge(alpha=0.1)
# clf.fit(X_train_rescale, y_train)


# Random Forest Quantile Regressor
# clf = RandomForestQuantileRegressor(random_state=0, min_samples_split=10, n_estimators=1000)
# clf.fit(X_train_rescale, y_train)
# y_pred = clf.predict(X_test_rescale)
# upper = clf.predict(X_test_rescale, quantile=98.5)
# lower = clf.predict(X_test_rescale, quantile=2.5)
# interval = upper - lower
# mean = (upper + lower) / 2


# GradientBoosting
# X_train_rescale, y_train = shuffle(X_train_rescale, y_train, random_state=0)
# clf = GradientBoostingRegressor(loss='quantile', alpha=0.7, random_state=0, n_estimators=100)
# clf.fit(X_train_rescale, y_train)


# DecisionTree
# clf = DecisionTreeRegressor(random_state=0)
# clf.fit(X_train_rescale, y_train)


# NaiveBayes
# clf = GaussianNB()
# clf.fit(X_train_rescale, y_train)


######################
# Prediction

print(clf)
y_pred = clf.predict(X_test_rescale)


######################
# Performance Measure

r2 = metrics.r2_score(y_test, y_pred)
print("R2 score",r2)
MSE = metrics.mean_squared_error(y_test, y_pred)
print("RMSE", np.sqrt(MSE))

MAE = metrics.mean_absolute_error(y_test, y_pred)
print("Mean absolute error", MAE)

# mean percentage error
MAPE = np.mean(np.abs((y_test-y_pred)/y_test))
print("Mean percentage error", MAPE)

# correct trend
trend_true = np.sign(np.diff(y_test))
trend_pred = np.sign(np.diff(y_pred))
accr = metrics.accuracy_score(trend_true, trend_pred)
print("trend accuracy:", accr)

######################
# Plot
test_diff_idx = np.where(np.diff(test_IDs))[0]

# All predictions together
# plt.plot(y_test, "bo")
# plt.plot(y_pred, "ro")
# plt.fill_between(
#     np.arange(len(upper)), lower, upper, alpha=0.2, color="r",
#     label="Pred. interval")
# # plt.xlabel("Ordered samples.")
# # plt.ylabel("Values and prediction intervals.")
# # plt.xlim([0, 500])
# plt.show()


# 2D scatter plot: true vs. predicted glucose level

plt.figure()
clf_name = clf.__str__().split("(")[0]
plt.scatter(y_test, y_pred, s=2, alpha=0.5)
plt.plot([np.min(y_test), np.max(y_test)],[np.min(y_test), np.max(y_test)], c='g', alpha=0.7)
# plt.axvline(x=70, c='r', alpha=0.5)
# plt.axvline(x=200, c='r', alpha=0.5)
plt.title(clf_name+": true vs. predicted glucose level")
plt.xlim([0, np.max(y_test)])
plt.xlabel("true glucose levels")
plt.ylim([0, np.max(y_pred)])
plt.ylabel("predicted glucose levels")
plt.savefig(PATH_TO_OUTPUT+clf_name+"("+str(num_pat)+").png", bbox_inches='tight')
plt.show()


# Sample plot of a few patients

time_test2 = np.array([tt.split('.')[0] for tt in time_test])

for j in range(len(test_diff_idx)-1):  # len(test_diff_idx)-1
    pat_indices = range(test_diff_idx[j],test_diff_idx[j+1])
    plt_pat_idx = range(len(y_test[pat_indices]))
    time_pat = time_test2[pat_indices]
    pat_test = y_test[pat_indices]
    pat_pred = y_pred[pat_indices]
    # pat_upper = upper[pat_indices]
    # pat_lower = lower[pat_indices]
    idx_pat_idx = range(len(plt_pat_idx))
    if len(time_pat) > 1:
        fig = plt.figure(figsize=(int(np.ceil(len(plt_pat_idx)) / 2), 4))

        time_dt = pd.to_datetime(time_pat)
        diff_dt = np.diff(time_dt).astype('timedelta64[h]').astype(int)
        diff_period = np.where(np.logical_or(diff_dt>72, diff_dt<0))[0]
        st_idx = 0
        for dp in diff_period:
            idx_slice = idx_pat_idx[st_idx:dp+1]
            if len(idx_slice)>1:
                plt.plot(time_pat[idx_slice], pat_test[idx_slice], 'o-', c='blue', label="true glucose levels")
                plt.plot(time_pat[idx_slice], pat_pred[idx_slice], 'x-', c='red', label="predicted glucose levels")
                # plt.fill_between(
                #     time_pat[idx_slice], pat_lower[idx_slice], pat_upper[idx_slice], alpha=0.2, color="r",
                #     label="Pred. interval")
            st_idx = dp+1

        plt.xlabel("time")
        plt.ylabel("glucose level")
        plt.legend(["true glucose levels", "predicted glucose levels", "95% interval"])
        fig.autofmt_xdate()
        clf_name = clf.__str__().split("(")[0]
        plt.title(clf_name+": Sample Patient")
        plt.savefig(PATH_TO_OUTPUT+"ind/"+clf_name+"("+str(num_pat)+")_"+str(j+1)+".png", bbox_inches='tight')
        plt.close()

