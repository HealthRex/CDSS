-- Create extra clinical item records needed for certain simulation cases

-- Direct Current Cardioversion for Afib example. No specific clinical_item/order represents the thing
-- Category 12 = Procedures
insert into clinical_item(clinical_item_id, clinical_item_category_id, external_id, name, description, default_recommend, analysis_status, unique_count, item_count, patient_count, encounter_count)
  values (-100, 12, null, 'DCCV', 'Direct Current Cardioversion', 1, 1, 200, 200, 200, 200);

insert into clinical_item_association(clinical_item_association_id, clinical_item_id, subsequent_item_id,
	count_0, count_3600, count_7200, count_21600, count_43200, count_86400, count_172800, count_345600, count_604800, count_1209600, count_2592000, count_7776000, count_15552000, count_31536000, count_63072000, count_126144000, count_any, time_diff_sum, time_diff_sum_squares,
	unique_count_0, unique_count_3600, unique_count_7200, unique_count_21600, unique_count_43200, unique_count_86400, unique_count_172800, unique_count_345600, unique_count_604800, unique_count_1209600, unique_count_2592000, unique_count_7776000, unique_count_15552000, unique_count_31536000, unique_count_63072000, unique_count_126144000, unique_count_any, unique_time_diff_sum, unique_time_diff_sum_squares,
	patient_count_0, patient_count_3600, patient_count_7200, patient_count_21600, patient_count_43200, patient_count_86400, patient_count_172800, patient_count_345600, patient_count_604800, patient_count_1209600, patient_count_2592000, patient_count_7776000, patient_count_15552000, patient_count_31536000, patient_count_63072000, patient_count_126144000, patient_count_any, patient_time_diff_sum, patient_time_diff_sum_squares,
	encounter_count_0, encounter_count_3600, encounter_count_7200, encounter_count_21600, encounter_count_43200, encounter_count_86400, encounter_count_172800, encounter_count_345600, encounter_count_604800, encounter_count_1209600, encounter_count_2592000, encounter_count_7776000, encounter_count_15552000, encounter_count_31536000, encounter_count_63072000, encounter_count_126144000, encounter_count_any, encounter_time_diff_sum, encounter_time_diff_sum_squares
	)
	values
	(	-150, -100, -100,
		200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 0.0, 0.0,
		200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 0.0, 0.0,
		200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 0.0, 0.0,
		200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 0.0, 0.0
	);

-- Associate with admit diagnosis "cardiac dysrhythmia ICD9 = 427" corresponds to clinical_item_id = 41870
insert into clinical_item_association(clinical_item_association_id, clinical_item_id, subsequent_item_id,
	count_0, count_3600, count_7200, count_21600, count_43200, count_86400, count_172800, count_345600, count_604800, count_1209600, count_2592000, count_7776000, count_15552000, count_31536000, count_63072000, count_126144000, count_any, time_diff_sum, time_diff_sum_squares,
	unique_count_0, unique_count_3600, unique_count_7200, unique_count_21600, unique_count_43200, unique_count_86400, unique_count_172800, unique_count_345600, unique_count_604800, unique_count_1209600, unique_count_2592000, unique_count_7776000, unique_count_15552000, unique_count_31536000, unique_count_63072000, unique_count_126144000, unique_count_any, unique_time_diff_sum, unique_time_diff_sum_squares,
	patient_count_0, patient_count_3600, patient_count_7200, patient_count_21600, patient_count_43200, patient_count_86400, patient_count_172800, patient_count_345600, patient_count_604800, patient_count_1209600, patient_count_2592000, patient_count_7776000, patient_count_15552000, patient_count_31536000, patient_count_63072000, patient_count_126144000, patient_count_any, patient_time_diff_sum, patient_time_diff_sum_squares,
	encounter_count_0, encounter_count_3600, encounter_count_7200, encounter_count_21600, encounter_count_43200, encounter_count_86400, encounter_count_172800, encounter_count_345600, encounter_count_604800, encounter_count_1209600, encounter_count_2592000, encounter_count_7776000, encounter_count_15552000, encounter_count_31536000, encounter_count_63072000, encounter_count_126144000, encounter_count_any, encounter_time_diff_sum, encounter_time_diff_sum_squares
	)
	values
	(	-160, 41870, -100,
		0, 0, 0, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 50000.0, 100000.0,
		0, 0, 0, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 50000.0, 100000.0,
		0, 0, 0, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 50000.0, 100000.0,
		0, 0, 0, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 50000.0, 100000.0
	);

-- Add cardioversion procedure to 1564	IP ATP CARDIOVERSION order set
insert into item_collection(item_collection_id, section, name, external_id, subgroup)
  values (-100, 'Procedure', 'IP ATP CARDIOVERSION', 1564, 'Orders');

insert into item_collection_item(item_collection_item_id, item_collection_id, clinical_item_id)
  values (-100, -100, -100);


-- Add specific abbreviations to certain clinical items
-- Add 'Ultrasound' prefix to all items starting with US
update clinical_item set description = CONCAT('Ultrasound - ', description) where description like 'US %';
-- Add 'DCCV' prevfix to direct current cardioversion item
update clinical_item set description = 'DCCV - Direct Current Cardioversion' where clinical_item_id = -100;
-- Add '(TTE)' suffix to ECHO - TRANSTHORACIC ECHO +DOPPLER item
update clinical_item set description = 'ECHO - TRANSTHORACIC ECHO +DOPPLER (TTE)' where clinical_item_id = 61832;
