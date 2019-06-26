# gradingRecommenderTests.py
import unittest
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
import numpy as np
import os
from helper import *
from configuration import *

# Create Three Groups
print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('Initializing Data for Test Case 1 ')
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

# Create Groups List
grading_groups = ['abx']

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Meningitis Worsens
clinical_order = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)','Acetaminophen (Oral)', 'Vancomycin (Intravenous)', 'Dexamethasone (Intravenous)', 'DIET NPO']))
case = pd.DataFrame(np.array(['meningitis', 'meningitis','meningitis','meningitis','meningitis']))
name_x =  pd.DataFrame(np.array(['Meningits Worsens','Meningits Worsens','Meningits Worsens','Meningits Worsens','Meningits Worsens']))
grade = pd.DataFrame(np.array([3, 4, 3, 3, 3]))
confidence = pd.DataFrame(np.array([3, 2, 1, 2,3]))
state_dependent = pd.DataFrame(np.array([False, False, False, False, False]))
group_dependent = pd.DataFrame(np.array([True, False, True, False, False ]))
group_x =  pd.DataFrame(np.array(['abx', 'null', 'abx', 'null', 'null']))
m_worsens = pd.concat([clinical_order, case, name_x, grade, confidence, group_x, state_dependent, group_dependent], axis=1, ignore_index = True)

# Meningitis Active
clinical_order = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Acetaminophen (Oral)', 'Vancomycin (Intravenous)', 'Dexamethasone (Intravenous)', 'DIET NPO']))
case = pd.DataFrame(np.array(['meningitis', 'meningitis', 'meningitis', 'meningitis', 'meningitis']))
name_x =  pd.DataFrame(np.array(['Mening Active', 'Mening Active', 'Mening Active', 'Mening Active', 'Mening Active']))
grade = pd.DataFrame(np.array([10, 4, 10, 10, 3]))
confidence = pd.DataFrame(np.array([3, 2, 1, 2, 3]))
state_dependent = pd.DataFrame(np.array([False, False, False, False, False]))
group_dependent = pd.DataFrame(np.array([True, False, True, False, False ]))
group_x =  pd.DataFrame(np.array(['abx', 'null', 'abx', 'null', 'null']))
m_active = pd.concat([clinical_order, case, name_x, grade, confidence, group_x, state_dependent, group_dependent], axis=1, ignore_index = True)

# Meningitis Adequately Treated
clinical_order = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Acetaminophen (Oral)','Vancomycin (Intravenous)', 'Dexamethasone (Intravenous)', 'DIET NPO']))
case = pd.DataFrame(np.array(['meningitis', 'meningitis', 'meningitis', 'meningitis', 'meningitis']))
name_x =  pd.DataFrame(np.array(['Meningitis Adequately Treated','Meningitis Adequately Treated','Meningitis Adequately Treated','Meningitis Adequately Treated','Meningitis Adequately Treated']))
grade = pd.DataFrame(np.array([5, 4, 5, 5, 3]))
confidence = pd.DataFrame(np.array([3, 2, 1, 2, 3]))
state_dependent = pd.DataFrame(np.array([False, False, False, False, False]))
group_dependent = pd.DataFrame(np.array([True, False, True, False, False ]))
group_x =  pd.DataFrame(np.array(['abx', 'null', 'abx', 'null', 'null']))
m_adequately_treated = pd.concat([clinical_order, case, name_x, grade, confidence, group_x, state_dependent, group_dependent], axis=1, ignore_index = True)

# APPENDING THE DATAFRAME TOGETHER
mf2 = m_adequately_treated.append(m_worsens)
mf3 = mf2.append(m_active)
mf3.columns = ['clinical_item_name', 'case', 'sim_state_name', 'score', 'confidence', 'group','state_dependent', 'group_dependent']
meningitis_grading_key_unit1 = mf3

print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('PRINTING MENINGITIS_GRADING_KEY_UNIT_1 ')
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print(meningitis_grading_key_unit1)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Initialize the first test case of one order
#

# Initializing Case Scores:

unit_grade_casex1 = 5
unit_grade_casex2 = 9
unit_grade_casex3 = 17
unit_grade_casex4 = 5
unit_grade_casex5 = 5
unit_grade_casex6 = 5
unit_grade_casex7 = 10
unit_grade_casex8 = 9
unit_grade_casex9 = 10


# TODO

# test basic addition (one order)
# test basic addition (two order)
# test basic addition (five order)


# TODO
clinical_order1 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)']))
clinical_order2 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)','Acetaminophen (Oral)']))
clinical_order3 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Acetaminophen (Oral)', 'Vancomycin (Intravenous)', 'Dexamethasone (Intravenous)', 'DIET NPO']))

# sample cases with len states
case = pd.DataFrame(np.array(['meningitis']))
case2 = pd.DataFrame(np.array(['meningitis', 'meningitis']))
case3 = pd.DataFrame(np.array(['meningitis','meningitis','meningitis','meningitis','meningitis']))

# states
name_x1 =  pd.DataFrame(np.array(['Meningitis Adequately Treated']))
name_x2 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningitis Adequately Treated']))
name_x3 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningitis Adequately Treated', 'Meningitis Adequately Treated', 'Meningitis Adequately Treated', 'Meningitis Adequately Treated']))

# sim user id
sim_user_id1 = pd.DataFrame(np.array(['1']))
sim_user_id2 = pd.DataFrame(np.array(['2','2']))
sim_user_id3 = pd.DataFrame(np.array(['3','3','3','3','3']))


#
caseX1 = pd.concat([clinical_order1, case, name_x1, sim_user_id1], axis=1, ignore_index = True)
caseX2 = pd.concat([clinical_order2, case2, name_x2, sim_user_id2], axis=1, ignore_index = True)
caseX3 = pd.concat([clinical_order3, case3, name_x3, sim_user_id3], axis=1, ignore_index = True)


caseX1.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']
caseX2.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']
caseX3.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']


# TODO

# test group_dependent_action

# TODO

# test state_dependent_action
# test group dependency
# case 4 (two ceftriaxone) (two sim_states)
# case 5 (two ceftriaxone and 1 vancomyocin) (two sim_states)
# case 6 (two ceftriaxone and 2 vancomyocin) (two sim_states)

clinical_order4 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Ceftriaxone (Intravenous)']))
clinical_order5 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Ceftriaxone (Intravenous)', 'Vancomycin (Intravenous)']))
clinical_order6 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Ceftriaxone (Intravenous)', 'Vancomycin (Intravenous)', 'Vancomycin (Intravenous)']))

# sample cases with len states
case4 = pd.DataFrame(np.array(['meningitis', 'meningitis']))
case5 = pd.DataFrame(np.array(['meningitis', 'meningitis', 'meningitis']))
case6 = pd.DataFrame(np.array(['meningitis','meningitis','meningitis','meningitis']))

# states
name_x4 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningits Worsens']))
name_x5 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningits Worsens', 'Meningitis Adequately Treated']))
name_x6 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningitis Adequately Treated', 'Meningitis Adequately Treated', 'Meningitis Adequately Treated']))

# sim user id
sim_user_id4 = pd.DataFrame(np.array(['4', '4']))
sim_user_id5 = pd.DataFrame(np.array(['5', '5', '5']))
sim_user_id6 = pd.DataFrame(np.array(['6','6','6','6']))

caseX4 = pd.concat([clinical_order4, case4, name_x4, sim_user_id4], axis=1, ignore_index = True)
caseX5 = pd.concat([clinical_order5, case5, name_x5, sim_user_id5], axis=1, ignore_index = True)
caseX6 = pd.concat([clinical_order6, case6, name_x6, sim_user_id6], axis=1, ignore_index = True)

caseX4.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']
caseX5.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']
caseX6.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']


# test group dependency
# case 7 (three ceftriaxone)
# case 8 (three ceftriaxone and 1 vancomyocin)
# case 9 (three ceftriaxone and 3 vancomyocin)

clinical_order7 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Ceftriaxone (Intravenous)', 'Ceftriaxone (Intravenous)']))
clinical_order8 = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)','Acetaminophen (Oral)']))
clinical_order9  = pd.DataFrame(np.array(['Ceftriaxone (Intravenous)', 'Ceftriaxone (Intravenous)','Ceftriaxone (Intravenous)', 'Vancomycin (Intravenous)', 'Vancomycin (Intravenous)', 'Vancomycin (Intravenous)']))

# sample cases with len states
case7 = pd.DataFrame(np.array(['meningitis', 'meningitis', 'meningitis']))
case8 = pd.DataFrame(np.array(['meningitis', 'meningitis']))
case9 = pd.DataFrame(np.array(['meningitis','meningitis','meningitis','meningitis','meningitis','meningitis']))

# states
name_x7 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningits Worsens', 'Mening Active']))
name_x8 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningitis Adequately Treated']))
name_x9 =  pd.DataFrame(np.array(['Meningitis Adequately Treated', 'Meningits Worsens', 'Mening Active','Meningitis Adequately Treated', 'Meningits Worsens', 'Mening Active']))

# sim user id
sim_user_id7 = pd.DataFrame(np.array(['7', '7', '7']))
sim_user_id8= pd.DataFrame(np.array(['8', '8']))
sim_user_id9 = pd.DataFrame(np.array(['9','9','9','9','9', '9']))


#
caseX7 = pd.concat([clinical_order7, case7, name_x7, sim_user_id7], axis=1, ignore_index = True)
caseX8 = pd.concat([clinical_order8, case8, name_x8, sim_user_id8], axis=1, ignore_index = True)
caseX9 = pd.concat([clinical_order9, case9, name_x9, sim_user_id9], axis=1, ignore_index = True)


caseX7.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']
caseX8.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']
caseX9.columns = ['clinical_item_name', 'case', 'sim_state_name', 'sim_user_id']



print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print(' RUNNING UNIT TESTS: caseX1, caseX2, caseX3')
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX1')
print(caseX1)
print('--------------------------------------------------------------------------------------------------------------------------------------')


print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX2')
print(caseX2)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')


print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX3')
print(caseX3)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')




print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('RUNNING UNIT TESTS: caseX4, caseX5, caseX6')
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')



print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX4')
print(caseX4)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX5')
print(caseX5)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX6')
print(caseX6)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')



print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print(' RUNNING UNIT TESTS: caseX7, caseX8, caseX9')
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

class TestCaseSet789(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')


print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX7')
print(caseX7)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX8')
print(caseX8)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

print('--------------------------------------------------------------------------------------------------------------------------------------')
print('---------')
print('caseX9')
print(caseX9)
print('---------')
print('--------------------------------------------------------------------------------------------------------------------------------------')

# TODO

class TestCaseSet123(unittest.TestCase):

    def test_123(self):
        self.assertEqual(sim_grader(caseX1, meningitis_grading_key_unit1), unit_grade_casex1)
        self.assertEqual(sim_grader(caseX2, meningitis_grading_key_unit1), unit_grade_casex2)
        self.assertEqual(sim_grader(caseX3, meningitis_grading_key_unit1), unit_grade_casex3)


class TestCaseSet456(unittest.TestCase):

    def test_456(self):
        self.assertEqual(sim_grader(caseX4, meningitis_grading_key_unit1), unit_grade_casex4)
        self.assertEqual(sim_grader(caseX5, meningitis_grading_key_unit1), unit_grade_casex5)
        self.assertEqual(sim_grader(caseX6, meningitis_grading_key_unit1), unit_grade_casex6)


class TestCaseSet789(unittest.TestCase):

    def test_789(self):
        self.assertEqual(sim_grader(caseX7, meningitis_grading_key_unit1), unit_grade_casex7)
        self.assertEqual(sim_grader(caseX8, meningitis_grading_key_unit1), unit_grade_casex8)
        self.assertEqual(sim_grader(caseX9, meningitis_grading_key_unit1), unit_grade_casex9)

if __name__ == '__main__':
    unittest.main()
