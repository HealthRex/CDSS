
#### \dt List of Tables from psql (David M.)  

- backup_link_patient_item
- clinical_item
- clinical_item_association
- clinical_item_category
- clinical_item_link
- collection_type
- data_cache
- item_collection
- item_collection_item
- order_result_stat
- patient_item
- patient_item_collection_link
- sim_note
- sim_note_type
- sim_order_result_map
- sim_patient
- sim_patient_order
- sim_patient_state
- sim_result
- sim_state_result
- sim_state_transition
- sim_user 

### Shell Script to Dump DataTables (Jonathan Chen) 
### Med Box directory 
[STRIDE-Inpatient-2008-2014]("https://stanfordmedicine.app.box.com")


#### Configuring your Database and LocalEnv.py 

 LocalEnv.py is created dynamically by setup.sh, but if you don't need <br />
 to do any of the other steps in setup.sh (e.g. installing libraries, <br />
 initializing DB) it may be easier to just make a copy of this file <br />
 and name it LocalEnv.py before editing the actual values. <br />

 medinfo/db/Env.py imports these DB variables, so all DB connections will <br />
 fail if these two environment variables are not defined. <br />

 Other variables which are likely to vary between dev environments should <br />
 be added to this template file, then be given default values via setup.sh. <br />

BOX_CLIENT_ID = "BOX_API_CLIENT_ID" <br />
BOX_CLIENT_SECRET = "BOX_API_CLIENT_SECRET" <br />
BOX_ACCESS_TOKEN = "BOX_API_ACCESS_TOKEN" <br />
BOX_STRIDE_FOLDER_ID = "BOX_STRIDE_FOLDER_ID" <br />

LOCAL_PROD_DB_PARAM = {}  <br />
LOCAL_PROD_DB_PARAM["HOST"] = 'localhost'  <br />   
LOCAL_PROD_DB_PARAM["DSN"] = 'medinfo'     <br />
LOCAL_PROD_DB_PARAM["UID"] = 'postgres'  <br />
LOCAL_PROD_DB_PARAM["PWD"] = "DB_PASSWORD"   <br />


LOCAL_TEST_DB_PARAM = {}  <br />
LOCAL_TEST_DB_PARAM["HOST"] = 'localhost'  <br />
LOCAL_TEST_DB_PARAM["DSN"] = "DATABASE_NAME"  <br />
LOCAL_TEST_DB_PARAM["UID"] = "DB_UID"  <br />
LOCAL_TEST_DB_PARAM["PWD"] = "DB_PASSWORD"  <br />

PATH_TO_CDSS = "/Users/jonc101/Documents/Biomedical_Data_Science/ui_server/CDSS/"; # Directory where this file is contained in

TEST_RUNNER_VERBOSITY = 2

DATASET_SOURCE_NAME = 'STRIDE'  <br />
DATABASE_CONNECTOR_NAME = "psycopg2"  <br />
SQL_PLACEHOLDER = "%s"  <br />


#### Define constants for connecting to database from which to dump tables. For example, if dumping from local database named test_database and accessing as user test_user, you would use the following lines:
export DB_HOST=localhost <br />
export DB_DSN=database <br />
export DB_USER=user <br />

#### Pipe the uncompressed data from gzip to psql to load to database.
gzip -d -c clinical_item_category.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c clinical_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c clinical_item_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c backup_link_patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c clinical_item_association.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c item_collection.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c collection_type.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c item_collection_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c patient_item_collection_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c order_result_stat.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c data_cache.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
