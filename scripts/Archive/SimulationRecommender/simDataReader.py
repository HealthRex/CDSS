
# how to get pandas data from postgree sql using python
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
connection = pg.connect("host='localhost' dbname=stride_inpatient_2014 user=postgres password='MANUAL PASSWORD'")

# -------------------------------------------------------------------------------
# to do :
#         Feature: Generate Grading Scheme
#             1) help visualize processes
#             2) introduce best grading schemes for each case
#             3) create a list of common errors seen
#
#             4) clean up exploratory analysis
#             5) convert to python module
#
#
#
# ---------------------------------------------------------------------------------

clinical_item = pd.read_sql_query('select * from clinical_item',con=connection)
print("|_____________________|")
print("clinical_item")
print("|_____________________|")
#print(sim_patient.head)

sim_patient_order = pd.read_sql_query('select * from sim_patient_order',con=connection)
print("|_____________________|")
print("sim_patient_order")
print("|_____________________|")
#print(sim_patient.head)

sim_state = pd.read_sql_query('select * from sim_state',con=connection)
print("|_____________________|")
print("sim_state_head")
print("|_____________________|")
#print(sim_state.head)
#


sim_user = pd.read_sql_query('select * from sim_user',con=connection)
print("|_____________________|")
print("sim_user")
print("|_____________________|")
#print(sim_patient.head)


sim_state_transition = pd.read_sql_query('select * from sim_state_transition',con=connection)
print("|_____________________|")
print("sim_state_transition")
print("|_____________________|")
#print(sim_state_result.head)

'''

merge sim_patient_order and sim_state by sim_state_id

'''
print("merging sim state and transition")
merged_order = sim_patient_order.merge(sim_state, left_on='sim_state_id', right_on='sim_state_id')
#print(merged_order)

'''

find unique clinical items from merged_order

'''

print("running clinical items unique")
clinical_items_list = merged_order['clinical_item_id'].unique()
#print(clinical_items_list)

# finds unique sim_state_id's
# RCODE:
#   sim_state_list <- unique(merged_order$sim_state_id)
# Python:
sim_state_list = merged_order['sim_state_id'].unique()

# creates clinical_item order key to reduce merge space:
# RCode: ordered_clinical_item_table <- clinical_item %>% filter(clinical_item_id %in% clinical_items_list)
ordered_clinical_item_table = clinical_item[clinical_item['clinical_item_id'].isin(clinical_items_list)]
#print(ordered_clinical_item_table)

remerged_order = merged_order.merge(ordered_clinical_item_table, left_on='clinical_item_id', right_on='clinical_item_id')

# https://medium.com/analytics-vidhya/split-apply-combine-strategy-for-data-mining-4fd6e2a0cc99
split_state = remerged_order.groupby('sim_state_id')
# print(list(split_state))

#--------------------------------------------------------------------------------
# afib
#--------------------------------------------------------------------------------
# "Afib-RVR Initial"
# "Afib-RVR Stabilized"
# "Afib-RVR Worse"
#--------------------------------------------------------------------------------
afib_states = ["Afib-RVR Initial",
                "Afib-RVR Stabilized" ,
                "Afib-RVR Worse" ]
#--------------------------------------------------------------------------------
# meningitis
#--------------------------------------------------------------------------------
# "Mening Active"
# "Meningitis Adequately Treated"
# "Meningits Worsens"
#--------------------------------------------------------------------------------
mening_states =  ["Mening Active",
                   "Meningitis Adequately Treated",
                   "Meningits Worsens"]
# -------------------------------------------------------------------------------
# pulmonary embolism
# -------------------------------------------------------------------------------
# "PE-COPD-LungCA"
# "PE-COPD-LungCA + Anticoagulation"
# "PE-COPD-LungCA + O2"
# "PE-COPD-LungCA + O2 + Anticoagulation"
# -------------------------------------------------------------------------------
pulmonary_emolism_states = ["PE-COPD-LungCA",
                              "PE-COPD-LungCA + Anticoagulation",
                              "PE-COPD-LungCA + O2",
                              "PE-COPD-LungCA + O2 + Anticoagulation"]
# -------------------------------------------------------------------------------
# neutropenic fever
# -------------------------------------------------------------------------------
#  "Neutropenic Fever Treated with IVF"
#  "Neutropenic Fever Treated with IVF + ABX"
#  "Neutropenic Fever v2"
#  "NFever"
# -------------------------------------------------------------------------------

neutropenic_fever_states = ["Neutropenic Fever Treated with IVF",
                              "Neutropenic Fever Treated with IVF + ABX",
                              "Neutropenic Fever v2"]

# -------------------------------------------------------------------------------
# GIBLEED
# -------------------------------------------------------------------------------
# "EtOH-GIBleed Active"
# "EtOH-GIBleed Bleeding Out"
# "EtOH-GIBleed Coag Stabilized"
# "EtOH-GIBleed Post-EGD"
# -------------------------------------------------------------------------------

gi_bleed_states = ["EtOH-GIBleed Active",
                      "EtOH-GIBleed Bleeding Out",
                      "EtOH-GIBleed Coag Stabilized",
                      "EtOH-GIBleed Post-EGD" ]

# -------------------------------------------------------------------------------
# DKA
# -------------------------------------------------------------------------------
# "DKA Euglycemic"
# "DKA Hyperglycemic"
# "DKA Onset"
# -------------------------------------------------------------------------------

dka_states = ["DKA Euglycemic" ,
                "DKA Hyperglycemic" ,
                "DKA Onset"]

list_of_states = [gi_bleed_states,
                       mening_states,
                       pulmonary_emolism_states,
                       afib_states,
                       neutropenic_fever_states]
print("LIST OF STATES")
#print(list_of_states[1])


def state_split(state_names, df):
    df2 = df[df['name_x'].isin(state_names)]
    return(df2)


print(list(remerged_order.columns))


gi_test = state_split(gi_bleed_states, remerged_order)
mening_test = state_split(mening_states, remerged_order)
pulmonary_embolism_test = state_split(pulmonary_emolism_states, remerged_order)
afib_test = state_split(afib_states, remerged_order)
neutropenic_test = state_split(neutropenic_fever_states, remerged_order)

gi_test['case'] = "gi_bleed"
mening_test['case'] = "meningitis"
pulmonary_embolism_test['case'] = "pulmonary_embolism"
afib_test['case'] = "atrial_fibrillation"
neutropenic_test['case'] = "neutropenic"
print(neutropenic_test['case'])

df_grading_pre = pd.concat([gi_test,
                        mening_test,
                        pulmonary_embolism_test,
                        afib_test,
                        neutropenic_test])


df_grading = pd.DataFrame(df_grading_pre[['sim_state_id',
                                        'clinical_item_id',
                                        'sim_user_id',
                                        'sim_patient_id',
                                        'name_x',
                                        'description_x',
                                        'description_y',
                                        'case']])


print(df_grading)

#sim_state_list = list(df_grading.groupby('sim_state_name'))

#print('sim_state_list')
#print(sim_state_list)
