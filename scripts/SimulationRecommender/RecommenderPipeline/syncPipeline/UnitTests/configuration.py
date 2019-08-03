import unittest
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
import numpy as np
import os

# SET PATH TO CLINICAL RECOMMENDER FOLDER
recommender_path = "/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/"
# SET DB CONNECTION
connection = pg.connect("host='localhost' dbname=stride_inpatient_2014 user=postgres password='MANUAL PASSWORD'")


physician_grading = recommender_path + "physician_grading/"
physician_response = recommender_path + "physician_response/"
tracker_data = recommender_path + "tracker_data/"
unit_test = recommender_path + "unit_test/"


clinical_item = pd.read_sql_query('select * from clinical_item', con=connection)
sim_patient_order = pd.read_sql_query('select * from sim_patient_order',con=connection)
sim_patient = pd.read_sql_query('select * from sim_patient',con=connection)
sim_state = pd.read_sql_query('select * from sim_state',con=connection)
sim_user = pd.read_sql_query('select * from sim_user',con=connection)
sim_state_transition = pd.read_sql_query('select * from sim_state_transition',con=connection)

# merge orders from sim patient order and sim_state
merged_order = sim_patient_order.merge(sim_state, left_on='sim_state_id', right_on='sim_state_id')
clinical_items_list = merged_order['clinical_item_id'].unique()
