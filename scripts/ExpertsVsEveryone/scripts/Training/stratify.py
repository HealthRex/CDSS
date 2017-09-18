f = open("matched/expert_list.csv", "rU")

limit = 600
o_num = 1
o = open("matched/expert_list_matched/" + str(o_num), "w")

count = 0
for line in f:
	o.write(line)

	count += 1
	if (count == limit):
		count = 0
		o_num += 1
		o = open("matched/expert_list_matched/" + str(o_num), "w")
