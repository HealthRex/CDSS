import pdb
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split
import csv
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import pickle
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score
from sklearn.metrics import mean_pinball_loss
import shap
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import mutual_info_regression
from numpy import arange
from sklearn.linear_model import Lasso

target_vars = ['Cost_Direct', 'Cost_Indirect', 'Cost_Total']
target='Cost_Direct'

# DISCHARGE DIET
# DISCHARGE WOUND CARE
# REASON TO CALL YOUR PHYSICIAN
# WHEN TO RESUME ACTIVITIES
# FOLLOW UP INSTRUCTIONS
# DISCHARGE MD TO CALL FOR QUESTIONS
# DISCHARGE INTERAGENCY REFERRAL TO HOME NURSING
# ADMIT TO INPATIENT
# DISCHARGE PATIENT WHEN CRITERIA MET
# NOTIFY MD:
# DISCHARGE PATIENT
features_to_remove = ['PROC_118367', 'PROC_118570', 'PROC_118573', 'PROC_118575',\
'PROC_118576', 'PROC_189185', 'PROC_189239', 'PROC_304577',\
'PROC_46821', 'PROC_735', 'PROC_400099']
num_selected_features = 50


def lasso_regression_model(train_data
						, test_data
						, target_vars
						, target
						, fs_method
						, id_name):
	# pdb.set_trace()
	alphas = np.array([10, 5, 1, 0.1, 0.01, 0.001, 0.0001])
	
	hyperparameters = {'alpha': alphas}
	
	print('Hyperparameters:')
	print(hyperparameters)
	with open('results/LASSO/LASSO_hyperparameters_'+fs_method+'.csv', 'w') as csv_file:  
	    writer = csv.writer(csv_file)
	    for key, value in hyperparameters.items():
	       writer.writerow([key, value])
	# pdb.set_trace()
	train_data_shuffled = train_data.sample(frac=1).reset_index(drop=True)  
	test_data_shuffled = test_data.sample(frac=1).reset_index(drop=True)  

	# randomCV = RandomizedSearchCV(estimator=xgb.XGBRegressor(n_jobs=-1), param_distributions=hyperparameters, n_iter=5, cv=3,scoring="roc_auc")

	randomCV = RandomizedSearchCV(estimator=Lasso(max_iter=5000), param_distributions=hyperparameters, n_iter=10, cv=3)
	randomCV.fit(train_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False), train_data_shuffled[target])

	# pdb.set_trace()
	# === Save models
	with open('results/LASSO/LASSO_model_'+fs_method+'.pkl','wb') as f:
	    pickle.dump(randomCV,f)

	(pd.DataFrame.from_dict(data=randomCV.best_params_, orient='index').to_csv('results/LASSO/best_params_LASSO_'+fs_method+'.csv', header=False))
	best_model= randomCV.best_estimator_

	predictions = best_model.predict(test_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False))    
	np.savetxt('results/LASSO/predictions_LASSO_'+fs_method+'.csv', predictions, delimiter=',')
	
	# pdb.set_trace()
	mse = mean_squared_error(y_true=test_data_shuffled[target], y_pred=predictions)
	mae = mean_absolute_error(y_true=test_data_shuffled[target], y_pred=predictions)
	evs = explained_variance_score(y_true=test_data_shuffled[target], y_pred=predictions)
	r2 = r2_score(y_true=test_data_shuffled[target], y_pred=predictions)
	mpl = mean_pinball_loss(y_true=test_data_shuffled[target], y_pred=predictions)

	with open('results/LASSO/results_LASSO_'+fs_method+'.csv', 'w') as res_file:
		res_file.write('mean_squared_error\n')
		res_file.write(str(mse))
		res_file.write('\n')
		res_file.write('mean_absolute_error\n')
		res_file.write(str(mae))
		res_file.write('\n')
		res_file.write('explained_variance_score\n')
		res_file.write(str(evs))
		res_file.write('\n')
		res_file.write('r2_score\n')
		res_file.write(str(r2))
		res_file.write('\n')
		res_file.write('mean_pinball_loss\n')
		res_file.write(str(mpl))
		res_file.write('\n')

def linear_regression_model(train_data
						, test_data
						, target_vars
						, target
						, fs_method
						, id_name):							
	# pdb.set_trace()
	train_data_shuffled = train_data.sample(frac=1).reset_index(drop=True)  
	test_data_shuffled = test_data.sample(frac=1).reset_index(drop=True)  
	model = LinearRegression()
	model.fit(train_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False), train_data_shuffled[target])

	# === Save models
	with open('results/LR/lr_model_'+fs_method+'.pkl','wb') as f:
	    pickle.dump(model,f)

	predictions = model.predict(test_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False))    
	np.savetxt('results/LR/predictions_lr_'+fs_method+'.csv', predictions, delimiter=',')
	
	# pdb.set_trace()
	mse = mean_squared_error(y_true=test_data_shuffled[target], y_pred=predictions)
	mae = mean_absolute_error(y_true=test_data_shuffled[target], y_pred=predictions)
	evs = explained_variance_score(y_true=test_data_shuffled[target], y_pred=predictions)
	r2 = r2_score(y_true=test_data_shuffled[target], y_pred=predictions)
	mpl = mean_pinball_loss(y_true=test_data_shuffled[target], y_pred=predictions)

	with open('results/LR/results_lr_'+fs_method+'.csv', 'w') as res_file:
		res_file.write('mean_squared_error\n')
		res_file.write(str(mse))
		res_file.write('\n')
		res_file.write('mean_absolute_error\n')
		res_file.write(str(mae))
		res_file.write('\n')
		res_file.write('explained_variance_score\n')
		res_file.write(str(evs))
		res_file.write('\n')
		res_file.write('r2_score\n')
		res_file.write(str(r2))
		res_file.write('\n')
		res_file.write('mean_pinball_loss\n')
		res_file.write(str(mpl))
		res_file.write('\n')
	
def xgb_regression_model(train_data
						, test_data
						, target_vars
						, target
						, fs_method
						, id_name):
	# pdb.set_trace()
	n_estimators = [100, 200, 400, 800]# [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
	# Maximum number of levels in tree
	max_depth = [4, 8, 16]# [int(x) for x in np.linspace(10, 110, num = 11)]
	# gamma = [0.001, 0.01, 0.1, 1, 10]
	learning_rate = [0.0001, 0.001, 0.01, 0.1, 1]
	# Create the random grid
	hyperparameters = {'n_estimators': n_estimators
	               , 'max_depth': max_depth
	               # , 'gamma': gamma
	               , 'learning_rate':learning_rate
	               }
	print('Hyperparameters:')
	print(hyperparameters)
	with open('results/XGB/xgb_hyperparameters_'+fs_method+'.csv', 'w') as csv_file:  
	    writer = csv.writer(csv_file)
	    for key, value in hyperparameters.items():
	       writer.writerow([key, value])
	# pdb.set_trace()
	train_data_shuffled = train_data.sample(frac=1).reset_index(drop=True)  
	test_data_shuffled = test_data.sample(frac=1).reset_index(drop=True)  

	# randomCV = RandomizedSearchCV(estimator=xgb.XGBRegressor(n_jobs=-1), param_distributions=hyperparameters, n_iter=5, cv=3,scoring="roc_auc")

	randomCV = RandomizedSearchCV(estimator=xgb.XGBRegressor(n_jobs=-1, objectvie='reg:squarederror', booster='gbtree'), param_distributions=hyperparameters, n_iter=10, cv=3)

	randomCV.fit(train_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False), train_data_shuffled[target])

	# pdb.set_trace()
	# === Save models
	with open('results/XGB/xgb_model_'+fs_method+'.pkl','wb') as f:
	    pickle.dump(randomCV,f)

	(pd.DataFrame.from_dict(data=randomCV.best_params_, orient='index').to_csv('results/XGB/best_params_xgb_'+fs_method+'.csv', header=False))
	best_model= randomCV.best_estimator_

	predictions = best_model.predict(test_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False))    
	np.savetxt('results/XGB/predictions_xgb_'+fs_method+'.csv', predictions, delimiter=',')
	
	feat_imp = pd.DataFrame(data=np.reshape(best_model.feature_importances_, (1,len(best_model.feature_importances_))), columns = train_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False).columns)
	feat_imp.to_csv('results/XGB/xgb_'+fs_method+'_feature_importance_.csv', index=False)
	# feat_imp.plot.bar()
	# plt.savefig('results/XGB/feat_importance_bar_xgb.png', dpi=300)

	# best_model.get_booster().get_score(importance_type='weight')

	
	# pdb.set_trace()
	mse = mean_squared_error(y_true=test_data_shuffled[target], y_pred=predictions)
	mae = mean_absolute_error(y_true=test_data_shuffled[target], y_pred=predictions)
	evs = explained_variance_score(y_true=test_data_shuffled[target], y_pred=predictions)
	r2 = r2_score(y_true=test_data_shuffled[target], y_pred=predictions)
	mpl = mean_pinball_loss(y_true=test_data_shuffled[target], y_pred=predictions)

	with open('results/XGB/results_xgb_'+fs_method+'.csv', 'w') as res_file:
		res_file.write('mean_squared_error\n')
		res_file.write(str(mse))
		res_file.write('\n')
		res_file.write('mean_absolute_error\n')
		res_file.write(str(mae))
		res_file.write('\n')
		res_file.write('explained_variance_score\n')
		res_file.write(str(evs))
		res_file.write('\n')
		res_file.write('r2_score\n')
		res_file.write(str(r2))
		res_file.write('\n')
		res_file.write('mean_pinball_loss\n')
		res_file.write(str(mpl))
		res_file.write('\n')

	explainer = shap.Explainer(best_model)
	shap_values = explainer(train_data_shuffled.drop(target_vars+[id_name], axis=1, inplace=False))

	shap.plots.beeswarm(shap_values, show=False)
	plt.yticks(fontsize=5)
	plt.savefig('results/XGB/shap_beeswarm_'+fs_method+'.png', dpi=300)
	plt.close()

def one_hot_encoding(X_train):
	pdb.set_trace()
	ohe = OneHotEncoder()
	ohe.fit(X_train)
	X_train_enc = ohe.transform(X_train)
	column_names = ohe.get_feature_names_out(X_train.columns)
	one_hot_encoded_frame =  pd.DataFrame(data=X_train_enc.toarray(), columns= column_names)
	return one_hot_encoded_frame

# prepare input data
def ordinal_encoding(X_train):
	# pdb.set_trace()
	oe = OrdinalEncoder()
	oe.fit(X_train)
	X_train_enc = oe.transform(X_train)	
	ordinal_encoded_frame =  pd.DataFrame(data=X_train_enc, columns= X_train.columns)
	return ordinal_encoded_frame

def select_features_f_regression(X_train, y_train, X_test, k_value):
	# pdb.set_trace()
	# configure to select all features
	fs = SelectKBest(score_func=f_regression, k=k_value)
	# learn relationship from training data
	fs.fit(X_train.iloc[:,1:], y_train)
	# transform train input data
	X_train_fs = fs.transform(X_train.iloc[:,1:])
	# transform test input data
	X_test_fs = fs.transform(X_test.iloc[:,1:])
	feature_scores = pd.DataFrame(fs.scores_, index = X_train.columns[1:], columns=['f_regression_score'])
	return X_train_fs, X_test_fs, fs, feature_scores

def select_features_mir(X_train, y_train, X_test, k_value):
	# pdb.set_trace()
	# configure to select all features
	fs = SelectKBest(score_func=mutual_info_regression, k=k_value)
	# learn relationship from training data
	fs.fit(X_train.iloc[:,1:], y_train)
	# transform train input data
	X_train_fs = fs.transform(X_train.iloc[:,1:])
	# transform test input data
	X_test_fs = fs.transform(X_test.iloc[:,1:])
	feature_scores = pd.DataFrame(fs.scores_, index = X_train.columns[1:], columns=['mutual_info_regression_score'])
	return X_train_fs, X_test_fs, fs, feature_scores


# pdb.set_trace()

data = pd.read_csv('stationary_data/stationary_dataset.csv')
data.columns = data.columns.str.strip()
data = data.loc[:, ~data.columns.isin(features_to_remove)]

# data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
# data.drop(features_to_remove, axis=1, inplace=True)

# data_x = data.loc[:, data.columns != target_var]
# data_y = data[target_var]
# data_x_for_ordinal = data_x[ordinal_encoding_features]
# data_x_for_numerical = data_x[numerical_columns]
# data_x_for_one_hot = data_x.loc[:, ~data_x.columns.isin(ordinal_encoding_features+numerical_columns)]
# data_x_ordinal_encoded = ordinal_encoding(data_x_for_ordinal)
# data_x_one_hot_encoded = one_hot_encoding(data_x_for_one_hot)
# data_encoded = pd.concat([data_x_for_numerical, data_x_ordinal_encoded, data_x_one_hot_encoded], axis=1)
# data_encoded[target_var] = data_y

# pdb.set_trace()
train_data, test_data = train_test_split(data, test_size=0.30)
print('Train data size is {}'.format(len(train_data)))
print('Test data size is {}'.format(len(test_data)))

# train_data= train_data.sample(200, replace=True)
# test_data= test_data.sample(100, replace=True)

X_train_fs_reg, X_test_fs_reg, fs_reg, feature_scores_reg = select_features_f_regression(train_data.drop(target_vars, axis=1, inplace=False), train_data[target], test_data.drop(target_vars, axis=1, inplace=False), num_selected_features)
X_train_fs_mir, X_test_fs_mir, fs_mir, feature_scores_mir = select_features_mir(train_data.drop(target_vars, axis=1, inplace=False), train_data[target], test_data.drop(target_vars, axis=1, inplace=False), num_selected_features)

feature_scores_reg.to_csv('results/feature_scores_reg.csv')
feature_scores_mir.to_csv('results/feature_scores_mir.csv')




selected_features_reg = feature_scores_reg.nlargest(num_selected_features, columns=['f_regression_score']).index.tolist()
selected_features_mir = feature_scores_mir.nlargest(num_selected_features, columns=['mutual_info_regression_score']).index.tolist()

# pdb.set_trace()

lasso_regression_model(train_data
					, test_data
					, target_vars
					, target
					, 'all'
					, 'patient_id')
lasso_regression_model(train_data.loc[:, train_data.columns.isin(selected_features_reg + ['patient_id'] + target_vars)]
					, test_data.loc[:, test_data.columns.isin(selected_features_reg + ['patient_id'] + target_vars)]
					, target_vars
					, target
					, 'reg'
					, 'patient_id'
					)
lasso_regression_model(train_data.loc[:, train_data.columns.isin(selected_features_mir + ['patient_id'] + target_vars)]
					, test_data.loc[:, test_data.columns.isin(selected_features_mir + ['patient_id'] + target_vars )]
					, target_vars
					, target
					, 'mir'
					, 'patient_id')



linear_regression_model(train_data
					, test_data
					, target_vars
					, target
					, 'all'
					, 'patient_id')

linear_regression_model(train_data.loc[:, train_data.columns.isin(selected_features_reg + ['patient_id'] + target_vars)]
					, test_data.loc[:, test_data.columns.isin(selected_features_reg + ['patient_id'] + target_vars)]
					, target_vars
					, target
					, 'reg'
					, 'patient_id'
					)
linear_regression_model(train_data.loc[:, train_data.columns.isin(selected_features_mir + ['patient_id'] + target_vars)]
					, test_data.loc[:, test_data.columns.isin(selected_features_mir + ['patient_id'] + target_vars)]
					, target_vars
					, target
					, 'mir'
					, 'patient_id'
					)

# pdb.set_trace()
xgb_regression_model(train_data
					, test_data
					, target_vars
					, target
					, 'all'
					, 'patient_id'
					)
xgb_regression_model(train_data.loc[:, train_data.columns.isin(selected_features_reg + ['patient_id'] + target_vars)]
					, test_data.loc[:, test_data.columns.isin(selected_features_reg + ['patient_id'] + target_vars)]
					, target_vars
					, target
					, 'reg'
					, 'patient_id'
					)
xgb_regression_model(train_data.loc[:, train_data.columns.isin(selected_features_mir + ['patient_id'] + target_vars)]
					, test_data.loc[:, test_data.columns.isin(selected_features_mir + ['patient_id'] + target_vars)]
					, target_vars
					, target
					, 'mir'
					, 'patient_id'
					)

