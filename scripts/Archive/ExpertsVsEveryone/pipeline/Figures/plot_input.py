# ref_file = 'Chest_Pain_reflist.csv'
# ref_file = 'GI_Bleed_reflist.csv'
ref_file = 'Pneumonia_reflist.csv'
ref = open('/Users/jwang/Desktop/Results/reference_lists/' + ref_file, "rU")

#pred_file = '41839 Chest pain.csv'
# pred_file = '41788 Gastrointestinal hemorrhage.csv'
pred_file = '42038 Pneumonia  organism unspecified.csv'
pred = open("/Users/jwang/Desktop/Results/unmatched/item_associations_everyone_unmatched/" + pred_file, "rU")

outf = open("/Users/jwang/Desktop/Results/unmatched/item_associations_everyone_unmatched/pneumonia_outcome_input.tab", "w")

num_refs = 50
ref_count = 0

ref.readline()
ref_list = {}
for ref_item in ref:
	ref_item = ref_item.strip().split(",")
	ref_list[ref_item[5]] = 1
	ref_count += 1
	if (ref_count == num_refs):
		break

outf.write("outcome\tscore\n")
pred.readline()
for pred_item in pred:
	pred_item = pred_item.strip().split(",")
	score = pred_item[2]
	outcome = 0
	if (pred_item[1] in ref_list):
		outcome = 1
	
	outf.write("{0}\t{1}\n".format(outcome,score))