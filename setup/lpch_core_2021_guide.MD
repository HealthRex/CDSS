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
 And saved the results in ```adt_code``` under ```lpch_core_2021``` by setting up the query result destination settings before I run the above query: More>Query Settings>Set a destination table for query results. Note I use the same table name as the original table and I select the overwrite option. NOTE: be careful to do not overwrite the original original tables from the database admin under ``` som-nero-phi-naras-ric:Jon_Chen_data_Oct_2021```.  
