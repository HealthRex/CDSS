import os
import sys
import time
import numpy as np
import pandas as pd
from backports import tempfile
from multiprocessing import Pool
os.chdir('/home/ec2-user/healthrex/CDSS/medinfo/dataconversion')
from medinfo.dataconversion import FeatureMatrixFactory as fmf
from medinfo.dataconversion import FeatureMatrix as fm
os.chdir('/home/ec2-user/cs230/scripts/matrix/icu2')
import psycopg2
from datetime import timedelta

# Code to connect to database:

dsn_pwd = raw_input("Enter the database password: ")
def connectToDB(dsn_pwd):
    '''
    Connects to Database, requires password
    '''

    dsn_database = "medinfo"
    dsn_hostname = "healthrex-db.cwyfvxgvic6c.us-east-1.rds.amazonaws.com"
    dsn_port = "5432"
    dsn_uid = "jonc101"


    try:
        conn_string = "host='"+dsn_hostname+"' port="+dsn_port+" dbname='"+dsn_database+"' user='"+dsn_uid+"' password='"+dsn_pwd+"'"
        print "Connecting to database\n  ->%s" % (conn_string)
        conn=psycopg2.connect(conn_string)
        print "Connected!\n"

    except:
        print "Unable to connect to the database."

    cursor = conn.cursor()
    return cursor

cursor = connectToDB(dsn_pwd) # Establish the connection to the database


# Select clinical items we want to pre-process
cursor.execute("""SELECT DISTINCT(name) FROM clinical_item WHERE analysis_status = 1""")
clinical_item_names = []
for elem in cursor:
    clinical_item_names.append(elem[0])

# Get total count of all the patient items we want
cursor.execute("SELECT COUNT(*) FROM patient_item where NOT (encounter_id IS NULL)")
total_count = int(cursor.fetchall()[0][0])

# Query in batches of batch_size
batch_size = 100000
num_iterations = total_count/batch_size + 1
outputdir = os.getcwd()

# The query and pre-processing for each batch
def queryItems(i):
    global batch_size
    global clinical_item_names
    global dsn_pwd
    global outputdir
    start_time = time.time()
    offset = batch_size*i
    print('Iteration : {} (Batch size: {}; Offset: {})'.format(str(i), str(batch_size), str(offset)))

    data = None
    with tempfile.TemporaryDirectory() as path:
        os.chdir(path)
        cursor = connectToDB(dsn_pwd)
        cursor.execute("SELECT * from patient_item where NOT (encounter_id IS NULL) order by encounter_id DESC LIMIT %s OFFSET %s", (str(batch_size), str(offset)))

        # Initialize FeatureMatrix
        factory = fm.FeatureMatrix(variable = 'hi', num_data_points=100000000, params=None)

        # Add features
        factory._factory.setPatientEpisodeInput(cursor)
        factory._factory.processPatientEpisodeInput()
        factory._add_features(index_time_col='item_date')
        factory._factory.addClinicalItemFeatures(['Death'], dayBins=[1,7,30], features="post")

        # Add relevant clinical item features
        for item in clinical_item_names:
            print(item)
            factory._factory.addClinicalItemFeatures(clinicalItemNames=[item], dayBins=[1,7,30], features="all")

        # Output the feature matrix for this iteration
        factory._factory.buildFeatureMatrix(matrixFileName=outputdir+"/FINAL_iteration_{}.txt".format(str(i)))
    end_time = time.time()
    
    print('Completed Iteration : {} in time : {}'.format(str(i), str(end_time-start_time)))
    return 0

# Do multiprocessing of the batches

pool = Pool(14)
iterations = range(0, num_iterations)
pool.map(queryItems, iterations, chunksize=1)

