-- Query for sample patients that have enough distinct recommendable orders

select patient_id, count(distinct pi.clinical_item_id)
from patient_item as pi,
clinical_item as ci,
clinical_item_category as cic
where 
pi.clinical_item_id = ci.clinical_item_id
and ci.clinical_item_category_id = cic.clinical_item_category_id
and ci.default_recommend <> 0
and cic.default_recommend <> 0
group by patient_id
having count(distinct pi.clinical_item_id) > 10
limit 100;

-- Data Date Histogram
select cic.source_table, date_part('month',item_date), date_part('year',item_date), count(patient_item_id)
from 
   clinical_item_category as cic,
   clinical_item as ci,
   patient_item as pi
where
   cic.clinical_item_category_id = ci.clinical_item_category_id and
   ci.clinical_item_id = pi.clinical_item_id 
group by
   cic.source_table, date_part('month',item_date), date_part('year',item_date)
