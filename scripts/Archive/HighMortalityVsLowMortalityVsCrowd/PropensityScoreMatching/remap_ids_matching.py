# create normalized id to original id mapping

# Top vs. Bottom
id_map = {}
matched = open("/Users/jwang/Desktop/Results/matched_top_bottom.csv", "rU")
feature_matrix_10_13 = open("/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix.csv", "rU")

feature_matrix_10_13.readline()
for line in feature_matrix_10_13:
	line = line.strip().split(",")
	id_map[line[0]] = line[1]

top_f = open("/Users/jwang/Desktop/Results/top_patients_matched_remapped.csv", "w")
bottom_f = open("/Users/jwang/Desktop/Results/bottom_patients_matched_remapped.csv", "w")

matched.readline()
for line in matched:
	line = line.strip().split(",")
	label = int(line[61]) # column 62
	if (label == 1): # top
		top_f.write("{0}\n".format(id_map[line[1]]))
	elif (label == 0): # bottom
		bottom_f.write("{0}\n".format(id_map[line[1]]))

top_f.close()
bottom_f.close()
matched.close()
feature_matrix_10_13.close()

# Top vs. Everyone
matched = open("/Users/jwang/Desktop/Results/matched_top_everyone.csv", "rU")
everyone_f = open("/Users/jwang/Desktop/Results/everyone_patients_matched_remapped.csv", "w")
matched.readline()
for line in matched:
	line = line.strip().split(",")
	label = int(line[61]) # column 62
	if (label == 1): # top*
		continue
	elif (label == 0): # everyone
		everyone_f.write("{0}\n".format(id_map[line[1]]))

matched.close()
everyone_f.close()
