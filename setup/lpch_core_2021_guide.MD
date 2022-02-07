<h1 style="font-size:60px;">1. Copying tables</h1>

The first step is to simply copy all tables under the database ```som-nero-phi-naras-ric:Jon_Chen_data_Oct_2021``` with the prefix of ```lpch_``` in the table name to the database ```som-nero-phi-jonc101.lpch_core_2021```. Note, the database ```lpch_core_2021``` was created by me and the database ```som-nero-phi-naras-ric:Jon_Chen_data_Oct_2021``` was provided to us by the database admin. 

To copy the tables: 
1) click on the tables name under the Explorer section
2) click on the copy button (the copy button apears on a bar on top right side after clicking on the table and it's next to other buttons QUERY, SHARE, COPY, SNAPSHOT, DELETE, EXPORT)
3) Select the ```som-nero-phi-jonc101``` project in the project name dropbox menue. Select ```lpch_core_2021``` under the dataset name dropbox menue. And write a table name for the coppied table. I used the same name as original table names except I droped the prefix ```lpch_``` in the table names. For example, when copying ```lpch_flowsheet``` I used ```flowsheet``` as the name for the coppied table. Note, there are two tables, ```prov_map``` and ```yn_jon_chen_lpch```, that do not have ```shc``` or ```lpch``` in their name and I coppied thse two tables under both ```shc_core_2021``` and ```lpch_core_2021```.
4) Repeat this process and coppy all lpch tables under ```lpch_core_2021```.

<h1 style="font-size:60px;">1. Re-formating datetime columns</h1>

Here, we convert convert string columns that nicludes date/datetime to date/datetime format. To check if a string column includes datetime values or date only values, we can use the following script and run it seperately for each column. Note, here we check the ```effective_time_jittered``` columns in table ```adt``` as an example. If this query returns more than 1 rows and each for a different time, then this means the ```effective_time_jittered``` column include multiple diiferent times and should be treated as a datetime column. For some columns, this query only returns 1 row 00:00:00(or 1 row for 00:00:00 plus another null row) and this means the current column should be converted to a date only format as all the dates are the same and do not include any extra information (but for some reason they have been save in a 'Y-M-D H:M:S' like format even though the 'H:M:S' does not include meaningful time points).  

```
select extract(time from case when effective_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', effective_time_jittered) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.adt
group by times
order by cnt desc;
```

For each table, visualy look into a number of rows. If you clearly see different time values in the columns that means you don't need to run the above script. However, if you don't see any different in terms of time you can run the above script to double check. 

After, identifying date only and datetime columns for each table you can use the following scripts to convert the columns. Here, I provide the scripts for each table seperately. Note, after running each columns I save the results in a big query table with the same name as the original table plus a "_code" at the end of the name of this new table. 

For example, for the ```adt``` tble, I first visually inspect the columns and identify that ```effective_time_jittered``` and ```event_time_jittered``` include date and time information but are saved in strings. Note, since for a sample of rows I can see they include different rows I don't need to run the above scripts. Therefore, I use the following script to convert string fields to datetime and create utc datetime:

```
select * except(effective_time_jittered, event_time_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when effective_time_jittered <> '' then effective_time_jittered else null end) as effective_time_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when event_time_jittered <> '' then event_time_jittered else null end) as event_time_jittered,
    timestamp(case when effective_time_jittered <> '' then effective_time_jittered else null end, "America/Los_Angeles") as effective_time_jittered_utc,
    timestamp(case when event_time_jittered <> '' then event_time_jittered else null end, "America/Los_Angeles") as event_time_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.adt;
```
 And saved the results in ```adt_code``` under ```lpch_core_2021``` manually using the SAVE RESULTS option or by setting up the query result destination settings before runnig the above query: More>Query Settings>Set a destination table for query results. 
 
Here are the queries for the rest of the tables:
```
-- alert
select * except(update_date_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when update_date_jittered <> '' then update_date_jittered else null end) as update_date_jittered,
    timestamp(case when update_date_jittered <> '' then update_date_jittered else null end, "America/Los_Angeles") as update_date_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.alert;
    
-- alert_history
select extract(time from contact_date) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.alert_history
group by times
order by cnt desc;

select * except(update_date_jittered, alt_action_inst, contact_date),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when update_date_jittered <> '' then update_date_jittered else null end) as update_date_jittered,
    alt_action_inst,
    extract(date from contact_date) as contact_date,
    timestamp(case when update_date_jittered <> '' then update_date_jittered else null end, "America/Los_Angeles") as update_date_jittered_utc,
    timestamp(alt_action_inst, "America/Los_Angeles") as alt_action_inst_utc,
    from som-nero-phi-jonc101.lpch_core_2021.alert_history;

-- alerts_orders
select * except(update_date_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when update_date_jittered <> '' then update_date_jittered else null end) as update_date_jittered,
    timestamp(case when update_date_jittered <> '' then update_date_jittered else null end, "America/Los_Angeles") as update_date_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.alerts_orders;

-- allergy
select extract(time from case when date_noted_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', date_noted_jittered) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.allergy
group by times
order by cnt desc;

select * except(date_noted_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when date_noted_jittered <> '' then date_noted_jittered else null end)) as date_noted_jittered,
    from som-nero-phi-jonc101.lpch_core_2021.allergy;
    
-- alt_com_action
select extract(time from case when contact_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', contact_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.alt_com_action`
group by times
order by cnt desc;

select * except(contact_date_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when contact_date_jittered <> '' then contact_date_jittered else null end)) as contact_date_jittered,
    from som-nero-phi-jonc101.lpch_core_2021.alt_com_action;
    
-- clinical_doc_meta
select extract(time from case when activity_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', activity_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.clinical_doc_meta`
group by times
order by cnt desc;

select * except(filing_date_jittered, note_date_jittered, activity_date_jittered, effective_time_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when filing_date_jittered <> '' then filing_date_jittered else null end) as filing_date_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when note_date_jittered <> '' then note_date_jittered else null end) as note_date_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when activity_date_jittered <> '' then activity_date_jittered else null end) as activity_date_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when effective_time_jittered <> '' then effective_time_jittered else null end) as effective_time_jittered,
    timestamp(case when filing_date_jittered <> '' then filing_date_jittered else null end, "America/Los_Angeles") as filing_date_jittered_utc,
    timestamp(case when note_date_jittered <> '' then note_date_jittered else null end, "America/Los_Angeles") as note_date_jittered_utc,
    timestamp(case when activity_date_jittered <> '' then activity_date_jittered else null end, "America/Los_Angeles") as activity_date_jittered_utc,
    timestamp(case when effective_time_jittered <> '' then effective_time_jittered else null end, "America/Los_Angeles") as effective_time_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.clinical_doc_meta;
    

--culture_sensitivity
select extract(time from case when sens_obs_inst_tm_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', sens_obs_inst_tm_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.culture_sensitivity`
group by times
order by cnt desc;

select * except(order_time_jittered, result_time_jittered, sens_obs_inst_tm_jittered, sens_anl_inst_tm_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_time_jittered <> '' then order_time_jittered else null end) as order_time_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when result_time_jittered <> '' then result_time_jittered else null end) as result_time_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when sens_obs_inst_tm_jittered <> '' then sens_obs_inst_tm_jittered else null end) as sens_obs_inst_tm_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when sens_anl_inst_tm_jittered <> '' then sens_anl_inst_tm_jittered else null end) as sens_anl_inst_tm_jittered,
    timestamp(case when order_time_jittered <> '' then order_time_jittered else null end, "America/Los_Angeles") as order_time_jittered_utc,
    timestamp(case when result_time_jittered <> '' then result_time_jittered else null end, "America/Los_Angeles") as result_time_jittered_utc,
    timestamp(case when sens_obs_inst_tm_jittered <> '' then sens_obs_inst_tm_jittered else null end, "America/Los_Angeles") as sens_obs_inst_tm_jittered_utc,
    timestamp(case when sens_anl_inst_tm_jittered <> '' then sens_anl_inst_tm_jittered else null end, "America/Los_Angeles") as sens_anl_inst_tm_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.culture_sensitivity;
    
-- demographic
select extract(time from birth_date_jittered) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.demographic`
group by times
order by cnt desc;

select extract(time from death_date_jittered) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.demographic`
group by times
order by cnt desc;


select * except(birth_date_jittered, death_date_jittered),
    extract(date from birth_date_jittered) as birth_date_jittered,
    extract(date from death_date_jittered) as death_date_jittered,
    from som-nero-phi-jonc101.lpch_core_2021.demographic;


-- dep_map and drg_code do not include any datetime or date columns

-- Diagnosis
select extract(time from case when start_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', start_date) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.diagnosis
group by times
order by cnt desc;

select extract(time from case when end_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', end_date) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.diagnosis
group by times
order by cnt desc;

select extract(time from case when noted_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', noted_date) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.diagnosis
group by times
order by cnt desc;

select extract(time from case when hx_date_of_entry <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', hx_date_of_entry) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.diagnosis
group by times
order by cnt desc;

select extract(time from case when resolved_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', resolved_date) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.diagnosis
group by times
order by cnt desc;


select * except(end_date, start_date, noted_date, hx_date_of_entry, resolved_date),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when end_date <> '' then end_date else null end) as end_date,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when start_date <> '' then start_date else null end) as start_date,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when noted_date <> '' then noted_date else null end)) as noted_date,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when hx_date_of_entry <> '' then hx_date_of_entry else null end)) as hx_date_of_entry,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when resolved_date <> '' then resolved_date else null end)) as resolved_date,
    timestamp(case when end_date <> '' then end_date else null end, "America/Los_Angeles") as end_date_utc,
    timestamp(case when start_date <> '' then start_date else null end, "America/Los_Angeles") as start_date_utc,
    from som-nero-phi-jonc101.lpch_core_2021.diagnosis;
    

-- encounter
select extract(time from case when adt_arrival_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', adt_arrival_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.encounter`
group by times
order by cnt desc;

select extract(time from case when hosp_admsn_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', hosp_admsn_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.encounter`
group by times
order by cnt desc;

select extract(time from case when appt_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', appt_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.encounter`
group by times
order by cnt desc;

select extract(time from case when appt_when_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', appt_when_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.encounter`
group by times
order by cnt desc;

select extract(time from case when hosp_dischrg_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', hosp_dischrg_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.encounter`
group by times
order by cnt desc;

select extract(time from case when contact_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', contact_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.encounter`
group by times
order by cnt desc;

select * except(adt_arrival_time_jittered, hosp_admsn_time_jittered, appt_time_jittered, appt_when_jittered, hosp_dischrg_time_jittered, contact_date_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when contact_date_jittered <> '' then contact_date_jittered else null end)) as contact_date_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when adt_arrival_time_jittered <> '' then adt_arrival_time_jittered else null end) as adt_arrival_time_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when hosp_admsn_time_jittered <> '' then hosp_admsn_time_jittered else null end) as hosp_admsn_time_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when appt_time_jittered <> '' then appt_time_jittered else null end) as appt_time_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when appt_when_jittered <> '' then appt_when_jittered else null end) as appt_when_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when hosp_dischrg_time_jittered <> '' then hosp_dischrg_time_jittered else null end) as hosp_dischrg_time_jittered,
    timestamp(case when adt_arrival_time_jittered <> '' then adt_arrival_time_jittered else null end, "America/Los_Angeles") as adt_arrival_time_jittered_utc,
    timestamp(case when hosp_admsn_time_jittered <> '' then hosp_admsn_time_jittered else null end, "America/Los_Angeles") as hosp_admsn_time_jittered_utc,
    timestamp(case when appt_time_jittered <> '' then appt_time_jittered else null end, "America/Los_Angeles") as appt_time_jittered_utc,
    timestamp(case when appt_when_jittered <> '' then appt_when_jittered else null end, "America/Los_Angeles") as appt_when_jittered_utc,
    timestamp(case when hosp_dischrg_time_jittered <> '' then hosp_dischrg_time_jittered else null end, "America/Los_Angeles") as hosp_dischrg_time_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.encounter;
    
 
```
