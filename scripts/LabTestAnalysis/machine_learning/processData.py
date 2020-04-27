import glob, gzip
import pandas as pd


def preprocessData(filepath, imp_method, filename, lab_type):
	OUTPUT_FOLDER = 'processedFeatureMatrixData/'

	df = pd.read_csv(filepath, na_values='None', sep='\t')

	colnames = [x for x in list(df) if '.post' not in x]

	if 'featureMatrix.SepsisICU' in filepath:
		df['y'] = df['Death.postTimeDays'] < 30
		colsToRemove = [
			'patient_id',
			'encounter_id',
			'firstItemDate',
			'lastContiguousItemDate',
			'payorTitle',
			'index_time',
			'days_until_end',
			'Death.pre',
			'Birth.pre']
		preTimeDays = ['Death']
		tests = [
			'BP_High_Systolic',
			'BP_Low_Diastolic',
			'FiO2',
			'Glasgow Coma Scale Score',
			'Pulse',
			'Resp',
			'Temp',
			'Urine',
			'WBC',
			'HCT',
			'PLT',
			'NA',
			'K',
			'CO2',
			'BUN',
			'CR',
			'TBIL',
			'ALB',
			'LAC',
			'ESR',
			'CRP',
			'TNI',
			'PHA',
			'PO2A',
			'PCO2A',
			'PHV',
			'PO2V',
			'PCO2V']
		colsToSubtractMean = [
			'bpDiastolic',
			'bpSystolic',
			'pulse',
			'respirations',
			'temperature']
		suffixesToRemove = [
			'.min',
			'.max',
			'.median',
			'.mean',
			'.std',
			'.first',
			'.last',
			'.proximate']
	elif 'sampleData' in filepath:
		df['y'] = df['Death.postTimeDays'] < 30
		colsToRemove = [
			'patient_id',
			'encounter_id',
			'resultItemId',
			'resultTime',
			'Death.pre',
			'Birth.pre']
		preTimeDays = [
			'Death',
			'Male',
			'Female']
		tests = [
			'WBC',
			'HCT',
			'PLT',
			'NA',
			'K',
			'CO2',
			'BUN',
			'CR',
			'TBIL',
			'ALB',
			'LAC',
			'ESR',
			'CRP',
			'TNI',
			'PHA',
			'PO2A',
			'PCO2A',
			'PHV',
			'PO2V',
			'PCO2V']
		suffixesToRemove = [
			'.min',
			'.max',
			'.median',
			'.mean',
			'.std',
			'.first',
			'.last',
			'.proximate',
			'.firstTimeDays',
			'.lastTimeDays',
			'.proximateTimeDays']
	else:
		colsToRemove = ['Birth.pre']
		preTimeDays = [
			'Male',
			'Female',
			'RaceWhiteNonHispanicLatino',
			'RaceAsian',
			'RaceWhiteHispanicLatino',
			'RaceHispanicLatino',
			'RaceUnknown',
			'RaceOther',
			'RaceBlack',
			'RacePacificIslander',
			'RaceNativeAmerican']
		diagnosisGroups = [
			'LiverModSevere',
			'Rheumatic',
			'CHF',
			'COPD',
			'Renal',
			'PepticUlcer',
			'Malignancy',
			'MI',
			'PeripheralVascular',
			'Cerebrovascular',
			'DiabetesComplications',
			'HemiplegiaParaplegia',
			'MalignancyMetastatic',
			'AIDSHIV',
			'Dementia',
			'LiverMild',
			'Diabetes']
		treatmentTeams = [
			'CCU-HF',
			'Cardiology',
			'HemeOnc',
			'MICU',
			'SICU',
			'CVICU',
			'SurgerySpecialty',
			'Psychiatry',
			'Neurology',
			'Trauma',
			'Medicine',
			'Transplant']
		labResults = {
			'LABFER': [
				'CRP',
				'PCO2V',
				'FERRITIN',
				'PCO2A',
				'WBC',
				'NA',
				'BUN',
				'CA',
				'ESR',
				'HCT',
				'K',
				'TBIL',
				'PLT',
				'CR',
				'TNI',
				'CO2',
				'PO2A',
				'PHA',
				'ALB',
				'LAC',
				'PHV',
				'PO2V'
			],
			'LABNTBNP': [
				'CRP',
				'PCO2V',
				'PCO2A',
				'WBC',
				'NA',
				'BUN',
				'CA',
				'ESR',
				'HCT',
				'K',
				'BNP',
				'TBIL',
				'PLT',
				'CR',
				'TNI',
				'CO2',
				'PO2A',
				'PHA',
				'ALB',
				'LAC',
				'PHV',
				'PO2V'
			],
			'LABSPLAC': [
				'CRP',
				'PCO2V',
				'PCO2A',
				'WBC',
				'SPLACW',
				'NA',
				'BUN',
				'LACWBL',
				'CA',
				'ESR',
				'HCT',
				'K',
				'TBIL',
				'PLT',
				'CR',
				'TNI',
				'CO2',
				'PO2A',
				'PHA',
				'ALB',
				'LAC',
				'PHV',
				'PO2V'
			],
			'LABTSH': [
				'CRP',
				'PCO2V',
				'TSH',
				'PCO2A',
				'WBC',
				'NA',
				'BUN',
				'CA',
				'ESR',
				'HCT',
				'K',
				'TBIL',
				'PLT',
				'CR',
				'TNI',
				'CO2',
				'PO2A',
				'PHA',
				'ALB',
				'LAC',
				'PHV',
				'PO2V'
			]
		}

	for rem in colsToRemove:
		colnames.remove(rem)

	for rem in preTimeDays:
		colnames.remove(rem + '.preTimeDays')

	for rem in diagnosisGroups:
		colnames.remove(rem + '.pre.1d')
		colnames.remove(rem + '.pre.2d')
		colnames.remove(rem + '.pre.4d')
		colnames.remove(rem + '.pre.7d')
		colnames.remove(rem + '.pre.14d')
		colnames.remove(rem + '.pre.30d')
		colnames.remove(rem + '.pre.90d')
		colnames.remove(rem + '.pre.180d')
		colnames.remove(rem + '.pre.365d')
		colnames.remove(rem + '.pre.730d')
		colnames.remove(rem + '.pre.1460d')

	for rem in treatmentTeams:
		colnames.remove(rem + '.preTimeDays')
		colnames.remove(rem + '.pre')
		colnames.remove(rem + '.pre.1d')
		colnames.remove(rem + '.pre.2d')
		colnames.remove(rem + '.pre.4d')
		colnames.remove(rem + '.pre.7d')
		colnames.remove(rem + '.pre.14d')
		colnames.remove(rem + '.pre.90d')
		colnames.remove(rem + '.pre.180d')
		colnames.remove(rem + '.pre.365d')
		colnames.remove(rem + '.pre.730d')
		colnames.remove(rem + '.pre.1460d')

	for rem in labResults[lab_type]:
		# ['1', '3', '7', '30', '90']
		for time in ['1', '7', '30', '90']:
			for suffix in ['count', 'countInRange', 'min', 'max', 'median', 'mean', 'std', 'first', 'last', 'diff', 'slope', 'proximate', 'firstTimeDays', 'lastTimeDays', 'proximateTimeDays']:
				colnames.remove(rem + '.-' + time + '_0.' + suffix)

	df = df.filter(items=colnames)

	# remove everything except count of tests and count of tests in range

	# testsToRemove = []
	# for test in tests:
	# 	# use (mostRecent - first) / mean
	# 	df[test + '.normalizedDelta'] = (df[test + '.last'] - df[test + '.first']) / df[test + '.mean']
	# 	for suf in suffixesToRemove:
	# 		testsToRemove.append(test + suf)
	# df = df.drop(testsToRemove, axis=1)

	# # convert true / false to 1 / 0
	# df = df * 1

	# df[colsToSubtractMean] = (df[colsToSubtractMean] - df.mean()[colsToSubtractMean]) / df.std()[colsToSubtractMean]

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
	df.to_csv(OUTPUT_FOLDER + 'processed_' + imp_method + '_' + filename + '.csv', index=False)
	return 'success'


if __name__ == '__main__':
	INPUT_FOLDER = 'rawFeatureMatrixData/'

	# filename = 'sampleData.csv'
	# filename = 'featureMatrix.SepsisICU.csv'

	# imp_method = 'zero'
	# imp_method = 'mean'
	imp_method = 'median'

	# print preprocessData(INPUT_FOLDER + filename, imp_method, filename[:-4])


	for filepath in glob.glob(INPUT_FOLDER + 'labFeatureMatrix*.tab.gz'):
		print(filepath)
		print(preprocessData(gzip.open(filepath),
			imp_method,
			filepath.split('/')[-1][:-7],
			filepath.split('.')[-3]))

		# pd.read_csv(gzip.open(filepath), na_values='None', sep='\t') \
		# 	.to_csv(filepath.split('/')[-1][:-7] + '.csv', index=False)



'''
for publication: people want to know what actually makes a difference
"what are the factors?"

for the heldout test cases, find the ones with high accuracy
make a calibration curve

go through models, for each model report accuracy/results

sklearn has Pipeline object / concept

april 24 machine learning in healthcare paper submission
'''