from google.cloud import bigquery
import pandas as pd
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/conorcorbin/.config/gcloud/application_default_credentials.json' 
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101' 

SQL_SEQUENCE = 

class FeatureGenerator():

	def __init__(self, cohort_table):
		self.cohort_table = cohort_table

	def getSequence(self):
		