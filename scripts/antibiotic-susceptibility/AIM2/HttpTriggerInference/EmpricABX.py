import collections
from xml.sax.handler import feature_validation
import pandas as pd
import numpy as np
import os
import xmltodict
import json
import uuid
import requests
from requests.auth import HTTPBasicAuth
from datetime import date, datetime, timedelta, timezone
from dateutil.parser import parse
import xml.etree.ElementTree as ET
from tqdm import tqdm
import pickle
from . import cosmos
import pytz
"""
********** code is not tested here *********
** this is a template for empiric antibiotic model **
"""
class  EmpricABX(object):
    def __init__(
        self,
        modelpath,
        credentials,
        env,
        client_id,
        databricks_endpoint=None,
            ):
        self.credentials = credentials
        self.modelpath = modelpath
        self.client_id = client_id
        with open(modelpath, "rb") as f:
            self.model = pickle.load(f)
        if databricks_endpoint is None:
            self.clf = self.model["model"]
        else:
            self.clf = None
        self.databricks_endpoint = databricks_endpoint
        self.env = env
    def __call__(self, feature_vector=None):
        ABX=['cefoxitin','levofloxacin']
        score_dict={}
        if self.clf is not None:
            model = self.clf
            y_dist = model.pred_dist(feature_vector)
            
        else:
            y_dist = self.get_score_from_databricks()
        
        for abx in ABX:
            task = f"empiric_{abx}"
            score=y_dist[f'label_{task}']
            score_dict[task] = score
        return score_dict
    
    def get_score_from_databricks(self):
        """
        Function to get score from databricks endpoint
        """
        if self.databricks_endpoint is None:
            raise ValueError("databricks_endpoint is not set")
        response = requests.post(
            self.databricks_endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.credentials['password']}",
            },
            json={"data": self.feature_vector},
        )
        if response.status_code != 200:
            raise Exception(
                f"Request to databricks failed with status code {response.status_code}, {response.text}"
            )
        result = response.json()
        return result["predictions"]

        