import os
import sys
import numpy as np
import pandas as pd
#os.chdir('/home/ec2-user/healthrex/CDSS/medinfo/dataconversion')
sys.path.insert(0,'/home/ec2-user/healthrex/CDSS/medinfo/dataconversion')
import FeatureMatrixFactory as fmf
import FeatureMatrix as fm
os.chdir('/home/ec2-user/cs230/scripts/matrix')
import sys, os
import pandas as pd
import psycopg2
from datetime import timedelta
from medinfo.dataconversion import FeatureMatrixFactory as fmf;

def connectToDB():
    '''
    Connects to Database, requires password
    '''

    dsn_database = "medinfo"
    dsn_hostname = "healthrex-db.cwyfvxgvic6c.us-east-1.rds.amazonaws.com"
    dsn_port = "5432"
    dsn_uid = "jonc101"
    dsn_pwd = raw_input("Enter the database password: ")


    try:
        conn_string = "host='"+dsn_hostname+"' port="+dsn_port+" dbname='"+dsn_database+"' user='"+dsn_uid+"' password='"+dsn_pwd+"'"
        print "Connecting to database\n  ->%s" % (conn_string)
        conn=psycopg2.connect(conn_string)
        print "Connected!\n"

    except:
        print "Unable to connect to the database."

    cursor = conn.cursor()
    return cursor

cursor = connectToDB()

# SELECT Drug names
#cursor.execute("""SELECT clinical_item_id, name FROM clinical_item WHERE clinical_item_category_id = 160 and item_count = 0 LIMIT 10""")
cursor.execute("""SELECT DISTINCT(name) FROM clinical_item WHERE clinical_item_category_id = 160""")
drug_names = []
for elem in cursor:
    drug_names.append(elem[0])

# Get total count
cursor.execute("SELECT COUNT(*) FROM patient_item")


total_count = int(cursor.fetchall()[0][0])

batch_size = 10000
num_iterations = total_count/batch_size + 1

for i in range(num_iterations):
    print('Iteration : {}'.format(str(i)))
    offset = 0
    # SELECT Patient IDs
    cursor.execute("SELECT * FROM patient_item LIMIT %s OFFSET %s", (str(batch_size), str(offset)))
    offset += batch_size
    # Initialize FeatureMatrix
    factory = fm.FeatureMatrix(variable = 'hi', num_data_points=100000000, params=None)

    # Add featuress
    factory._factory.setPatientEpisodeInput(cursor)
    factory._factory.processPatientEpisodeInput()
    factory._add_features(index_time_col='item_date')
    
    # SELECT Drug names
    # Create Drug features
    for drug in drug_names:
        factory._factory.addClinicalItemFeatures(clinicalItemNames=[drug])
    factory._factory.buildFeatureMatrix(matrixFileName="test_iteration_{}.txt".format(str(i)))
    data = pd.read_table('test_iteration_{}.txt'.format(str(i)), sep = '\t', header = 2)
    
    # Remove undesired columns
    data2 = data[data.columns.drop(list(data.filter(regex='post.2d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.4d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.7d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.14d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.30d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.90d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.180d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.365d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.730d')))]
    data2 = data2[data2.columns.drop(list(data2.filter(regex='post.1460d')))]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.post')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.min')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.max')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.median')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.mean')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.mean')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.std')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.first')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.last')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.diff')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.slope')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.countInRange')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.proximate')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.firstTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.lastTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.proximateTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.2d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.4d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.14d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.90d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.180d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.365d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.730d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.pre.1460d')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('patient_id')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('patient_item_id')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('external_id')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('clinical_item_id')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('item_date')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.sin')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.cos')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.preTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('analyze_date')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('encounter_id')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('Birth.pre')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('Death.postTimeDays')]
    data2 = data2.loc[:, ~data2.columns.str.endswith('.postTimeDays')]
    
    data2.to_csv('Feature_Iteration_{}.csv'.format(str(i)))

