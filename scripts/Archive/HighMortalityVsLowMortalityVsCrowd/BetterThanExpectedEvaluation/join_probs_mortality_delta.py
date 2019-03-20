inf_mortality = open("mortality_days_after_last_admission.csv", "rU")
inf_mortality.readline()
inf_probs = open("mortality_probs_remapped_2010_2013.csv", "rU")
inf_probs.readline()

outf = open("joined_probs_mortality_delta_spreadsheet.csv", "w")
outf.write("pat_id,30_day_mortality_prob,delta\n")

pat_mortality_map = {}
pat_prob_map = {}

for line in inf_mortality:
	line = line.strip().split(",")
	pat_mortality_map[line[0]] = line[3] # pat_id: mortality_delta
inf_mortality.close()

for line in inf_probs:
	line = line.strip().split(",")
	pat_prob_map[line[0]] = line[1] # pat_id: 30_day_mortality_prob
inf_probs.close()

for pat_id, prob in pat_prob_map.iteritems():
	delta = "N/A"
	if (pat_id in pat_mortality_map):
		delta = pat_mortality_map[pat_id]
	# if (delta == "N/A"):
	# 	continue
	outf.write("{0},{1},{2}\n".format(pat_id,prob,delta))

outf.close()