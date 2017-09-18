select 
	preci.description,
	preci.item_count, 
	preci.clinical_item_category_id,
	cia.clinical_item_id, 
	cia.count_day,
	cia.subsequent_item_id,
	postci.clinical_item_category_id,
	postci.item_count, 
	postci.description,

    (cia.count_day * 1.0 * 10 / preci.item_count) as conditionalFreq,
    ( (cia.count_day * 1900.0 * 10 *10) / (preci.item_count * postci.item_count) ) as freqRatio

from 
	clinical_item as preci,
	clinical_item_association as cia,
	clinical_item as postci

where
    preci.analysis_status = 1 and
	preci.clinical_item_id = cia.clinical_item_id and
	cia.clinical_item_id <> cia.subsequent_item_id and
	cia.subsequent_item_id = postci.clinical_item_id and
	postci.analysis_status = 1 and
	postci.clinical_item_category_id in (7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,76,77,78,80,82,83,85,87,88,89,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,125,126,127,133)
	
	and (cia.count_day * 1.0 * 10 / preci.item_count) > 0.1
    and ( (cia.count_day * 1900.0 * 10 *10) / (preci.item_count * postci.item_count) ) > 1.0


order by preci.item_count desc, freqRatio desc,conditionalFreq desc

limit 250
