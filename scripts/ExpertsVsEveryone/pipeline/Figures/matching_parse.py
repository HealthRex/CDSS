f = open("matching_compare.csv", "rU")
o = open("matching_table.csv", "w")

for i in range(4):
	f.readline()

o.write("Covariate Name, Expert Mean, Everyone Mean, P-Value, Expert Mean, Everyone Mean, P-Value\n")
for feature_id in range(35):
	line = f.readline()
	line = line.strip().split(",")[0]
	line = line.strip()
	name = line[5:len(line)-3]

	line = f.readline()
	line = line.strip().split(",")
	expert_unmatched = line[0][4:]
	expert_matched = line[1][4:]

	line = f.readline()
	line = line.strip().split(",")
	everyone_unmatched = line[0][4:]
	everyone_matched = line[1][4:]

	line = f.readline()
	line = line.strip().split(",")
	pvalue_unmatched = line[0][4:]
	pvalue_matched = line[1][4:]

	f.readline()
	o.write("{0},{1},{2},{3},{4},{5},{6}\n".format(name,expert_unmatched,everyone_unmatched,pvalue_unmatched,expert_matched,everyone_matched,pvalue_matched))



