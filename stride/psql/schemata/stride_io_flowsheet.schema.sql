-- Table: stride_io_flowsheet
-- Description: Flow sheet of intake (feeding) and output (urine/bowel mvmt).
-- Original Files:
--            2008 – 2014
--  * Jchen_Inpu_output_data1.csv.gz
--  * Jchen_Inpu_output_data2.csv.gz
--  * Jchen_Inpu_output_data3.csv.gz
--  * Jchen_Inpu_output_data4.csv.gz
--  * Jchen_Inpu_output_data5.csv.gz
--            2014 – 2017
--  * Jchen_Inpu_output_update_11.csv.gz
--  * Jchen_Inpu_output_update_12.csv.gz
--  * Jchen_Inpu_output_update_13.csv.gz
--  * Jchen_Inpu_output_update_14.csv.gz
--  * Jchen_Inpu_output_update_15.csv.gz
--  * Jchen_Inpu_output_update_16.csv.gz
--  * Jchen_Inpu_output_update_17.csv.gz
--  * Jchen_Inpu_output_update_18.csv.gz
--  * Jchen_Inpu_output_update_19.csv.gz
--  * Jchen_Inpu_output_update_20.csv.gz
-- Clean Files:
--          2008 – 2014
--  * stride_io_flowsheet_1.csv.gz
--  * stride_io_flowsheet_2.csv.gz
--  * stride_io_flowsheet_3.csv.gz
--  * stride_io_flowsheet_4.csv.gz
--  * stride_io_flowsheet_5.csv.gz
--          2014 – 2017
--  * stride_io_flowsheet_11.csv.gz
--  * stride_io_flowsheet_12.csv.gz
--  * stride_io_flowsheet_13.csv.gz
--  * stride_io_flowsheet_14.csv.gz
--  * stride_io_flowsheet_15.csv.gz
--  * stride_io_flowsheet_16.csv.gz
--  * stride_io_flowsheet_17.csv.gz
--  * stride_io_flowsheet_18.csv.gz
--  * stride_io_flowsheet_19.csv.gz
--  * stride_io_flowsheet_20.csv.gz
-- CSV Fields:
--  * PAT_ANON_ID (e.g. 8788729772386)
--  * PAT_ENC_CSN_ANON_ID (e.g. 377427)
--  * FLO_MEAS_ID (e.g. 30404896)
--  * G1_DISP_NAME (e.g. "Nutritional Intake")
--  * G2_DISP_NAME (e.g. "Urine Output")
--  * SHIFTED_TRANSF_IN_DT_TM (e.g. 02-NOV-13 20:00)
--  * MEAS_VALUE (e.g. "Reg")
--  * RN (e.g. 10205663)

CREATE TABLE IF NOT EXISTS stride_io_flowsheet
(
  pat_anon_id BIGINT,
	pat_enc_csn_anon_id BIGINT,
	flo_meas_id BIGINT,
	g1_disp_name TEXT,
	g2_disp_name TEXT,
	shifted_transf_in_dt_tm TIMESTAMP,
	meas_value TEXT,
	rn BIGINT
);
