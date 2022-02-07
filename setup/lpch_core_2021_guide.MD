<h1 style="font-size:60px;">1. Copying tables</h1>

The first step is to simply copy all tables under the database ```som-nero-phi-naras-ric:Jon_Chen_data_Oct_2021``` with the prefix of ```lpch_``` in the table name to the database ```som-nero-phi-jonc101.lpch_core_2021```. Note, the database ```lpch_core_2021``` was created by me and the database ```som-nero-phi-naras-ric:Jon_Chen_data_Oct_2021``` was provided to us by the database admin. 

To copy the tables: 
1) click on the tables name under the Explorer section
2) click on the copy button (the copy button apears on a bar on top right side after clicking on the table and it's next to other buttons QUERY, SHARE, COPY, SNAPSHOT, DELETE, EXPORT)
3) Select the ```som-nero-phi-jonc101``` project in the project name dropbox menue. Select ```lpch_core_2021``` under the dataset name dropbox menue. And write a table name for the coppied table. I used the same name as original table names except I droped the prefix ```lpch_``` in the table names. For example, when copying ```lpch_flowsheet``` I used ```flowsheet``` as the name for the coppied table. Note, there are two tables, ```prov_map``` and ```yn_jon_chen_lpch```, that do not have ```shc``` or ```lpch``` in their name and I coppied thse two tables under both ```shc_core_2021``` and ```lpch_core_2021```.
4) Repeat this process and coppy all lpch tables under ```lpch_core_2021```.

<h1 style="font-size:60px;">1. Re-formating datetime columns</h1>

