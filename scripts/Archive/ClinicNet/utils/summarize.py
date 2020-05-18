import pandas as pd
import os
import gc
import sys, getopt

features = {
'RaceWhiteHispanicLatino': 'clinitem_72407.pre',
'RaceWhiteNonHispanicLatino': 'clinitem_72401.pre',
'RaceHispanicLatino': 'clinitem_72409.pre',
'RaceBlack': 'clinitem_72413.pre',
'RaceAsian': 'clinitem_72405.pre',
'RacePacificIslander': 'clinitem_72420.pre',
'RaceNativeAmerican': 'clinitem_72427.pre',
'RaceOther': 'clinitem_72412.pre',
'RaceUnknown': 'clinitem_72411.pre',
'Male': 'clinitem_72408.pre',
'Female': 'clinitem_72402.pre',
'Birth1910s': 'clinitem_72422.pre',
'Birth1920s': 'clinitem_72421.pre',
'Birth1930s': 'clinitem_72410.pre',
'Birth1940s': 'clinitem_72406.pre',
'Birth1950s': 'clinitem_72403.pre',
'Birth1960s': 'clinitem_72400.pre',
'Birth1970s': 'clinitem_72415.pre',
'Birth1980s': 'clinitem_72404.pre',
'Birth1990s': 'clinitem_72414.pre'
}


def main(argv):
	data_dir = ''
	try:
		opts, args = getopt.getopt(argv,"hi:")
	except getopt.GetoptError:
		print('summarize.py -i <data_directory> [-h]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('summarize.py -i <data_directory> [-h]')
			print('')
			print('This script prints out summary data (e.g. demographics) for data stored in HDF5 format in <data_directory>.')
			sys.exit()
		if opt == '-i':
			data_dir = arg
	if len(argv) < 1:
		print('summarize.py -i <data_directory> [-h]')
		sys.exit(2)

	data = None
	for filename in os.listdir(data_dir):
		if filename.endswith(".hdf5") or filename.endswith(".h5"):
			fname = data_dir + "/" + filename
			print("Reading file: {}".format(fname))
			data_x = pd.read_hdf(fname, 'data_x')
			data_x = data_x.loc[:,features.values()].astype('int64')
			data_s = pd.read_hdf(fname, 'data_s')
			data_s = data_s.loc[:,'patient_id']
			if data is None:
				data = pd.concat([data_x, data_s], axis=1)
			else:
				data = data.append(pd.concat([data_x, data_s], axis=1))
			del data_x
			del data_s
			gc.collect()

	data = data.rename(columns={v:k for k,v in features.items()})
	data = data.groupby(['patient_id']).max().clip(upper=1)
	print(data.sum().to_string())
	print("Total number of patients: {}".format(data.shape[0]))
	print("Percentages:")
	print((data.sum() / data.shape[0]).to_string())

if __name__ == "__main__":
   main(sys.argv[1:])

