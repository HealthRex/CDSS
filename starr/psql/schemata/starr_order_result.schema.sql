-- Table: starr_order_result
-- Description: Order results for procedure proc_code.
-- Original Files:
--	* Chen_Order_Result_Yr1.csv.gz
--	* Chen_Order_Result_Yr2.csv.gz
--	* Chen_Order_Result_Yr3.csv.gz
--	* Chen_Order_Result_Yr4.csv.gz
--	* Chen_Order_Result_Yr5.csv.gz
--  * Chen_Order_Res_Yr6.csv.gz
--  * Chen_Order_Res_Yr7.csv.gz
--  * Chen_Order_Res_Yr8.csv.gz
-- Clean Files:
--	* starr_order_result_year_1.csv.gz
--	* starr_order_result_year_2.csv.gz
--	* starr_order_result_year_3.csv.gz
--	* starr_order_result_year_4.csv.gz
--	* starr_order_result_year_5.csv.gz
--	* starr_order_result_year_6.csv.gz
--	* starr_order_result_year_7.csv.gz
--	* starr_order_result_year_8.csv.gz
-- CSV Fields:
--  * order_proc_id (e.g. 41330963)
--  * line (e.g. 1)
--  * ord_date_real (e.g. 61721.01)
--  * result_date (e.g. "10/14/2009 00:00")
--  * result_time (e.g. "09/24/2009 15:19")
--  * component_name (e.g. "SOURCE")
--  * base_name (e.g. "PCCOM")
--  * common_name (e.g. "GLUCOSE BY METER")
--  * ord_num_value (e.g. 1.0)
--  * reference_unit (e.g. "mg/dL")
--  * result_in_range_yn (e.g. "Y")
--  * result_status (e.g. "Final")
--  * lab_status (e.g. "Final result")
--  * value_normalized (e.g. "")

CREATE TABLE IF NOT EXISTS starr_order_result
(
  order_proc_id BIGINT NOT NULL,
  line INTEGER NOT NULL,
  ord_date_real FLOAT,
  result_date DATE,
  result_time TIMESTAMP,
  component_name TEXT,
  base_name TEXT,
  common_name TEXT,
  ord_num_value FLOAT,
  reference_unit TEXT,
  result_in_range_yn TEXT,
  result_flag TEXT,
  result_status TEXT,
  lab_status TEXT,
  value_normalized TEXT
);
