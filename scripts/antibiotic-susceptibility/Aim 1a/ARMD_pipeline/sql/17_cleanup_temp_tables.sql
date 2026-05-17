-- Drop intermediate / staging tables created during the pipeline. None of
-- these are part of the published ARMD schema; they exist only because their
-- parent step (03 ward_info, 07 prior_medications, 14 adi_scores, 16 implied
-- susceptibility) builds the final output in multiple statements.
--
-- This step is safe to re-run: every DROP is IF EXISTS.
-- If you ever need to debug one of these intermediates, comment out the
-- corresponding DROP below before re-running.

-- ---- Step 03 (ward_info) intermediates ----
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_er_icu_info_adt`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_er_info_order_proc`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_combined_er_icu_info`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_ip_op_info`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_combined_hosp_ward_info`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_cohortOfInterest`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_ordersTransfer`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.temp_icuTransferCount`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_with_icu_flag`;

-- ---- Step 07 (prior_medications) intermediate ----
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.microbiology_cultures_prior_antibiotics_extracted`;

-- ---- Step 14 (adi_scores) intermediates ----
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.cohort_adi`;
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.averaged_adi_scores`;

-- ---- Step 16 (implied_susceptibility) intermediate ----
DROP TABLE IF EXISTS `som-nero-phi-jonc101.antimicrobial_stewardship.missing_abx_records`;
