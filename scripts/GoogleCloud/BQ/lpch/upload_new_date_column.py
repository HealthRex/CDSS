from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client()



'''
# TODO(developer): Set table_id to the ID of the table
#                  to add an empty column.
#table_id = "mining-clinical-decisions.lpch.allergy"
table_id = "mining-clinical-decisions.lpch.family_hx"
table = client.get_table(table_id)  # Make an API request.
original_schema = table.schema
new_schema = original_schema[:]  # Creates a copy of the schema.
new_schema.append(bigquery.SchemaField("CONTACT_DATE_JITTERED_UTC", "DATETIME"))
table.schema = new_schema
table = client.update_table(table, ["schema"])  # Make an API request.

if len(table.schema) == len(original_schema) + 1 == len(new_schema):
    print("A new column has been added.")
else:
    print("The column has not been added.")

table_id_lda = "mining-clinical-decisions.lpch.lda"
table_lda = client.get_table(table_id_lda)  # Make an API request.
original_schema_lda = table_lda.schema
new_schema_lda = original_schema_lda[:]  # Creates a copy of the schema.
new_schema_lda.append(bigquery.SchemaField("PLACEMENT_INSTANT_JITTERED_UTC", "DATETIME"))
new_schema_lda.append(bigquery.SchemaField("REMOVAL_INSTANT_JITTERED_UTC", "DATETIME"))
table_lda.schema = new_schema_lda
table_lda = client.update_table(table_lda, ["schema"])  # Make an API request.

if len(table_lda.schema) == len(original_schema_lda) + 2 == len(new_schema_lda):
    print("A new column has been added to LDA")
else:
    print("The column has not been added LDA")

table_id = "mining-clinical-decisions.lpch.treatment_team"
table = client.get_table(table_id)  # Make an API request.
original_schema = table.schema
new_schema = original_schema[:]  # Creates a copy of the schema.
new_schema.append(bigquery.SchemaField("TRTMNT_TM_BEGIN_DT_JITTERED_UTC", "DATETIME"))
new_schema.append(bigquery.SchemaField("TRTMNT_TM_END_DT_JITTERED_UTC", "DATETIME"))
table.schema = new_schema
table = client.update_table(table, ["schema"])  # Make an API request.

if len(table_lda.schema) == len(original_schema_lda) + 2 == len(new_schema_lda):
    print("A new column has been added to treatment_team")
else:
    print("The column has not been added treatment")

'''

table_id = "mining-clinical-decisions.lpch.flowsheets"
table = client.get_table(table_id)  # Make an API request.
original_schema = table.schema
new_schema = original_schema[:]  # Creates a copy of the schema.
new_schema.append(bigquery.SchemaField("RECORDED_TIME_JITTERED_UTC", "DATETIME"))
table.schema = new_schema
table = client.update_table(table, ["schema"])  # Make an API request.

if len(table.schema) == len(original_schema) + 2 == len(new_schema):
    print("A new column has been added to treatment_team")
else:
    print("The column has not been added treatment")
