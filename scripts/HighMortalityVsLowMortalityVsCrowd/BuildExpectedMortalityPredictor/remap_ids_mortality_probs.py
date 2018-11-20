# create normalized id to original id mapping
id_map = {}
sickness_metrics = open("/Users/jwang/Desktop/Results/mortality_probs.csv", "rU")
# sickness_metrics = open("/Users/jwang/Desktop/Results/mortality_or_readmission_probs.csv", "rU")
feature_matrix_10_13 = open("/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix.csv", "rU")

feature_matrix_10_13.readline()
for line in feature_matrix_10_13:
	line = line.strip().split(",")
	id_map[line[0]] = line[1]

outf = open("/Users/jwang/Desktop/Results/mortality_probs_remapped.csv", "w")
# outf = open("/Users/jwang/Desktop/Results/mortality_or_readmission_probs_remapped.csv", "w")
outf.write("patient_id,prob\n")

sickness_metrics.readline()
for line in sickness_metrics:
	line = line.strip().split(",")
	outf.write("{0},{1}\n".format(id_map[line[1]],line[2]))

outf.close()
sickness_metrics.close()
feature_matrix_10_13.close()