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


sim_patient = pd.read_sql_query('select * from sim_patient',con=connection)
print("|_____________________|")
print("sim_patient")
print("|_____________________|")
#print(sim_patient.head)

sim_state = pd.read_sql_query('select * from sim_state',con=connection)
print("|_____________________|")
print("sim_state_head")
print("|_____________________|")
#print(sim_state.head)
#

sim_state_result = pd.read_sql_query('select * from sim_state',con=connection)
print("|_____________________|")
print("sim_state_result")
print("|_____________________|")
#print(sim_state_result.head)


# sim_state_transition explicitly states the transition from one patient state to the next
# indicates if patient is getting worse or better dependent on state

#sim_state_transition = pd.read_sql_query('select * from sim_state_transition',con=connection)
#print(sim_state_transition)

# python merge data frames(https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html)
# df1.merge(df2, left_on='lkey', right_on='rkey')

# getting unique values in python
# https://pandas.pydata.org/pandas-docs/version/0.23.4/generated/pandas.unique.html

# pd.unique(Series(pd.Categorical(list('baabc'))))
# gapminder_2002 = gapminder[is_2002]
# chaining
# gapminder_2002 = gapminder[gapminder.year == 2002]

# create keys to split
# sort the dataframe

'''
#create some data with Names column
data = pd.DataFrame({'Names': ['Joe', 'John', 'Jasper', 'Jez'] *4, 'Ob1' : np.random.rand(16), 'Ob2' : np.random.rand(16)})

#create unique list of names
UniqueNames = data.Names.unique()

#create a data frame dictionary to store your data frames
DataFrameDict = {elem : pd.DataFrame for elem in UniqueNames}

for key in DataFrameDict.keys():
    DataFrameDict[key] = data[:][data.Names == key]


df = pd.DataFrame({'Name':list('aabbef'),
                   'A':[4,5,4,5,5,4],
                   'B':[7,8,9,4,2,3],
                   'C':[1,3,5,7,1,0]}, columns = ['Name','A','B','C'])

print (df)
  Name  A  B  C
0    a  4  7  1
1    a  5  8  3
2    b  4  9  5
3    b  5  4  7
4    e  5  2  1
5    f  4  3  0

d = dict(tuple(df.groupby('Name')))
print (d)
{'b':   Name  A  B  C
2    b  4  9  5
3    b  5  4  7, 'e':   Name  A  B  C
4    e  5  2  1, 'a':   Name  A  B  C
0    a  4  7  1
1    a  5  8  3, 'f':   Name  A  B  C
5    f  4  3  0}

print (d['a'])
  Name  A  B  C
0    a  4  7  1
1    a  5  8  3

'''


'''



# finds unique clinical item list
clinical_items_list <- unique(merged_order$clinical_item_id)

# finds unique sim_state_id's
sim_state_list <- unique(merged_order$sim_state_id)

# creates clinical_item order key to reduce merge space:
ordered_clinical_item_table <- clinical_item %>% filter(clinical_item_id %in% clinical_items_list)

# joins tables by clinical item id (creates a dataframe that includes clinical descriptions)
remerged_order <- merge(merged_order, ordered_clinical_item_table,
                        by.x="clinical_item_id",
                        by.y="clinical_item_id")

#
split_state <- split(remerged_order, remerged_order$sim_state_id)

#
split_user_state <- split(split_state$`5000`, split_state$`5000`$sim_user_id)

sort(unique(remerged_order$name.x))

#--------------------------------------------------------------------------------
# afib
#--------------------------------------------------------------------------------
# "Afib-RVR Initial"
# "Afib-RVR Stabilized"
# "Afib-RVR Worse"
#--------------------------------------------------------------------------------

afib_states <- c("Afib-RVR Initial",
                "Afib-RVR Stabilized" ,
                "Afib-RVR Worse" )

#--------------------------------------------------------------------------------
# meningitis
#--------------------------------------------------------------------------------
# "Mening Active"
# "Meningitis Adequately Treated"
# "Meningits Worsens"
#--------------------------------------------------------------------------------

mening_states <- c( "Mening Active",
                   "Meningitis Adequately Treated",
                   "Meningits Worsens")

# -------------------------------------------------------------------------------
# pulmonary embolism
# -------------------------------------------------------------------------------
# "PE-COPD-LungCA"
# "PE-COPD-LungCA + Anticoagulation"
# "PE-COPD-LungCA + O2"
# "PE-COPD-LungCA + O2 + Anticoagulation"
# -------------------------------------------------------------------------------

pulmonary_emolism_states <- c( "PE-COPD-LungCA",
                              "PE-COPD-LungCA + Anticoagulation",
                              "PE-COPD-LungCA + O2",
                              "PE-COPD-LungCA + O2 + Anticoagulation")


# -------------------------------------------------------------------------------
# neutropenic fever
# -------------------------------------------------------------------------------
#  "Neutropenic Fever Treated with IVF"
#  "Neutropenic Fever Treated with IVF + ABX"
#  "Neutropenic Fever v2"
#  "NFever"
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# GIBLEED
# -------------------------------------------------------------------------------
# "EtOH-GIBleed Active"
# "EtOH-GIBleed Bleeding Out"
# "EtOH-GIBleed Coag Stabilized"
# "EtOH-GIBleed Post-EGD"
# -------------------------------------------------------------------------------


s# -------------------------------------------------------------------------------
# DKA
# -------------------------------------------------------------------------------
# "DKA Euglycemic"
# "DKA Hyperglycemic"
# "DKA Onset"
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# Meningitis
# -------------------------------------------------------------------------------
# "Mening Active"
# "Meningitis Adequately Treated"
# "Meningits Worsens"
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# Neutropenic Fever
# -------------------------------------------------------------------------------
# "Neutropenic Fever Treated with IVF"
# "Neutropenic Fever Treated with IVF + ABX"
# "Neutropenic Fever v2"
# "NFever"
# -------------------------------------------------------------------------------



afib_df <- remerged_order %>% filter(name.x %in% afib_state)
afib_split <- split(afib_df, afib_df$sim_state_id)

# function to find unique orders for each sim state

afib.40 <- afib_split$`40` %>% select(sim_state_id, clinical_item_id, sim_user_id, sim_patient_id, description.x, name.x, description.x, description.y)
afib.41 <- afib_split$`41` %>% select(sim_state_id, clinical_item_id, sim_user_id, sim_patient_id, description.x, name.x, description.x, description.y)
afib.43 <- afib_split$`43` %>% select(sim_state_id, clinical_item_id, sim_user_id, sim_patient_id, description.x, name.x, description.x, description.y)

unique_orders_afib_40 <- unique(afib.40$description.y)
unique_orders_afib_41 <- unique(afib.41$description.y)
unique_orders_afib_43 <- unique(afib.43$description.y)

total_order_list <- unique(c(unique_orders_afib_40,
                          unique_orders_afib_41,
                          unique_orders_afib_43))





library(xlsx)
write.xlsx(total_order_list, "afib_grading_doctors.xlsx", sheetName = "afib_case_orders",
           col.names = TRUE, row.names = TRUE, append = FALSE)

write.xlsx(unique_orders_afib_40, "afib_grading_doctors.xlsx", sheetName = "afib_initial",
           col.names = TRUE, row.names = TRUE, append = TRUE)

write.xlsx(unique_orders_afib_41, "afib_grading_doctors.xlsx", sheetName = "afib_stabilized",
           col.names = TRUE, row.names = TRUE, append = TRUE)

write.xlsx(unique_orders_afib_43, "afib_grading_doctors.xlsx", sheetName = "afib_worsened",
           col.names = TRUE, row.names = TRUE, append = TRUE)
'''
