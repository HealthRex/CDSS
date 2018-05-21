-- Table: starr_order_med
-- Description: Medication orders for medication_id.
-- Original Files:
--	* Chen_Order_Med_5Yr.csv.gz
--  * Chen_Order_Med_Yrs6_8.patchHeader.csv.gz
-- Clean Files:
--	* starr_order_med_2008_2014.csv.gz
--  * starr_order_med_2014_2017.patchHeader.csv.gz
-- CSV Fields:
--  * order_med_id (e.g. 6757747)
--  * pat_id (e.g. 10000892290139)
--  * pat_enc_csn_id (e.g. 831773)
--  * ordering_date (e.g. "01/19/2014 20:28")
--  * order_class_c (e.g. 60)
--  * order_class_name (e.g. "E-Prescribe")
--  * medication_id (e.g. 8981)
--  * description (e.g. "HYDROMORPHONE 1 MG/ML IV PCA")
--  * quantity (e.g. "10 Syringe")
--  * refills (e.g. "2")
--  * start_taking_time (e.g. "02/23/2014 22:00")
--  * order_end_time (e.g. "08/27/2014 13:38")
--  * end_taking_time (e.g. "03/19/2014 21:25")
--  * rsn_for_discon_c (e.g. 18)
--  * rsn_for_discon (e.g. "Patient Discharge")
--  * med_presc_prov_id (unique identifier for prescriber, e.g. 314264)
--  * display_name (e.g. "oxyCODONE (ROXICODONE) tablet 5 mg")
--  * order_priority_c (e.g. 2)
--  * order_priority (e.g. "STAT")
--  * med_route_c (e.g. 15)
--  * med_route (e.g. "Oral")
--  * discon_time (e.g. "03/27/2014 15:29")
--  * chng_order_med_id (e.g. 445699906)
--  * hv_discr_freq_id (id for medication frequency category, e.g. "200006")
--  * freq_name (corresponds to hv_discr_freq_id, e.g. "2 TIMES DAILY" for "200006")
--  * discrete_frequency (corresponds to hv_discr_freq_id, e.g. "Q6H PRN" for "200526")
--  * hv_discrete_dose (e.g. "3100")
--  * hv_dose_unit_c (e.g. 3)
--  * hv_dose_unit (corresponds to hv_dose_unit_c, e.g. "mg" for 3)
--  * order_status_c (e.g. 5)
--  * order_status (e.g. "Discontinued")
--  * authrzing_prov_id (e.g. 345324)
--  * ord_prov_id (e.g. 403311)
--  * min_discrete_dose (e.g. 25)
--  * max_discrete_dose (e.g. 12)
--  * dose_unit_c (e.g. 8)
--  * dose_unit (e.g. "mg")
--  * pat_loc_id (e.g. 2000232)
--  * department_name (e.g. "D3")
--  * modify_track_c (e.g. 2)
--  * modify_track (e.g. "MODIFIED")
--  * act_order_c (e.g. 3)
--  * active_order (e.g. "Discontinued Medication")
--  * lastdose (e.g. "Pt Unsure")
--  * amb_med_disp_name (e.g. "acetaminophen (TYLENOL) 325 mg tablet")
--  * refills_remaining (e.g. 3)
--  * resume_status_c (e.g. 2)
--  * resume_status (e.g. "Sent")
--  * ordering_mode_c (e.g. 2)
--  * ordering_mode (e.g. "Inpatient")
--  * med_dis_disp_qty (e.g. 90)
--  * med_dis_disp_unit_c (e.g. 5003)
--  * dispense_unit (e.g. "Packet")
--  * number_of_doses (e.g. 2)
--  * doses_remaining (e.g. 1)
--  * min_rate (e.g. 100)
--  * max_rate (e.g. 200)
--  * rate_unit_c (e.g. 41)
--  * rate_unit (e.g. "mL/hr")
--  * min_duration (e.g. 60)
--  * max_duration (e.g. 120)
--  * med_duration_unit_c (e.g. 2)
--  * duration_unit_name (e.g. "Hours")
--  * min_volume (e.g. 50)
--  * max_volume (e.g. "")
--  * volume_unit_c (e.g. 1)
--  * volume_unit (e.g. "mL")
--  * calc_volume_yn (e.g. "Y")
--  * calc_min_dose (e.g. 5)
--  * calc_max_dose (e.g. 10)
--  * calc_dose_unit_c (e.g. 7)
--  * calc_dose_unit (e.g. "g")
--  * admin_min_dose (e.g. 5)
--  * admin_max_dose (e.g. 50)
--  * admin_dose_unit_c (e.g. 5025)
--  * admin_dose_unit (e.g. "Units")

CREATE TABLE IF NOT EXISTS starr_order_med
(
	order_med_id BIGINT NOT NULL,
	pat_id TEXT,
	pat_enc_csn_id BIGINT,
	ordering_date TIMESTAMP,
	order_class_c INTEGER,
	order_class_name TEXT,
	medication_id INTEGER,
	description TEXT,
	quantity TEXT,
	refills TEXT,
	start_taking_time TIMESTAMP,
	order_end_time TIMESTAMP,
	end_taking_time TIMESTAMP,
	rsn_for_discon_c INTEGER,
	rsn_for_discon TEXT,
	med_presc_prov_id INTEGER,
	display_name TEXT,
	order_priority_c INTEGER,
	order_priority TEXT,
	med_route_c INTEGER,
	med_route TEXT,
	discon_time TIMESTAMP,
	chng_order_med_id BIGINT,
	hv_discr_freq_id INTEGER,
	freq_name TEXT,
	discrete_frequency TEXT,
	hv_discrete_dose TEXT,
	hv_dose_unit_c INTEGER,
	hv_dose_unit TEXT,
	order_status_c INTEGER,
	order_status TEXT,
	authrzing_prov_id INTEGER,
	ord_prov_id INTEGER,
	min_discrete_dose FLOAT,
	max_discrete_dose FLOAT,
	dose_unit_c INTEGER,
	dose_unit TEXT,
	pat_loc_id INTEGER,
	department_name TEXT,
	modify_track_c INTEGER,
	modify_track TEXT,
	act_order_c INTEGER,
	active_order TEXT,
	lastdose TEXT,
	amb_med_disp_name TEXT,
	refills_remaining INTEGER,
	resume_status_c INTEGER,
	resume_status TEXT,
	ordering_mode_c INTEGER,
	ordering_mode TEXT,
	med_dis_disp_qty FLOAT,
	med_dis_disp_unit_c INTEGER,
	dispense_unit TEXT,
	number_of_doses INTEGER,
	doses_remaining INTEGER,
	min_rate FLOAT,
	max_rate FLOAT,
	rate_unit_c INTEGER,
	rate_unit TEXT,
	min_duration FLOAT,
	max_duration FLOAT,
	med_duration_unit_c INTEGER,
	duration_unit_name TEXT,
	min_volume FLOAT,
	max_volume FLOAT,
	volume_unit_c INTEGER,
	volume_unit TEXT,
	calc_volume_yn TEXT,
	calc_min_dose FLOAT,
	calc_max_dose FLOAT,
	calc_dose_unit_c INTEGER,
	calc_dose_unit TEXT,
	admin_min_dose FLOAT,
	admin_max_dose FLOAT,
	admin_dose_unit_c INTEGER,
	admin_dose_unit TEXT
  );
