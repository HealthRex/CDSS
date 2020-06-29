import pandas as pd


def preprocessData(filename, imp_method):
	DATA_FOLDER = 'dataExtraction/'

	df = pd.read_csv(DATA_FOLDER + filename, na_values='None')

	# use outcome as death.posttime days < 30
	df['y'] = (df['Death.postTimeDays'] < 30) * 1
	colnames = [x for x in list(df) if 'post' not in x]

	# throw out times
	if filename == 'featureMatrix.SepsisICU.csv':
		colsToRemove = ['patient_id', 'encounter_id', 'firstItemDate', 'lastContiguousItemDate', 'payorTitle', 'index_time', 'days_until_end', 'Death.preTimeDays', 'Death.pre', 'Birth.pre']
		tests = ['BP_High_Systolic', 'BP_Low_Diastolic', 'FiO2', 'Glasgow Coma Scale Score', 'Pulse', 'Resp', 'Temp', 'Urine', 'WBC', 'HCT', 'PLT', 'NA', 'K', 'CO2', 'BUN', 'CR', 'TBIL', 'ALB', 'LAC', 'ESR', 'CRP', 'TNI', 'PHA', 'PO2A', 'PCO2A', 'PHV', 'PO2V', 'PCO2V']
		colsToSubtractMean = ['bpDiastolic', 'bpSystolic', 'pulse', 'respirations', 'temperature']
		suffixesToRemove = ['.min', '.max', '.median', '.mean', '.std', '.first', '.last', '.proximate']
	elif filename == 'sampleData.csv':
		colsToRemove = ['patient_id', 'encounter_id', 'resultItemId', 'resultTime', 'Death.preTimeDays', 'Death.pre', 'Birth.pre', 'Male.preTimeDays', 'Female.preTimeDays']
		tests = ['WBC', 'HCT', 'PLT', 'NA', 'K', 'CO2', 'BUN', 'CR', 'TBIL', 'ALB', 'LAC', 'ESR', 'CRP', 'TNI', 'PHA', 'PO2A', 'PCO2A', 'PHV', 'PO2V', 'PCO2V']
		suffixesToRemove = ['.min', '.max', '.median', '.mean', '.std', '.first', '.last', '.proximate', '.firstTimeDays', '.lastTimeDays', '.proximateTimeDays']
	for rem in colsToRemove:
		colnames.remove(rem)

	df = df.filter(items=colnames)

	# remove everything except count of tests and count of tests in range

	testsToRemove = []
	for test in tests:
		# use (mostRecent - first) / mean
		df[test + '.normalizedDelta'] = (df[test + '.last'] - df[test + '.first']) / df[test + '.mean']
		for suf in suffixesToRemove:
			testsToRemove.append(test + suf)
	df = df.drop(testsToRemove, axis=1)

	# convert true / false to 1 / 0
	df = df * 1

	df[colsToSubtractMean] = (df[colsToSubtractMean] - df.mean()[colsToSubtractMean]) / df.std()[colsToSubtractMean]

	if imp_method == 'zero':
		# 0 imputation - fill NaNs with 0s
		df = df.fillna(0)
	elif imp_method == 'mean':
		# mean imputation - fill NaNs with mean of column
		df = df.fillna(df.mean())
	elif imp_method == 'median':
		# median imputation - fill NaNs with median of column
		df = df.fillna(df.median())
	else:
		return 'error'

	# most important is to store whether that lab test was even conducted or whether imputation

	# print df
	df.to_csv(DATA_FOLDER + 'preprocessed_' + imp_method + '_' + filename, index=False)
	return 'success'


if __name__ == '__main__':
	# filename = 'sampleData.csv'
	filename = 'featureMatrix.SepsisICU.csv'

	# imp_method = 'zero'
	# imp_method = 'mean'
	imp_method = 'median'

	print(preprocessData(filename, imp_method))

'''
for publication: people want to know what actually makes a difference
"what are the factors?"

for the heldout test cases, find the ones with high accuracy
make a calibration curve

go through models, for each model report accuracy/results

sklearn has Pipeline object / concept

april 24 machine learning in healthcare paper submission
'''