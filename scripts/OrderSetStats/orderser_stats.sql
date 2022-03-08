-- For proc_orderset

WITH 
proc_orderset_usage AS
(
    SELECT 
        EXTRACT(YEAR FROM op.ordering_date_jittered) as orderYear, pos.protocol_id, pos.protocol_name, 
        count(distinct pos.anon_id) as nPatientsPerOrderSet, count(distinct pos.pat_enc_csn_id_coded) as nEncountersPerOrderSet
    FROM `som-nero-phi-jonc101.shc_core_2021.proc_orderset` as pos
       INNER JOIN `som-nero-phi-jonc101.shc_core_2021.order_proc` as op USING (order_proc_id_coded)
    WHERE ss_section_name <> 'Ad-hoc Orders'  -- These are not a part of the order set. Could be random orders that users add on after the fact
    group by orderYear, pos.protocol_id, pos.protocol_name
),

proc_orderset_individual_order_usage AS
(
    SELECT 
        EXTRACT(YEAR FROM op.ordering_date_jittered) as orderYear, pos.protocol_id, pos.protocol_name, 
        op.order_type, op.proc_code, op.display_name, 
        count(distinct op.anon_id) as nPatients, count(distinct op.pat_enc_csn_id_coded) as nEncounters, count(distinct op.order_proc_id_coded) as nOrders
    FROM `som-nero-phi-jonc101.shc_core_2021.proc_orderset` as pos
       INNER JOIN `som-nero-phi-jonc101.shc_core_2021.order_proc` as op USING (order_proc_id_coded)
    WHERE ss_section_name <> 'Ad-hoc Orders'  
    group by orderYear, pos.protocol_id, pos.protocol_name, op.order_type, op.proc_code, op.display_name
)
 

 select *
 from proc_orderset_usage as pou
 INNER JOIN proc_orderset_individual_order_usage as poiou USING (orderYear, protocol_id, protocol_name)
 WHERE nPatients > 10 -- Ignore rare items to avoid exposing PHI
 and orderYear > 2018 -- Avoid excessive old results
 order by orderYear desc, nEncountersPerOrderSet desc, protocol_name, nOrders desc


 -- Similarly for med_orderset
 WITH 

med_orderset_usage AS

(
    SELECT 

        EXTRACT(YEAR FROM om.order_time_jittered) as orderYear, mos.protocol_id, mos.protocol_name, 
        count(distinct mos.anon_id) as nPatientsPerOrderSet, count(distinct mos.pat_enc_csn_id_coded) as nEncountersPerOrderSet
    FROM `som-nero-phi-jonc101.shc_core_2021.med_orderset` as mos
       INNER JOIN `som-nero-phi-jonc101.shc_core_2021.order_med` as om USING (order_med_id_coded)
    WHERE ss_section_name <> 'Ad-hoc Orders'  -- These are not a part of the order set. Could be random orders that users add on after the fact
    group by orderYear, mos.protocol_id, mos.protocol_name
),

med_orderset_individual_order_usage AS
(
    SELECT 
        EXTRACT(YEAR FROM om.order_time_jittered) as orderYear, mos.protocol_id, mos.protocol_name, 
        om.pharm_class_abbr, om.pharm_class_name, 
        count(distinct om.anon_id) as nPatients, count(distinct om.pat_enc_csn_id_coded) as nEncounters, count(distinct om.order_med_id_coded) as nOrders
    FROM `som-nero-phi-jonc101.shc_core_2021.med_orderset` as mos
       INNER JOIN `som-nero-phi-jonc101.shc_core_2021.order_med` as om USING (order_med_id_coded)
    WHERE ss_section_name <> 'Ad-hoc Orders'  
    group by orderYear, mos.protocol_id, mos.protocol_name, om.pharm_class_abbr, om.pharm_class_name
)

 
 select *
 from med_orderset_usage as pou
 INNER JOIN med_orderset_individual_order_usage as poiou USING (orderYear, protocol_id, protocol_name)
 WHERE nPatients > 10 -- Ignore rare items to avoid exposing PHI
 and orderYear > 2018 -- Avoid excessive old results
 order by orderYear desc, nEncountersPerOrderSet desc, protocol_name, nOrders desc