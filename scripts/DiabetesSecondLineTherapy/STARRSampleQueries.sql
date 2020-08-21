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


