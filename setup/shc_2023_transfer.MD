```
-- adt table
create table som-nero-phi-jonc101.shc_core_2023.adt as

select * except(effective_time_jittered, event_time_jittered),
    effective_time_jittered,
    timestamp(effective_time_jittered, "America/Los_Angeles") as effective_time_jittered_utc,
    event_time_jittered,
    timestamp(event_time_jittered, "America/Los_Angeles") as event_time_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.adt;



-- alert
create table som-nero-phi-jonc101.shc_core_2023.alert as

select * except(update_date_jittered),
    update_date_jittered,
    timestamp(update_date_jittered, "America/Los_Angeles") as update_date_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.alert;


-- alert_history
create table som-nero-phi-jonc101.shc_core_2023.alert_history as

select * except(update_date_jittered, alt_action_inst, contact_date),
    update_date_jittered,
    alt_action_inst,
    extract(date from contact_date) as contact_date,
    timestamp(update_date_jittered, "America/Los_Angeles") as update_date_jittered_utc,
    timestamp(alt_action_inst, "America/Los_Angeles") as alt_action_inst_utc,
    from som-nero-phi-jonc101.shc_core_2022.alert_history;


-- alerts_orders
create table som-nero-phi-jonc101.shc_core_2023.alerts_orders as

select * except(update_date_jittered),
    update_date_jittered,
    timestamp(update_date_jittered, "America/Los_Angeles") as update_date_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.alerts_orders;


-- allergy
create table som-nero-phi-jonc101.shc_core_2023.allergy as

select * except(date_noted_jittered),
    extract(date from date_noted_jittered) as date_noted_jittered,
    from som-nero-phi-jonc101.shc_core_2022.allergy;

-- alt_com_action
create table som-nero-phi-jonc101.shc_core_2023.alt_com_action as

select * except(contact_date_jittered),
    extract(date from contact_date_jittered) as contact_date_jittered,
    from som-nero-phi-jonc101.shc_core_2022.alt_com_action;

-- clinical_doc_meta
create table som-nero-phi-jonc101.shc_core_2023.clinical_doc_meta as

select * except(filing_date_jittered, note_date_jittered, activity_date_jittered, effective_time_jittered),
    filing_date_jittered,
    note_date_jittered,
    activity_date_jittered,
    effective_time_jittered,
    timestamp(filing_date_jittered, "America/Los_Angeles") as filing_date_jittered_utc,
    timestamp(note_date_jittered, "America/Los_Angeles") as note_date_jittered_utc,
    timestamp(activity_date_jittered, "America/Los_Angeles") as activity_date_jittered_utc,
    timestamp(effective_time_jittered, "America/Los_Angeles") as effective_time_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.clinical_doc_meta;

-- culture_sensitivity
create table som-nero-phi-jonc101.shc_core_2023.culture_sensitivity as

select * except(order_time_jittered, result_time_jittered, sens_obs_inst_tm_jittered, sens_anl_inst_tm_jittered),
    order_time_jittered,
    result_time_jittered,
    sens_obs_inst_tm_jittered,
    sens_anl_inst_tm_jittered,
    timestamp(order_time_jittered, "America/Los_Angeles") as order_time_jittered_utc,
    timestamp(result_time_jittered, "America/Los_Angeles") as result_time_jittered_utc,
    timestamp(sens_obs_inst_tm_jittered, "America/Los_Angeles") as sens_obs_inst_tm_jittered_utc,
    timestamp(sens_anl_inst_tm_jittered, "America/Los_Angeles") as sens_anl_inst_tm_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.culture_sensitivity;


-- demographic
create table som-nero-phi-jonc101.shc_core_2023.demographic as

select * except(birth_date_jittered, death_date_jittered),
    extract(date from birth_date_jittered) as birth_date_jittered,
    extract(date from death_date_jittered) as death_date_jittered,
    from som-nero-phi-jonc101.shc_core_2022.demographic;


-- diagnosis
create table som-nero-phi-jonc101.shc_core_2023.diagnosis as

select * except(end_date_jittered, start_date_jittered, noted_date_jittered, hx_date_of_entry_jittered, resolved_date_jittered),
    end_date_jittered,
    start_date_jittered,
    extract(date from noted_date_jittered) as noted_date_jittered,
    extract(date from hx_date_of_entry_jittered) as hx_date_of_entry_jittered,
    extract(date from resolved_date_jittered) as resolved_date_jittered,
    timestamp(end_date_jittered, "America/Los_Angeles") as end_date_jittered_utc,
    timestamp(start_date_jittered, "America/Los_Angeles") as start_date_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.diagnosis;

-- encounter
create table som-nero-phi-jonc101.shc_core_2023.encounter as

select * except(adt_arrival_time_jittered, hosp_admsn_time_jittered, appt_time_jittered, appt_when_jittered, hosp_disch_time_jittered, contact_date_jittered),
    extract(date from contact_date_jittered) as contact_date_jittered,
    adt_arrival_time_jittered,
    hosp_admsn_time_jittered,
    appt_time_jittered,
    appt_when_jittered,
    hosp_disch_time_jittered,
    timestamp(adt_arrival_time_jittered, "America/Los_Angeles") as adt_arrival_time_jittered_utc,
    timestamp(hosp_admsn_time_jittered, "America/Los_Angeles") as hosp_admsn_time_jittered_utc,
    timestamp(appt_time_jittered, "America/Los_Angeles") as appt_time_jittered_utc,
    timestamp(appt_when_jittered, "America/Los_Angeles") as appt_when_jittered_utc,
    timestamp(hosp_disch_time_jittered, "America/Los_Angeles") as hosp_disch_time_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.encounter;


-- f_ip_hsp_admission
create table som-nero-phi-jonc101.shc_core_2023.f_ip_hsp_admission as

select * except(hosp_adm_date_jittered, hosp_disch_date_jittered),
    extract(date from hosp_adm_date_jittered) as hosp_adm_date_jittered,
    extract(date from hosp_disch_date_jittered) as hosp_disch_date_jittered,
    from som-nero-phi-jonc101.shc_core_2022.f_ip_hsp_admission;


-- family_hx
create table som-nero-phi-jonc101.shc_core_2023.family_hx as

select * except(contact_date_jittered),
     contact_date_jittered,
    from som-nero-phi-jonc101.shc_core_2022.family_hx;


-- flowsheet
create table som-nero-phi-jonc101.shc_core_2023.flowsheet as

select * except(recorded_time_jittered),
    recorded_time_jittered,
    timestamp(recorded_time_jittered, "America/Los_Angeles") as recorded_time_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.flowsheet;



-- lab_result
create table som-nero-phi-jonc101.shc_core_2023.lab_result as

select * except(order_time_jittered, taken_time_jittered, result_time_jittered),
    order_time_jittered,
    taken_time_jittered,
    result_time_jittered,
    timestamp(order_time_jittered, "America/Los_Angeles") as order_time_jittered_utc,
    timestamp(taken_time_jittered, "America/Los_Angeles") as taken_time_jittered_utc,
    timestamp(result_time_jittered, "America/Los_Angeles") as result_time_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.lab_result;


-- lda
create table som-nero-phi-jonc101.shc_core_2023.lda as


select * except(placement_instant_jittered, removal_instant_jittered),
    placement_instant_jittered,
    removal_instant_jittered,
    timestamp(placement_instant_jittered, "America/Los_Angeles") as placement_instant_jittered_utc,
    timestamp(removal_instant_jittered, "America/Los_Angeles") as removal_instant_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.lda;


-- myc_mesg
create table som-nero-phi-jonc101.shc_core_2023.myc_mesg as

select * except(created_time_jittered, final_handled_time_jittered),
    created_time_jittered,
    final_handled_time_jittered,
    timestamp(created_time_jittered, "America/Los_Angeles") as created_time_jittered_utc,
    timestamp(final_handled_time_jittered, "America/Los_Angeles") as final_handled_time_jittered_utc,
    from `som-nero-phi-jonc101.shc_core_2022.myc_mesg`;

-- order_comment
create table som-nero-phi-jonc101.shc_core_2023.order_comment as

select * except(order_inst_jittered),
    order_inst_jittered,
    timestamp(order_inst_jittered, "America/Los_Angeles") as order_inst_jittered_utc,
    from `som-nero-phi-jonc101.shc_core_2022.order_comment`;


-- order_med
create table som-nero-phi-jonc101.shc_core_2023.order_med as

select * except(order_start_time_jittered, order_end_time_jittered, order_inst_jittered, discon_time_jittered, ordering_date_jittered, start_date_jittered, end_date_jittered),
    order_start_time_jittered,
    order_end_time_jittered,
    order_inst_jittered,
    discon_time_jittered,
    extract(date from ordering_date_jittered) as ordering_date_jittered,
    extract(date from start_date_jittered) as start_date_jittered,
    extract(date from end_date_jittered) as end_date_jittered,
    timestamp(order_start_time_jittered, "America/Los_Angeles") as order_start_time_jittered_utc,
    timestamp(order_end_time_jittered, "America/Los_Angeles") as order_end_time_jittered_utc,
    timestamp(order_inst_jittered, "America/Los_Angeles") as order_inst_jittered_utc,
    timestamp(discon_time_jittered, "America/Los_Angeles") as discon_time_jittered_utc,
    from `som-nero-phi-jonc101.shc_core_2022.order_med`;


-- order_proc
create table som-nero-phi-jonc101.shc_core_2023.order_proc as

select * except(ordering_date_jittered, standing_exp_date_jittered, proc_bgn_time_jittered, proc_end_time_jittered, order_inst_jittered, instantiated_time_jittered,
                order_time_jittered, result_time_jittered, proc_start_time_jittered, proc_date_jittered, last_stand_perf_dt_jittered, last_stand_perf_tm_jittered),

    extract(date from ordering_date_jittered) as ordering_date_jittered,    
    extract(date from standing_exp_date_jittered) as standing_exp_date_jittered,    
    proc_bgn_time_jittered,
    timestamp(proc_bgn_time_jittered, "America/Los_Angeles") as proc_bgn_time_jittered_utc,
    proc_end_time_jittered,
    timestamp(proc_end_time_jittered, "America/Los_Angeles") as proc_end_time_jittered_utc,
    order_inst_jittered,
    timestamp(order_inst_jittered, "America/Los_Angeles") as order_inst_jittered_utc,
    instantiated_time_jittered,
    timestamp(instantiated_time_jittered, "America/Los_Angeles") as instantiated_time_jittered_utc,
    order_time_jittered,
    timestamp(order_time_jittered, "America/Los_Angeles") as order_time_jittered_utc,
    result_time_jittered,
    timestamp(result_time_jittered, "America/Los_Angeles") as result_time_jittered_utc,
    proc_start_time_jittered,
    timestamp(proc_start_time_jittered, "America/Los_Angeles") as proc_start_time_jittered_utc,
    extract(date from proc_date_jittered) as proc_date_jittered,    
    extract(date from last_stand_perf_dt_jittered) as last_stand_perf_dt_jittered,    
    last_stand_perf_tm_jittered,
    timestamp(last_stand_perf_tm_jittered, "America/Los_Angeles") as last_stand_perf_tm_jittered_utc,
  
    from `som-nero-phi-jonc101.shc_core_2022.order_proc`;


--order_quest
create table som-nero-phi-jonc101.shc_core_2023.order_quest as

select * except(ord_quest_date_jittered),
    extract(date from ord_quest_date_jittered) as ord_quest_date_jittered,      
    from `som-nero-phi-jonc101.shc_core_2022.order_quest`;


-- pharmacy_mar
create table som-nero-phi-jonc101.shc_core_2023.pharmacy_mar as

select * except(taken_time_jittered, scheduled_time_jittered),
    taken_time_jittered,
    timestamp(taken_time_jittered, "America/Los_Angeles") as taken_time_jittered_utc,
    scheduled_time_jittered,
    timestamp(scheduled_time_jittered, "America/Los_Angeles") as scheduled_time_jittered_utc,
    from `som-nero-phi-jonc101.shc_core_2022.pharmacy_mar`;


-- procedure
create table som-nero-phi-jonc101.shc_core_2023.procedure as

select * except(proc_date_jittered, start_date_jittered, adm_date_time_jittered),
    extract(date from proc_date_jittered) as proc_date_jittered,    
    start_date_jittered,
    timestamp(start_date_jittered, "America/Los_Angeles") as start_date_jittered_utc,
    adm_date_time_jittered,
    timestamp(adm_date_time_jittered, "America/Los_Angeles") as adm_date_time_jittered_utc,
    from `som-nero-phi-jonc101.shc_core_2022.procedure`;


-- social_hx
create table som-nero-phi-jonc101.shc_core_2023.social_hx as

select * except(contact_date_jittered, smoking_quit_date, smokeless_quit_date_jittered),
    contact_date_jittered,    
    smoking_quit_date,    
    smokeless_quit_date_jittered,    
    from `som-nero-phi-jonc101.shc_core_2022.social_hx`;


-- treatment_team
create table som-nero-phi-jonc101.shc_core_2023.treatment_team as

select * except( trtmnt_tm_begin_dt_jittered, trtmnt_tm_end_dt_jittered),
    trtmnt_tm_begin_dt_jittered,
    timestamp(trtmnt_tm_begin_dt_jittered, "America/Los_Angeles") as trtmnt_tm_begin_dt_jittered_utc,
    trtmnt_tm_end_dt_jittered,
    timestamp(trtmnt_tm_end_dt_jittered, "America/Los_Angeles") as trtmnt_tm_end_dt_jittered_utc,
    from `som-nero-phi-jonc101.shc_core_2022.treatment_team`;



-- ib_messages
create table som-nero-phi-jonc101.shc_core_2023.ib_messages as

select * except(create_time_jittered, send_on_jittered),
    create_time_jittered,
    send_on_jittered,
    timestamp(create_time_jittered, "America/Los_Angeles") as create_time_jittered_utc,
    timestamp(send_on_jittered, "America/Los_Angeles") as send_on_jittered_utc,
    from som-nero-phi-jonc101.shc_core_2022.ib_messages;


-- extract meas values
create table som-nero-phi-jonc101.shc_core_2023.flowsheet_with_meas_values as

select * from (
  select A.anon_id, A.inpatient_data_id_coded , A.line, A.template, A.row_disp_name, A.meas_value, A.units, A.data_source, A.recorded_time_jittered, A.recorded_time_jittered_utc, offset + 1 as offset, num
  from `som-nero-phi-jonc101.shc_core_2023.flowsheet` A 
  left join unnest(regexp_extract_all(A.meas_value, r'(-?[\d\.]+)')) num with offset
)
pivot (min(num) as numerical_val for offset in (1,2,3,4)) 
```
