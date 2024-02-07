#### Learning Objectives:
- Identify and access an updated dataset from an external project in BigQuery.
- Copy the identified dataset into a new dataset with a unique ID within your own BigQuery project.
- Apply transformations to datetime columns to standardize them into UTC format and extract numerical data from string-type flowsheet measurements.
- Set up appropriate access controls for the newly created dataset.
- Streamline the process for annual updates, ensuring efficient data management, data integrity, and adherence to time-based analysis standards.

# 0. Accessing the Updated Dataset
#### 1. Add the External Project to Your Project List
* In the BigQuery console, click on "+ ADD" on the top left.
* Choose "Star a project by name" from the dropdown menu.
* In the dialog that appears, type the name of the external project you have been granted access to (e.g., `som-nero-phi-naras-ric`) and press Enter.
* The project should now be listed in your BigQuery resources.

#### 2. Locate the Updated Dataset
* Navigate to the newly pinned project in your resource list.
* Expand the project to view the available datasets.
* Identify the updated dataset you need to copy (e.g., `updated_dataset_2024`).

<h1 style="font-size:60px;">1. Copying tables</h1>

The first step is to simply copy all tables under the database ```som-nero-phi-naras-ric:Jon_Chen_data_Oct_2021``` with the prefix of ```lpch_``` in the table name to the database ```som-nero-phi-jonc101.lpch_core_2021```. Note, the database ```lpch_core_2021``` was created by me and the database ```som-nero-phi-naras-ric:Jon_Chen_data_Oct_2021``` was provided to us by the database admin. 

To copy the tables: 
1) click on the tables name under the Explorer section
2) click on the copy button (the copy button apears on a bar on top right side after clicking on the table and it's next to other buttons QUERY, SHARE, COPY, SNAPSHOT, DELETE, EXPORT)
3) Select the ```som-nero-phi-jonc101``` project in the project name dropbox menue. Select ```lpch_core_2021``` under the dataset name dropbox menue. And write a table name for the coppied table. I used the same name as original table names except I droped the prefix ```lpch_``` in the table names. For example, when copying ```lpch_flowsheet``` I used ```flowsheet``` as the name for the coppied table. Note, there are two tables, ```prov_map``` and ```yn_jon_chen_lpch```, that do not have ```shc``` or ```lpch``` in their name and I coppied thse two tables under both ```shc_core_2021``` and ```lpch_core_2021```.
4) Repeat this process and coppy all lpch tables under ```lpch_core_2021```.

<h1 style="font-size:60px;">2. Re-formating datetime columns</h1>

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

-- alert
```
select * except(update_date_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when update_date_jittered <> '' then update_date_jittered else null end) as update_date_jittered,
    timestamp(case when update_date_jittered <> '' then update_date_jittered else null end, "America/Los_Angeles") as update_date_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.alert;
```    
-- alert_history
```
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
```

-- alerts_orders
```
select * except(update_date_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when update_date_jittered <> '' then update_date_jittered else null end) as update_date_jittered,
    timestamp(case when update_date_jittered <> '' then update_date_jittered else null end, "America/Los_Angeles") as update_date_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.alerts_orders;
```

-- allergy
```
select extract(time from case when date_noted_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', date_noted_jittered) else null end) times, count(*) as cnt
from som-nero-phi-jonc101.lpch_core_2021.allergy
group by times
order by cnt desc;

select * except(date_noted_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when date_noted_jittered <> '' then date_noted_jittered else null end)) as date_noted_jittered,
    from som-nero-phi-jonc101.lpch_core_2021.allergy;
```    

-- alt_com_action
```
select extract(time from case when contact_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', contact_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.alt_com_action`
group by times
order by cnt desc;

select * except(contact_date_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when contact_date_jittered <> '' then contact_date_jittered else null end)) as contact_date_jittered,
    from som-nero-phi-jonc101.lpch_core_2021.alt_com_action;
```

-- clinical_doc_meta
```
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
```    

--culture_sensitivity
```
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
```

-- demographic
```
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
```

-- dep_map and drg_code do not include any datetime or date columns


-- Diagnosis
```
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
```    

-- encounter
```
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
    
-- f_ip_hsp_admission
```
select extract(time from case when hosp_adm_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', hosp_adm_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.f_ip_hsp_admission`
group by times
order by cnt desc;

select extract(time from case when hosp_disch_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', hosp_disch_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.f_ip_hsp_admission`
group by times
order by cnt desc;

select * except(hosp_adm_date_jittered, hosp_disch_date_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when hosp_adm_date_jittered <> '' then hosp_adm_date_jittered else null end)) as hosp_adm_date_jittered,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when hosp_disch_date_jittered <> '' then hosp_disch_date_jittered else null end)) as hosp_disch_date_jittered,
    from som-nero-phi-jonc101.lpch_core_2021.f_ip_hsp_admission;
```

-- family_hx
```
select extract(time from case when contact_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', contact_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.family_hx`
group by times
order by cnt desc;

select * except(contact_date_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when contact_date_jittered <> '' then contact_date_jittered else null end)) as contact_date_jittered,
    from som-nero-phi-jonc101.lpch_core_2021.family_hx;
```

--flowsheet: NOTE: I had to set up destination because the result was too large. 
```
select * except(recorded_time),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when recorded_time <> '' then recorded_time else null end) as recorded_time,
    timestamp(case when recorded_time <> '' then recorded_time else null end, "America/Los_Angeles") as recorded_time_utc,
    from som-nero-phi-jonc101.lpch_core_2021.flowsheet;
```    
    
-- lab_result
```
select * except(order_time, taken_time, result_time),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_time <> '' then order_time else null end) as order_time,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when taken_time <> '' then taken_time else null end) as taken_time,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when result_time <> '' then result_time else null end) as result_time,
    timestamp(case when order_time <> '' then order_time else null end, "America/Los_Angeles") as order_time_utc,
    timestamp(case when taken_time <> '' then taken_time else null end, "America/Los_Angeles") as taken_time_utc,
    timestamp(case when result_time <> '' then result_time else null end, "America/Los_Angeles") as result_time_utc,
    from som-nero-phi-jonc101.lpch_core_2021.lab_result;
```    
    
-- lda
```
select * except(placement_instant_jittered, removal_instant_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when placement_instant_jittered <> '' then placement_instant_jittered else null end) as placement_instant_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when removal_instant_jittered <> '' then removal_instant_jittered else null end) as removal_instant_jittered,
    timestamp(case when placement_instant_jittered <> '' then placement_instant_jittered else null end, "America/Los_Angeles") as placement_instant_jittered_utc,
    timestamp(case when removal_instant_jittered <> '' then removal_instant_jittered else null end, "America/Los_Angeles") as removal_instant_jittered_utc,
    from som-nero-phi-jonc101.lpch_core_2021.lda;
```

-- myc_mesg
```
select * except(created_time_jittered, final_handled_time_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when created_time_jittered <> '' then created_time_jittered else null end) as created_time_jittered,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when final_handled_time_jittered <> '' then final_handled_time_jittered else null end) as final_handled_time_jittered,
    timestamp(case when created_time_jittered <> '' then created_time_jittered else null end, "America/Los_Angeles") as created_time_jittered_utc,
    timestamp(case when final_handled_time_jittered <> '' then final_handled_time_jittered else null end, "America/Los_Angeles") as final_handled_time_jittered_utc,
    from `som-nero-phi-jonc101.lpch_core_2021.myc_mesg`;
```    
 
--ndc_code does not include any datetime/date columns


-- order_comment
```
select * except(order_inst_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_inst_jittered <> '' then order_inst_jittered else null end) as order_inst_jittered,
    timestamp(case when order_inst_jittered <> '' then order_inst_jittered else null end, "America/Los_Angeles") as order_inst_jittered_utc,
    from `som-nero-phi-jonc101.lpch_core_2021.order_comment`;
```

-- order_med
```
select extract(time from case when order_start_time <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', order_start_time) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_med`
group by times
order by cnt desc;

select extract(time from case when order_end_time <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', order_end_time) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_med`
group by times
order by cnt desc;

select extract(time from case when order_inst <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', order_inst) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_med`
group by times
order by cnt desc;

select extract(time from case when discon_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', discon_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_med`
group by times
order by cnt desc;

select extract(time from case when order_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', order_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_med`
group by times
order by cnt desc;

select extract(time from case when start_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', start_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_med`
group by times
order by cnt desc;

select extract(time from case when end_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', end_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_med`
group by times
order by cnt desc;

select * except(order_start_time, order_end_time, order_inst, discon_time_jittered, order_time_jittered, start_time_jittered, end_time_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_start_time <> '' then order_start_time else null end) as order_start_time,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_end_time <> '' then order_end_time else null end) as order_end_time,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_inst <> '' then order_inst else null end) as order_inst,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when discon_time_jittered <> '' then discon_time_jittered else null end) as discon_time_jittered,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when order_time_jittered <> '' then order_time_jittered else null end)) as order_time_jittered,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when start_time_jittered <> '' then start_time_jittered else null end)) as start_time_jittered,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when end_time_jittered <> '' then end_time_jittered else null end)) as end_time_jittered,
    timestamp(case when order_start_time <> '' then order_start_time else null end, "America/Los_Angeles") as order_start_time_utc,
    timestamp(case when order_end_time <> '' then order_end_time else null end, "America/Los_Angeles") as order_end_time_utc,
    timestamp(case when order_inst <> '' then order_inst else null end, "America/Los_Angeles") as order_inst_utc,
    timestamp(case when discon_time_jittered <> '' then discon_time_jittered else null end, "America/Los_Angeles") as discon_time_jittered_utc,
    from `som-nero-phi-jonc101.lpch_core_2021.order_med`;
```    

-- order_proc
```
select extract(time from case when ordering_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', ordering_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when standing_exp_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', standing_exp_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when proc_bgn_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', proc_bgn_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when proc_end_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', proc_end_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when order_inst_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', order_inst_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when instantiated_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', instantiated_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when order_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', order_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when result_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', result_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when proc_start_time_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', proc_start_time_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when proc_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', proc_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when last_stand_perf_dt_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', last_stand_perf_dt_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;

select extract(time from case when last_stand_perf_tm_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', last_stand_perf_tm_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_proc`
group by times
order by cnt desc;


select * except(ordering_date_jittered, standing_exp_date_jittered, proc_bgn_time_jittered, proc_end_time_jittered, order_inst_jittered, instantiated_time_jittered,
                order_time_jittered, result_time_jittered, proc_start_time_jittered, proc_date_jittered, last_stand_perf_dt_jittered, last_stand_perf_tm_jittered),

    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when ordering_date_jittered <> '' then ordering_date_jittered else null end)) as ordering_date_jittered,    
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when standing_exp_date_jittered <> '' then standing_exp_date_jittered else null end)) as standing_exp_date_jittered,    
    parse_datetime('%Y-%m-%d %H:%M:%S', case when proc_bgn_time_jittered <> '' then proc_bgn_time_jittered else null end) as proc_bgn_time_jittered,
    timestamp(case when proc_bgn_time_jittered <> '' then proc_bgn_time_jittered else null end, "America/Los_Angeles") as proc_bgn_time_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when proc_end_time_jittered <> '' then proc_end_time_jittered else null end) as proc_end_time_jittered,
    timestamp(case when proc_end_time_jittered <> '' then proc_end_time_jittered else null end, "America/Los_Angeles") as proc_end_time_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_inst_jittered <> '' then order_inst_jittered else null end) as order_inst_jittered,
    timestamp(case when order_inst_jittered <> '' then order_inst_jittered else null end, "America/Los_Angeles") as order_inst_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when instantiated_time_jittered <> '' then instantiated_time_jittered else null end) as instantiated_time_jittered,
    timestamp(case when instantiated_time_jittered <> '' then instantiated_time_jittered else null end, "America/Los_Angeles") as instantiated_time_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when order_time_jittered <> '' then order_time_jittered else null end) as order_time_jittered,
    timestamp(case when order_time_jittered <> '' then order_time_jittered else null end, "America/Los_Angeles") as order_time_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when result_time_jittered <> '' then result_time_jittered else null end) as result_time_jittered,
    timestamp(case when result_time_jittered <> '' then result_time_jittered else null end, "America/Los_Angeles") as result_time_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when proc_start_time_jittered <> '' then proc_start_time_jittered else null end) as proc_start_time_jittered,
    timestamp(case when proc_start_time_jittered <> '' then proc_start_time_jittered else null end, "America/Los_Angeles") as proc_start_time_jittered_utc,
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when proc_date_jittered <> '' then proc_date_jittered else null end)) as proc_date_jittered,    
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when last_stand_perf_dt_jittered <> '' then last_stand_perf_dt_jittered else null end)) as last_stand_perf_dt_jittered,    
    parse_datetime('%Y-%m-%d %H:%M:%S', case when last_stand_perf_tm_jittered <> '' then last_stand_perf_tm_jittered else null end) as last_stand_perf_tm_jittered,
    timestamp(case when last_stand_perf_tm_jittered <> '' then last_stand_perf_tm_jittered else null end, "America/Los_Angeles") as last_stand_perf_tm_jittered_utc,
  
    from `som-nero-phi-jonc101.lpch_core_2021.order_proc`;
```    
    
--order_quest
```
select extract(time from case when ord_quest_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', ord_quest_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.order_quest`
group by times
order by cnt desc;

select * except(ord_quest_date_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when ord_quest_date_jittered <> '' then ord_quest_date_jittered else null end)) as ord_quest_date_jittered,      
    from `som-nero-phi-jonc101.lpch_core_2021.order_quest`;
```    

--pharmacy_mar
```
select * except(taken_time_jittered, scheduled_time_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when taken_time_jittered <> '' then taken_time_jittered else null end) as taken_time_jittered,
    timestamp(case when taken_time_jittered <> '' then taken_time_jittered else null end, "America/Los_Angeles") as taken_time_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when scheduled_time_jittered <> '' then scheduled_time_jittered else null end) as scheduled_time_jittered,
    timestamp(case when scheduled_time_jittered <> '' then scheduled_time_jittered else null end, "America/Los_Angeles") as scheduled_time_jittered_utc,
    from `som-nero-phi-jonc101.lpch_core_2021.pharmacy_mar`;
```

--proc_note
```
select extract(time from case when ordering_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', ordering_date) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.proc_note`
group by times
order by cnt desc;

select * except(ordering_date, proc_start_time, proc_end_time, result_time),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when ordering_date <> '' then ordering_date else null end)) as ordering_date,    
    parse_datetime('%Y-%m-%d %H:%M:%S', case when proc_start_time <> '' then proc_start_time else null end) as proc_start_time,
    timestamp(case when proc_start_time <> '' then proc_start_time else null end, "America/Los_Angeles") as proc_start_time_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when proc_end_time <> '' then proc_end_time else null end) as proc_end_time,
    timestamp(case when proc_end_time <> '' then proc_end_time else null end, "America/Los_Angeles") as proc_end_time_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when result_time <> '' then result_time else null end) as result_time,
    timestamp(case when result_time <> '' then result_time else null end, "America/Los_Angeles") as result_time_utc,    
    from `som-nero-phi-jonc101.lpch_core_2021.proc_note`;
```    
    
-- prov_map does not include any datetime/date columns

--proc_orderset does not include any datetime/date columns

-- procedure
```
select extract(time from case when proc_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', proc_date) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.procedure`
group by times
order by cnt desc;

select extract(time from case when start_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', start_date) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.procedure`
group by times
order by cnt desc;

select extract(time from case when adm_date_time <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', adm_date_time) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.procedure`
group by times
order by cnt desc;

select * except(proc_date, start_date, adm_date_time),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when proc_date <> '' then proc_date else null end)) as proc_date,    
    parse_datetime('%Y-%m-%d %H:%M:%S', case when start_date <> '' then start_date else null end) as start_date,
    timestamp(case when start_date <> '' then start_date else null end, "America/Los_Angeles") as start_date_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when adm_date_time <> '' then adm_date_time else null end) as adm_date_time,
    timestamp(case when adm_date_time <> '' then adm_date_time else null end, "America/Los_Angeles") as adm_date_time_utc,
    from `som-nero-phi-jonc101.lpch_core_2021.procedure`;
```

-- prov_map does not include any datetime/date columns

-- social_hx
```
select extract(time from case when contact_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', contact_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.social_hx`
group by times
order by cnt desc;

select extract(time from case when smoking_quit_date <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', smoking_quit_date) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.social_hx`
group by times
order by cnt desc;

select extract(time from case when smokeless_quit_date_jittered <> '' then parse_datetime('%Y-%m-%d %H:%M:%S', smokeless_quit_date_jittered) else null end) times, count(*) as cnt
from `som-nero-phi-jonc101.lpch_core_2021.social_hx`
group by times
order by cnt desc;


select * except(contact_date_jittered, smoking_quit_date, smokeless_quit_date_jittered),
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when contact_date_jittered <> '' then contact_date_jittered else null end)) as contact_date_jittered,    
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when smoking_quit_date <> '' then smoking_quit_date else null end)) as smoking_quit_date,    
    extract(date from parse_datetime('%Y-%m-%d %H:%M:%S', case when smokeless_quit_date_jittered <> '' then smokeless_quit_date_jittered else null end)) as smokeless_quit_date_jittered,    
    from `som-nero-phi-jonc101.lpch_core_2021.social_hx`;
```

-- treatment_team
```
select * except( trtmnt_tm_begin_dt_jittered, trtmnt_tm_end_dt_jittered),
    parse_datetime('%Y-%m-%d %H:%M:%S', case when trtmnt_tm_begin_dt_jittered <> '' then trtmnt_tm_begin_dt_jittered else null end) as trtmnt_tm_begin_dt_jittered,
    timestamp(case when trtmnt_tm_begin_dt_jittered <> '' then trtmnt_tm_begin_dt_jittered else null end, "America/Los_Angeles") as trtmnt_tm_begin_dt_jittered_utc,
    parse_datetime('%Y-%m-%d %H:%M:%S', case when trtmnt_tm_end_dt_jittered <> '' then trtmnt_tm_end_dt_jittered else null end) as trtmnt_tm_end_dt_jittered,
    timestamp(case when trtmnt_tm_end_dt_jittered <> '' then trtmnt_tm_end_dt_jittered else null end, "America/Los_Angeles") as trtmnt_tm_end_dt_jittered_utc,
    from `som-nero-phi-jonc101.lpch_core_2021.treatment_team`;
```    

-- yn_jon_chen_lpch does not include any datetime/date columns

 Finally, I removed the ```_code``` at the end of all table.
 
<h1 style="font-size:60px;">3. Extracting numerical values from meas_value in flowsheet</h1>

Table ```flowsheet``` has a string column, ```meas_value```, which include numerical values. Use the following code to extract those numerical values from ```meas_value``` and store them in seperate columns:

```
select * from (
  select A.anon_id, A.inpatient_data_id_coded , A.line, A.template, A.row_disp_name, A.meas_value, A.units, A.data_source, A.recorded_time, A.recorded_time_utc, offset + 1 as offset, num
  from `som-nero-phi-jonc101.lpch_core_2021.flowsheet` A 
  left join unnest(regexp_extract_all(A.meas_value, r'(-?[\d\.]+)')) num with offset
)
pivot (min(num) as numerical_val for offset in (1,2,3,4)) 
```

<h1 style="font-size:60px;">4. Testing SHC tables</h1>

Use the following script to compare the original ```shc_clinical_doc_meta``` table with the coppied one under ```shc_core_2021```, ```clinical_doc_meta```:


```
SELECT
    *
FROM `som-nero-phi-jonc101.shc_core_2021.clinical_doc_meta` A
FULL OUTER JOIN `som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021.shc_clinical_doc_meta` B
 on FARM_FINGERPRINT(ARRAY_TO_STRING([A.anon_id 
                                    , CAST(A.pat_enc_csn_id_coded AS STRING)
                                    , CAST(A.filing_date_jittered AS STRING)
                                    , CAST(A.note_date_jittered AS STRING)
                                    , CAST(A.activity_date_jittered AS STRING)
                                    , A.author_prov_map_id
                                    , CAST(A.effective_dept_id AS STRING)
                                    , A.note_status_c
                                    , A.note_status
                                    , A.ambulatory
                                    , CAST(A.ltr_status_c AS STRING)
                                    , A.letter_status
                                    , A.note_type
                                    , CAST(A.effective_time_jittered AS STRING)
                                    , A.auth_lnked_prov_map_id
                                    , A.cosign_prov_map_id
                                    , A.data_source],"")) = 
        FARM_FINGERPRINT(ARRAY_TO_STRING([B.anon_id 
                                    , CAST(B.pat_enc_csn_id_coded AS STRING)
                                    , B.filing_date_jittered
                                    , B.note_date_jittered
                                    , B.activity_date_jittered
                                    , B.author_prov_map_id
                                    , CAST(B.effective_dept_id AS STRING)
                                    , B.note_status_c
                                    , B.note_status
                                    , B.ambulatory
                                    , CAST(B.ltr_status_c AS STRING)
                                    , B.letter_status
                                    , B.note_type
                                    , B.effective_time_jittered
                                    , B.auth_lnked_prov_map_id
                                    , B.cosign_prov_map_id
                                    , B.data_source],"")) 
WHERE A.anon_id IS NULL 
OR B.anon_id IS NULL
```

For other tables similarly:
```
-- adt
SELECT
    *
FROM `som-nero-phi-jonc101.shc_core_2021.adt` A
FULL OUTER JOIN `som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021.shc_adt` B
 on FARM_FINGERPRINT(ARRAY_TO_STRING([A.anon_id 
                                    , CAST(A.pat_enc_csn_id_coded AS STRING)
                                    , CAST(A.event_id_coded AS STRING)
                                    , CAST(A.event_type_c AS STRING)
                                    , A.event_type
                                    , CAST(A.event_subtype_c AS STRING)
                                    , A.event_subtype
                                    , CAST(A.department_id AS STRING)
                                    , A.pat_class_c
                                    , A.pat_class
                                    , CAST(A.base_pat_class_c AS STRING)
                                    , A.base_pat_class
                                    , A.pat_service_c
                                    , A.pat_service
                                    , A.status_of_bed_c
                                    , A.status_of_bed
                                    , A.pat_lvl_of_care_c
                                    , A.pat_lv_of_care
                                    , CAST(A.xfer_event_id_coded AS STRING)
                                    , CAST(A.swap_event_id_coded AS STRING)
                                    , A.reason_c
                                    , A.accommodation_c
                                    , A.accomodation
                                    , CAST(A.accom_reason_c AS STRING)
                                    , CAST(A.adm_event_id_coded AS STRING)
                                    , CAST(A.dis_event_id_coded AS STRING)
                                    , CAST(A.xfer_in_event_id_coded AS STRING)
                                    , CAST(A.next_out_event_id_coded AS STRING)
                                    , CAST(A.last_in_event_id_coded AS STRING)
                                    , CAST(A.prev_event_id_coded AS STRING)
                                    , CAST(A.in_event_type_c AS STRING)
                                    , A.in_event_type
                                    , CAST(A.out_event_type_c AS STRING)
                                    , A.out_event_type
                                    , CAST(A.from_base_class_c AS STRING)
                                    , A.from_base_class
                                    , CAST(A.to_base_class_c AS STRING)
                                    , A.to_base_class
                                    , CAST(A.seq_num_in_enc AS STRING)
                                    , CAST(A.seq_num_in_bed_min AS STRING)
                                    , CAST(A.labor_status_c AS STRING)
                                    , A.first_ip_in_ip_yn
                                    , CAST(A.loa_reason_c AS STRING)
                                    , A.data_source
                                    , CAST(A.effective_time_jittered AS STRING)
                                    , CAST(A.event_time_jittered AS STRING)],"")) = 
        FARM_FINGERPRINT(ARRAY_TO_STRING([B.anon_id 
                                    , CAST(B.pat_enc_csn_id_coded AS STRING)
                                    , CAST(B.event_id_coded AS STRING)
                                    , CAST(B.event_type_c AS STRING)
                                    , B.event_type
                                    , CAST(B.event_subtype_c AS STRING)
                                    , B.event_subtype
                                    , CAST(B.department_id AS STRING)
                                    , B.pat_class_c
                                    , B.pat_class
                                    , CAST(B.base_pat_class_c AS STRING)
                                    , B.base_pat_class
                                    , B.pat_service_c
                                    , B.pat_service
                                    , B.status_of_bed_c
                                    , B.status_of_bed
                                    , B.pat_lvl_of_care_c
                                    , B.pat_lv_of_care
                                    , CAST(B.xfer_event_id_coded AS STRING)
                                    , CAST(B.swap_event_id_coded AS STRING)
                                    , B.reason_c
                                    , B.accommodation_c
                                    , B.accomodation
                                    , CAST(B.accom_reason_c AS STRING)
                                    , CAST(B.adm_event_id_coded AS STRING)
                                    , CAST(B.dis_event_id_coded AS STRING)
                                    , CAST(B.xfer_in_event_id_coded AS STRING)
                                    , CAST(B.next_out_event_id_coded AS STRING)
                                    , CAST(B.last_in_event_id_coded AS STRING)
                                    , CAST(B.prev_event_id_coded AS STRING)
                                    , CAST(B.in_event_type_c AS STRING)
                                    , B.in_event_type
                                    , CAST(B.out_event_type_c AS STRING)
                                    , B.out_event_type
                                    , CAST(B.from_base_class_c AS STRING)
                                    , B.from_base_class
                                    , CAST(B.to_base_class_c AS STRING)
                                    , B.to_base_class
                                    , CAST(B.seq_num_in_enc AS STRING)
                                    , CAST(B.seq_num_in_bed_min AS STRING)
                                    , CAST(B.labor_status_c AS STRING)
                                    , B.first_ip_in_ip_yn
                                    , CAST(B.loa_reason_c AS STRING)
                                    , B.data_source
                                    , CAST(B.effective_time_jittered AS STRING)
                                    , CAST(B.event_time_jittered AS STRING)],""))
WHERE A.anon_id IS NULL 
OR B.anon_id IS NULL


-- ALERT
SELECT
    *
FROM `som-nero-phi-jonc101.shc_core_2021.alert` A
FULL OUTER JOIN `som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021.shc_alert` B
 on FARM_FINGERPRINT(ARRAY_TO_STRING([A.anon_id 
                                    , CAST(A.alt_id_coded AS STRING)
                                    , CAST(A.pat_enc_csn_id_coded AS STRING)
                                    , A.alert_desc
                                    , CAST(A.general_alt_type_c AS STRING)
                                    , A.alt_type    
                                    , A.alt_title
                                    , A.abbr
                                    , CAST(A.med_alert_type_c AS STRING)
                                    , A.med_alt_type
                                    , A.med_alt_title
                                    , A.med_alt_type_abbr
                                    , CAST(A.immun_id AS STRING)
                                    , A.immun_name
                                    , A.immun_abbreviation
                                    , CAST(A.immun_type AS STRING)
                                    , CAST(A.bpa_locator_id AS STRING)
                                    , CAST(A.update_date_jittered AS STRING)],"")) = 
        FARM_FINGERPRINT(ARRAY_TO_STRING([B.anon_id 
                                    , CAST(B.alt_id_coded AS STRING)
                                    , CAST(B.pat_enc_csn_id_coded AS STRING)
                                    , B.alert_desc
                                    , CAST(B.general_alt_type_c AS STRING)
                                    , B.alt_type    
                                    , B.alt_title
                                    , B.abbr
                                    , CAST(B.med_alert_type_c AS STRING)
                                    , B.med_alt_type
                                    , B.med_alt_title
                                    , B.med_alt_type_abbr
                                    , CAST(B.immun_id AS STRING)
                                    , B.immun_name
                                    , B.immun_abbreviation
                                    , CAST(B.immun_type AS STRING)
                                    , CAST(B.bpa_locator_id AS STRING)
                                    , CAST(B.update_date_jittered AS STRING)],""))
WHERE A.anon_id IS NULL 
OR B.anon_id IS NULL


-- culture_sensitivity
SELECT
    *
FROM `som-nero-phi-jonc101.shc_core_2021.culture_sensitivity` A
FULL OUTER JOIN `som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021.shc_culture_sensitivity` B
 on FARM_FINGERPRINT(ARRAY_TO_STRING([A.anon_id
                                        , CAST(A.order_proc_id_coded AS STRING)
                                        , CAST(A.line	AS STRING)
                                        , A.description
                                        , A.sens_organism_sid
                                        , A.organism
                                        , A.organism_quantity
                                        , A.antibiotic		
                                        , A.suscept	
                                        , A.sensitivity_value	
                                        , A.sensitivity_units	
                                        , CAST(A.sens_status_c	AS STRING)	
                                        , A.sens_ref_range		
                                        , CAST(A.ANTIBIO_LNC_ID	AS STRING)	
                                        , A.specimen_source		
                                        , A.specimen_type		
                                        , CAST(A.resulting_lab_id	AS STRING)	
                                        , A.llb_name		
                                        , A.data_source],"")) = 
        FARM_FINGERPRINT(ARRAY_TO_STRING([B.anon_id
                                        , CAST(B.order_proc_id_coded AS STRING)
                                        , CAST(B.line	AS STRING)
                                        , B.description
                                        , B.sens_organism_sid
                                        , B.organism
                                        , B.organism_quantity
                                        , B.antibiotic		
                                        , B.suscept	
                                        , B.sensitivity_value	
                                        , B.sensitivity_units	
                                        , CAST(B.sens_status_c	AS STRING)	
                                        , B.sens_ref_range		
                                        , CAST(B.ANTIBIO_LNC_ID	AS STRING)	
                                        , B.specimen_source		
                                        , B.specimen_type		
                                        , CAST(B.resulting_lab_id	AS STRING)	
                                        , B.llb_name		
                                        , B.data_source],""))
WHERE A.anon_id IS NULL 
OR B.anon_id IS NULL


-- check random records
select *
from `som-nero-phi-jonc101.shc_core_2021.culture_sensitivity` A
where A.anon_id = 'JC557358'
and A.order_proc_id_coded = 576835304
and A.line = 12
```

Double checking myc_msg from shc_core_2021 with the original shc_myc_msg:
```
-- myc_mesg
SELECT
    *
FROM `som-nero-phi-jonc101.shc_core_2021.myc_mesg` A
FULL OUTER JOIN `som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021.shc_myc_mesg` B
on FARM_FINGERPRINT(ARRAY_TO_STRING([A.anon_id
                                    , CAST(A.offset_message_id	AS STRING)		
                                    , CAST(A.offset_parent_message_id	AS STRING)		
                                    , CAST(A.offset_inbasket_msg_id	AS STRING)		
                                    , CAST(A.offset_pat_enc_csn_id	AS STRING)		
                                    , CAST(A.line	AS STRING)		
                                    , A.msg_txt
                                    , A.message_type
                                    , A.to_or_from_pat
                                    , A.subject
                                    , A.routing_department_name
                                    , CAST(A.created_time_jittered	AS STRING)		
                                    , CAST(A.final_handled_time_jittered	AS STRING)],"")) = 
        FARM_FINGERPRINT(ARRAY_TO_STRING([B.anon_id
                                    , CAST(B.offset_message_id	AS STRING)		
                                    , CAST(B.offset_parent_message_id	AS STRING)		
                                    , CAST(B.offset_inbasket_msg_id	AS STRING)		
                                    , CAST(B.offset_pat_enc_csn_id	AS STRING)		
                                    , CAST(B.line	AS STRING)		
                                    , B.msg_txt
                                    , B.message_type
                                    , B.to_or_from_pat
                                    , B.subject
                                    , B.routing_department_name
                                    , CAST(B.created_time_jittered	AS STRING)		
                                    , CAST(B.final_handled_time_jittered	AS STRING)],""))
WHERE A.anon_id IS NULL 
OR B.anon_id IS NULL

-- check random records

-- select a random patient
select *
from `som-nero-phi-jonc101.shc_core_2021.myc_mesg` A 
order by rand()
limit 1

-- select some of the records for that random patient in shc_core_2021.myc_msg (3396032 were selected in the previous step)
select *
from `som-nero-phi-jonc101.shc_core_2021.myc_mesg` A 
where A.anon_id = 'JC1706420'
and A.offset_message_id = 3396032
order by A.line

-- select the same records for the same patient in the original data
select *
from `som-nero-phi-naras-ric.Jon_Chen_data_Oct_2021.shc_myc_mesg` A 
where A.anon_id = 'JC1706420'
and A.offset_message_id = 3396032
order by A.line

-- compare the results: they were the same in this case.

```
