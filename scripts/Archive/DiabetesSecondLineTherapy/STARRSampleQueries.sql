-- Identify medication order classes based on specific diabetes examples

select 
  pharm_class_abbr, pharm_class_name, thera_class_abbr, thera_class_name,
  count(distinct anon_id) as nPatients, count(distinct order_med_id_coded) nOrders
from shc_core.order_med
where
   med_description like 'METFORM%'
OR med_description like 'GLIPIZIDE%'
OR med_description like 'GLYBURIDE%'
OR med_description like 'GLIMEPIRIDE%'
OR med_description like 'REPAGLINIDE%'
OR med_description like 'NATEGLINIDE%'
OR med_description like 'ROSIGLITAZONE%'
OR med_description like 'PIOGLITAZONE%'
OR med_description like 'SITAGLIPTIN%'
OR med_description like 'SAXAGLIPTIN%'
OR med_description like 'LINAGLIPTIN%'
OR med_description like 'EXENATIDE%'
OR med_description like 'LIRAGLUTIDE%'
OR med_description like 'SEMAGLUTIDE%'
OR med_description like 'CANAGLIFLOZIN%'
OR med_description like 'DAPAGLIFLOZIN%'
OR med_description like 'EMPAGLIFLOZIN'
OR med_description like 'INSULIN%'
GROUP BY
  pharm_class_abbr, pharm_class_name, thera_class_abbr, thera_class_name
ORDER BY 
  nPatients desc







-- Look for all outpatient prescription fills from one of the primary diabetes medication categories
-- Broken up by year
select 
  EXTRACT(YEAR from order_inst) as orderYear,
  pharm_class_abbr, pharm_class_name, thera_class_abbr, thera_class_name,
  count(distinct anon_id) as nPatients, count(distinct order_med_id_coded) nOrders
from shc_core.order_med
where thera_class_abbr = 'ANT71' -- Anti-Hyperglycemics
GROUP BY
  orderYear,
  pharm_class_abbr, pharm_class_name, thera_class_abbr, thera_class_name
ORDER BY 
  orderYear desc,
  nPatients desc




-- Patient Demographics for those who ever took some Diabetes medications
-- Find demographic info on patients who received at least one diabetes drug prescription and their age at the first date it happened
WITH
dmRxPatients AS
(
	SELECT 
	  d.anon_id, d.gender, d.canonical_race, d.canonical_ethnicity, 
	  min(om.order_inst) as first_order_inst,
	  EXTRACT(YEAR from min(om.order_inst)) - EXTRACT(YEAR from d.birth_date_jittered) as age_at_first_order

	FROM `shc_core.demographic` as d
	   INNER JOIN `shc_core.order_med` as om USING (anon_id)
	WHERE
	   om.thera_class_abbr = 'ANT71'
	GROUP BY
	  d.anon_id, d.gender, d.canonical_race, d.canonical_ethnicity, d.birth_date_jittered
)

-- By Gender
select gender, count(distinct anon_id) as nPatients
from dmRxPatients
group by gender
order by nPatients desc



-- By Race/Ethnicity
select canonical_race, canonical_ethnicity, count(distinct anon_id) as nPatients
from dmRxPatients
group by canonical_race, canonical_ethnicity
order by nPatients desc



-- By Age of First Prescription/Order
select CAST(FLOOR(age_at_first_order/10)*10 AS INT64) AS decade_at_first_order, count(distinct anon_id) as nPatients
from dmRxPatients
group by decade_at_first_order
order by decade_at_first_order desc













WITH
dmRx AS
( -- Find all prescriptions for diabetes related drugs
  select 
    anon_id, order_med_id_coded,
    order_inst, EXTRACT(YEAR from order_inst) as orderYear,
    pharm_class_abbr, pharm_class_name, thera_class_abbr, thera_class_name
  from shc_core.order_med
  where thera_class_abbr = 'ANT71' -- Anti-Hyperglycemics
),
maceDxSample AS
(
  -- Pull out diagnoses where matches one of the ICD10 codes for select Major Adverse Cardiovascular Events
  -- Doesn't capture all of them however, as the full list appears to include other procedure codes and this is only for ICD10 
  -- (whereas the database appears to have ICD9 codes prior to ~2015)
  -- https://www.ahajournals.org/doi/pdf/10.1161/JAHA.119.014402
  SELECT anon_id, icd9, icd10, start_date, EXTRACT(YEAR FROM start_date) AS dx_year
  FROM `shc_core.diagnosis_code` 
  WHERE
  (
    -- Myocardial Infarction
    icd10 LIKE 'I21%' OR
    icd10 LIKE 'I21.0%' OR
    icd10 LIKE 'I21.01%' OR
    icd10 LIKE 'I21.02%' OR
    icd10 LIKE 'I21.09%' OR
    icd10 LIKE 'I21.1%' OR
    icd10 LIKE 'I21.11%' OR
    icd10 LIKE 'I21.19%' OR
    icd10 LIKE 'I21.2%' OR
    icd10 LIKE 'I21.21%' OR
    icd10 LIKE 'I21.29%' OR
    icd10 LIKE 'I21.3%' OR
    icd10 LIKE 'I21.4%' OR
    icd10 LIKE 'I22%' OR
    icd10 LIKE 'I22.0%' OR
    icd10 LIKE 'I22.1%' OR
    icd10 LIKE 'I22.2%' OR
    icd10 LIKE 'I22.8%' OR
    icd10 LIKE 'I22.9%' OR
    icd10 LIKE 'I23%' OR
    icd10 LIKE 'I23.0%' OR
    icd10 LIKE 'I23.1%' OR
    icd10 LIKE 'I23.2%' OR
    icd10 LIKE 'I23.3%' OR
    icd10 LIKE 'I23.4%' OR
    icd10 LIKE 'I23.5%' OR
    icd10 LIKE 'I23.6%' OR
    icd10 LIKE 'I23.7%' OR
    icd10 LIKE 'I23.8%' OR
    icd10 LIKE 'I25.2%' OR

    -- Ischemic stroke 
    icd10 LIKE 'I63%' OR

    -- Heart failure
    icd10 LIKE 'I09.9%' OR
    icd10 LIKE 'I11.0%' OR
    icd10 LIKE 'I13.0%' OR
    icd10 LIKE 'I13.2%' OR
    icd10 LIKE 'I25.5%' OR
    icd10 LIKE 'I42.0%' OR
    icd10 LIKE 'I42.5%' OR
    icd10 LIKE 'I42.6%' OR
    icd10 LIKE 'I42.7%' OR
    icd10 LIKE 'I42.8%' OR
    icd10 LIKE 'I42.9%' OR
    icd10 LIKE 'I43%' OR
    icd10 LIKE 'I50%' OR
    icd10 LIKE 'P29.0%' OR

    -- Acute coronary syndrome
    icd10 LIKE 'I20.0%' OR
    icd10 LIKE 'I21.09%' OR
    icd10 LIKE 'I21.11%' OR
    icd10 LIKE 'I21.19%' OR
    icd10 LIKE 'I21.29%' OR
    icd10 LIKE 'I21.3%' OR
    icd10 LIKE 'I21.4%' OR
    icd10 LIKE 'I24.0%' 
  )
),

dmRxMACESamplePatients AS
(
  -- Find demographic info on patients who received at least one diabetes drug prescription 
  -- and a cardiovascular event sample diagnosis anytime after

  SELECT 
    d.anon_id, d.gender, d.canonical_race, d.canonical_ethnicity, 
    min(order_inst) as first_dmRx_datetime, EXTRACT(YEAR FROM min(order_inst)) - EXTRACT(YEAR FROM birth_date_jittered) AS age_at_first_dmRx,
    min(start_date) as first_maceSampleDx_datetime, EXTRACT(YEAR FROM min(start_date)) - EXTRACT(YEAR FROM birth_date_jittered) as age_at_first_maceDxSample

  FROM 
      shc_core.demographic as d
      INNER JOIN dmRx USING (anon_id)
      INNER JOIN maceDxSample USING (anon_id)
  WHERE
     dmRx.order_inst < maceDxSample.start_date  -- Only capture when MACE diagnosis event occurs after medication order
  GROUP BY
    d.anon_id, d.gender, d.canonical_race, d.canonical_ethnicity, d.birth_date_jittered
)

SELECT 
  EXTRACT(YEAR FROM first_maceSampleDx_datetime) as FIRST_MACE_SAMPLE_DX_YEAR,
  -- CAST(FLOOR(AGE_AT_FIRST_MACE_SAMPLE_DX/10)*10 AS INT64) AS DECADE_AT_FIRST_MACE_SAMPLE_DX,
  COUNT(DISTINCT anon_id) as nPatients,
FROM dmRxMACESamplePatients
GROUP BY 
  FIRST_MACE_SAMPLE_DX_YEAR
ORDER BY
  FIRST_MACE_SAMPLE_DX_YEAR desc














