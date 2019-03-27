[Google Big Query Stroke](https://console.cloud.google.com/bigquery?project=mining-clinical-decisions&j=bq:US:bquxjob_341287ce_16997f447ea&page=queryresults)

## Diagnostic Pathways 




## Emergency Department 

SQL Query 2 <br/>
		- given those people describe them  <br/>
		- look at diagnosis codes (top 5 diagnosis codes)  <br/>
		- demographics <br/>
		- common prescribed 24 hours <br/>
		- top 10 lab tests (lab_result)  <br/>

##
Patient can have multiple diagnoses in one encounter, though one is usally designated "Primary" <br/>


Make Med list looks like specific medications instead of categories <br/>

Looks like you got the top ten lab results, but many of these (sodium, glucose, creatinine, potassium, etc.) come from a single panel order (Basic metabolic panel). <br/>

Go to the Order_Proc table instead to look for most common orders to type laboratory and imaging <br/>

All of the above, mo' better if can report the counts as well as the "baseline" counts (how often that item occurs for any random admission to the hospital) so that you can calculate relative risks / lift / interest /TF-IDF.  <br/>

Consult Song <br/>

## Communicating with Susan Weber to Get Data 

