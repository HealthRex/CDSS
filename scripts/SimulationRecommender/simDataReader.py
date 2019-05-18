# how to get pandas data from postgree sql using python
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
connection = pg.connect("host='localhost' dbname=stride_inpatient_2014 user=postgres password='CHANGE PW'")

# sim_patient
#sim_patient = pd.read_sql_query('select * from sim_patient',con=connection)
print("|_____________________|")
print("sim_patient")
print("|_____________________|")
#print(sim_patient.head)

#sim_state = pd.read_sql_query('select * from sim_state',con=connection)
print("|_____________________|")
print("sim_state_head")
print("|_____________________|")
#print(sim_state.head)

#sim_state_result = pd.read_sql_query('select * from sim_state',con=connection)
print("|_____________________|")
print("sim_state_result")
print("|_____________________|")
#print(sim_state_result.head)


# sim_state_transition explicitly states the transition from one patient state to the next
# indicates if patient is getting worse or better dependent on state

#sim_state_transition = pd.read_sql_query('select * from sim_state_transition',con=connection)
#print(sim_state_transition)

# todo (check sql query)

sql =       '''
            select
                a.sim_patient_order_id, a.sim_user_id, a.sim_state_id, a.relative_time_start, a.sim_state_id,
                b.description as clin_description,
                c.description as state_description
            from
                sim_patient_order as a,
                clinical_item as b,
                sim_state_transition as c
            where a.clinical_item_id = c.clinical_item_id
            and b.clinical_item_id = b.clinical_item_id



            '''


# need to join clinical_item table with clinical description and clinical item

sim_patient_order = pd.read_sql_query('select * from sim_patient_order',con=connection)
#print(sim_patient_order)

grouped_sim_user = sim_patient_order.groupby("sim_user_id")
#grouped_sim_order = sim_patient_order.groupby("")
#print(grouped_sim_user.groups)

# running way too slowly
# test = pd.read_sql_query(sql, con = connection)
#print(test.head)
