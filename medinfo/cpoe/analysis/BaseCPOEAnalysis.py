#!/usr/bin/env python
"""
Base Analysis module to assess results of recommenders / predictors.
"""

import sys, os
import time;
from optparse import OptionParser
from io import StringIO;
from math import sqrt;
from datetime import timedelta;

from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, BaselineFrequencyRecommender, RandomItemRecommender;
from medinfo.cpoe.DataManager import DataManager;
from .Util import log;

# Prepare lookup reference of recommender objects known to be available and facilitate reference by string name
RECOMMENDER_CLASS_LIST = [ItemAssociationRecommender, BaselineFrequencyRecommender, RandomItemRecommender];
RECOMMENDER_CLASS_BY_NAME = dict();
for recClass in RECOMMENDER_CLASS_LIST:
    RECOMMENDER_CLASS_BY_NAME[recClass.__name__] = recClass;

from medinfo.cpoe.Const import AGGREGATOR_OPTIONS;

class AnalysisQuery:
    """Simple struct to pass query parameters
    """
    patientIds = None;  # IDs of the patients to test / analyze against 
    filteredPatientIds = None;  # Generated subset of IDs relevant for testing
    numQueryItems = None;   # Number of orders / items from each patient to use as query items to prime the recommendations
                            #   If set to a float number in (0,1), then treat as a percentage of the patient's total orders / items
    numVerifyItems = None;  # Number of orders / items from each patient after the query items to use to validate recommendations
                            #   If set to a float number in (0,1), then treat as a percentage of the patient's total orders / items
                            #   If left unset (None), then just use all remaining orders / items for that patient
    numRecommendations = None;  # Number of orders / items to recommend for comparison against the verification set
    numRecsByOrderSet = None;   # Alternative option. If set, then figure out number of recommendations on the fly based on which key order was used to trigger the evaluation period

    baseCategoryId = None;  # ID of clinical item category to look for initial items / orders from (probably the ADMIT Dx item).
    baseItemId = None;      # ID of the specific clincial item to look for initial items / orders from
    startDate = None;       # Only use test data occuring after or on this date
    endDate = None;         # Only use test data occuring before this date
    queryTimeSpan = None;   # Time frame specified in seconds over which to look for initial query items 
                            #   (e.g., 24hrs = 86400) after the base item found from the category above.  
                            # Start the time counting from the first item time occuring *after* the category item 
                            #   above since the ADMIT Dx items are often keyed to dates only without times 
                            #   (defaulting to midnight of the date specified).
    verifyTimeSpan = None;  # Time frame specified in seconds over which to look for verify items, starting from the query start time.  Will ignore items that occur within the queryTimeSpan
    
    pastCategoryIds = None; # IDs of clinical item categories where any (past) items should always be included for consideration (e.g., patient demographics)
    
    sequenceItemIdsByVirtualItemId = None;    # Track virtual item IDs to predict (e.g., Readmission) that are based on sequences of explicit items (e.g., Discharge, Admit)
    skipIfOutcomeInQuery = None;    # If set and outcome item in query period, then skip those patients
    byOrderSets = None; # Whether to separate query and verify sets by existing order set use

    preparedPatientItemFile = None; # If specified, will look for source data from a file rather than querying the database

    recommender = None; # Instance of the recommender to test against
    baseRecQuery = None;    # Base Recommender Query to test recommender with.  
                            # Query items and return counts will be customized by analyzer dynamically, but allows specification of static query modifiers (e.g., excluded categories, items, timeDeltaMax)
    
    def __init__(self):
        self.patientIds = set();
        self.filteredPatientIds = None;
        self.numQueryItems = None;
        self.numVerifyItems = None;
        self.numRecommendations = None;
        self.numRecsByOrderSet = False;

        self.baseCategoryId = None;
        self.baseItemId = None;
        self.startDate = None;
        self.endDate = None;
        self.queryTimeSpan = None;
        self.verifyTimeSpan = None;
        self.sequenceItemIdsByVirtualItemId = dict();
        self.skipIfOutcomeInQuery = False;
        self.byOrderSets = False;

        self.preparedPatientItemFile = None;
        
        self.recommender = None;
        self.baseRecQuery = None;

class BaseCPOEAnalysis:
    connFactory = None;

    def __init__(self):
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source
        self.dataManager = DataManager();

    def isItemRecommendable(self, clinicalItemId, queryItemCountById, recQuery, categoryIdByItemId):
        """Decide if the next clinical item could even possibly appear
        in the recommendation list.  (Because if not, no point in trying to
        test recommender against it).
        """
        return ItemAssociationRecommender.isItemRecommendable(clinicalItemId, queryItemCountById, recQuery, categoryIdByItemId);
