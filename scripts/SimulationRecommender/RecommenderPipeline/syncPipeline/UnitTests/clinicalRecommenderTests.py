import unittest
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
import numpy as np
import os
from helper import *
from configuration import *

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
class TestPhysicianGrading(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

# TODO
class TestTracker(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
# TODO
class TestDataMerges(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
