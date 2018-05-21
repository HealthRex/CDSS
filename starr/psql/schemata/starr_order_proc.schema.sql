-- Table: starr_order_proc
-- Description: Procedure orders for procedure proc_code.
-- Original Files:
--	* Chen_Order_Proc_Yr1.patchcommas.csv.gz
--  * Chen_Order_Proc_Yr2.patchcommascsv.gz
--  * Chen_Order_Proc_Yr3.patchcommas.csv.gz
--  * Chen_Order_Proc_Yr4.patchcommas.csv.gz
--  * Chen_Order_Proc_Yr5.patchcommas.csv.gz
--  * Chen_Order_Proc_Yr6.patchcommas.csv.gz
--  * Chen_Order_Proc_Yr7.patchcommas.csv.gz
--  * Chen_Order_Proc_Yr8.patchcommas.csv.gz
-- Clean Files:
--	* starr_order_proc_year_1.csv.gz
--  * starr_order_proc_year_2.csv.gz
--  * starr_order_proc_year_3.csv.gz
--  * starr_order_proc_year_4.csv.gz
--  * starr_order_proc_year_5.csv.gz
--  * starr_order_proc_year_6.csv.gz
--  * starr_order_proc_year_7.csv.gz
--  * starr_order_proc_year_8.csv.gz
-- CSV Fields:
--  * order_proc_id (e.g. 41330963)
--  * pat_id (e.g. -9799065180730)
--  * pat_enc_csn_id (e.g. 845950)
--  * ordering_date (e.g. "12/26/2013 00:00")
--  * order_type (e.g. "Nursing")
--  * proc_id (e.g. 46821)
--  * proc_code (e.g. "IMGCTHPRW")
--  * description (e.g. "CONSULT TO NEUROLOGY")
--  * display_name (e.g. "SLP Evaluate and Treat")
--  * cpt_code (e.g. "IMGMRHWWO")
--  * proc_cat_name (e.g. "LAB BLOOD ORDERABLES")
--  * order_class (e.g. "Normal")
--  * authrzing_prov_id (e.g. 314264)
--  * abnormal_yn (e.g. "Y")
--  * lab_status (e.g. "Final result")
--  * order_status (e.g. e.g. "Cancelled")
--  * quantity (e.g. 1)
--  * future_or_stand (e.g. "S")
--  * standing_exp_date (e.g. "01/24/2014 02:00")
--  * standing_occurs (e.g. 1)
--  * stand_orig_occur (e.g. 11)
--  * radiology_status (e.g. "Preliminary")
--  * proc_bgn_time (e.g. "12/02/2009 16:30")
--  * proc_end_time (e.g. "04/18/2009 20:01")
--  * order_inst (e.g. "09/30/2009 00:17")
--  * stand_interval (e.g. "CONTINUOUS")
--  * discrete_interval (e.g. "3 Times a Week")
--  * instantiated_time (e.g. "09/15/2009 00:17")
--  * order_time (e.g. "09/30/2009 00:17")
--  * result_time (e.g. "10/06/2009 07:23")
--  * proc_start_time (e.g. "10/18/2009 00:00")
--  * problem_list_id (e.g. 1459219)
--  * proc_ending_time (e.g. "10/14/2009 00:00")
--  * chng_order_proc_id (e.g. 353403435)
--  * last_stand_perf_dt (e.g. "10/14/2009 00:00")
--  * last_stand_perf_tm (e.g. "06/01/2011 22:00")
--  * parent_ce_order_id (e.g. 381781414)
--  * ordering_mode (e.g. "Inpatient")

CREATE TABLE IF NOT EXISTS starr_order_proc
(
  order_proc_id BIGINT NOT NULL,
  pat_id TEXT,
  pat_enc_csn_id BIGINT,
  ordering_date DATE,
  order_type TEXT,
  proc_id BIGINT,
  proc_code TEXT,
  description TEXT,
  display_name TEXT,
  cpt_code TEXT,
  proc_cat_name TEXT,
  order_class TEXT,
  authrzing_prov_id TEXT,
  abnormal_yn TEXT,
  lab_status TEXT,
  order_status TEXT,
  quantity INTEGER,
  future_or_stand TEXT,
  standing_exp_date DATE,
  standing_occurs INTEGER,
  stand_orig_occur INTEGER,
  radiology_status TEXT,
  proc_bgn_time TIMESTAMP,
  proc_end_time TIMESTAMP,
  order_inst TIMESTAMP,
  stand_interval TEXT,
  discrete_interval TEXT,
  instantiated_time TIMESTAMP,
  order_time TIMESTAMP,
  result_time TIMESTAMP,
  proc_start_time TIMESTAMP,
  problem_list_id BIGINT,
  proc_ending_time TIMESTAMP,
  chng_order_proc_id BIGINT,
  last_stand_perf_dt DATE,
  last_stand_perf_tm TIMESTAMP,
  parent_ce_order_id BIGINT,
  ordering_mode TEXT
);
