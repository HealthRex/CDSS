import csv
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

# TODO need to clean-up and refactor

def createClinicalItemTable():
    conn = pg.connect("host='localhost' dbname=stride_inpatient_2008_2014 user=postgres password='postgres'")

    cur = conn.cursor()

    with open('results-20190518-103636.csv', 'r') as f:
        reader = csv.reader(f)
        cols = next(reader)
        types = ['int', 'int', 'int', 'bigint', 'text', 'text', 'int', 'int', 'int', 'int', 'int', 'int']

        print('creating clinical_item table...')
        cur.execute(generateCreateTableStr('clinical_item', cols, types))

        for row in reader:
            insCmdPre = 'INSERT INTO clinical_item VALUES (' + '\'{}\','*(len(row)-1) + '\'{}\')'
            insCmd = insCmdPre.format(*[a.replace('\'', '\'\'') for a in row]).replace('\'NA\'', 'NULL')
            print('\tinserting ' + str(row), len(row), insCmd)
            cur.execute(insCmd)

    conn.commit()
    conn.close()

def generateCreateTableStr(name, columns, types):
    colTypeList = []
    for i in range(len(columns)):
        if i == 0:
            colTypeList.append(columns[i] + ' ' + types[i] + ' PRIMARY KEY, ')
        else:
            colTypeList.append(columns[i] + ' ' + types[i] + ', ')

    outStr = 'CREATE TABLE {}({})'.format(name, ''.join(colTypeList)[:-2])
    return outStr

'''
headers = ['int64_field_0', 'clinical_item_id', 'clinical_item_category_id', 'external_id', \
           'name', 'description', 'default_recommend', 'item_count', 'patient_count', \
           'encounter_count', 'analysis_status', 'outcome_interest']
types = ['int', 'int', 'int', 'int', 'text', 'text', 'int', 'int', 'int', 'int', 'int', 'int']
print(generateCreateTableStr('clinical_item', headers, types))
'''

createClinicalItemTable()