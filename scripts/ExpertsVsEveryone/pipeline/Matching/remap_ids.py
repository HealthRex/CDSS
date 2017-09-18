# create normalized id to original id mapping
id_map = {}
expert_map = open("expert_2013only.csv", "rU")
everyone_map = open("everyone_2013only.csv", "rU")

expert_map.readline()
for line in expert_map:
	line = line.strip().split(",")
	id_map[line[0]] = line[1]

everyone_map.readline()
for line in everyone_map:
	line = line.strip().split(",")
	id_map[line[0]] = line[1]

expert_out = open("/Users/jwang/Desktop/Results/matched/expert_list.csv", "w")
everyone_out = open("/Users/jwang/Desktop/Results/matched/everyone_list.csv", "w")
matched = open("matched.csv", "rU")

matched.readline()
for line in matched:
	line = line.strip().split(",")
	normalized_id = line[1]
	original_id = id_map[normalized_id]
	if (int(normalized_id) > 0): #expert
		expert_out.write("{0}\n".format(original_id))
	else: # everyone
		everyone_out.write("{0}\n".format(original_id))



