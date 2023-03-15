WITH
inpatientCBCOrdersMostRecentADT AS
(
	SELECT anon_id, pat_enc_csn_id_coded, order_proc_id_coded, order_time_jittered, max(effective_time_jittered) as effective_time_jittered
	FROM `som-nero-phi-jonc101.shc_core_2021.order_proc` as op
		join `som-nero-phi-jonc101.shc_core_2021.adt` using (anon_id, pat_enc_csn_id_coded)
	where proc_code like 'LABCBC%'
	and ordering_mode = 'Inpatient'
  and pat_service is not null
  group by anon_id, pat_enc_csn_id_coded, order_proc_id_coded, order_time_jittered
),

-- Rejoin against the last ADT event time so can figure out info about that last ADT event (particularly pat_sevice)
inpatientCBCOrdersMostRecentADTService AS
(
  select op.*, pat_service
  from inpatientCBCOrdersMostRecentADT as op
    join `som-nero-phi-jonc101.shc_core_2021.adt` using (anon_id, pat_enc_csn_id_coded, effective_time_jittered)
),

summaryInpatientCBCOrderServices AS
(
  select extract(year from order_time_jittered) as orderYear, pat_service, 
    count(distinct order_proc_id_coded) as nOrders, count(distinct pat_enc_csn_id_coded) as nEncounters, count(distinct anon_id) as nPatients,
    count(distinct order_proc_id_coded) / count(distinct pat_enc_csn_id_coded) as nOrdersPerEncounter
  from inpatientCBCOrdersMostRecentADTService
  group by orderYear, pat_service
  order by orderYear desc, nOrders desc
)

select *
from summaryInpatientCBCOrderServices
LIMIT 1000

