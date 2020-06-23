import unittest
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
import numpy as np
import os
from helper import *
from configuration import *

# checks to see if paths have folders
class TestBoxConnection(unittest.TestCase):
    def test_recommender_path(self):
        self.assertTrue(len(os.listdir(recommender_path))> 0)
    def test_physician_grading(self):
        self.assertTrue(len(os.listdir(physician_grading))> 0)
    def test_physician_response(self):
        self.assertTrue(len(os.listdir(physician_response))> 0)
    def test_tracker_path(self):
        self.assertTrue(len(os.listdir(tracker_data)) > 0)

class TestDataConnection(unittest.TestCase):
    def test_sim_user(self):
        self.assertTrue(len(sim_user) > 0)
    def test_sim_patient_order(self):
        self.assertTrue(len(sim_patient_order) > 0)
    def test_sim_state(self):
        self.assertTrue(len(sim_state) > 0)
    def test_sim_user(self):
        self.assertTrue(len(sim_user) > 0)
    def test_clinical_item(self):
        self.assertTrue(len(clinical_item) == 45979)

# TODO
class TestTracker(unittest.TestCase):
    # only checks folders are available
    def check_tracker_path(self):
        self.assertTrue(len(os.listdir(tracker_data))> 0)
        # checks to see if proper folders are in directory
    def check_tracker_data_path(self):
        self.assertTrue('v4_data' in os.listdir(tracker_data))
    def check_tracker_output_path(self):
        self.assertTrue('tracker_output' in os.listdir(tracker_data))

if __name__ == '__main__':
    unittest.main()
