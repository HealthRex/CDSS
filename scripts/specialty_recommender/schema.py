import json
import math
import datetime
import sys
import getopt
import operator
import random
import re
from dateutil.relativedelta import relativedelta

##Setting up Google sdk environment
import os 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/wip/.config/gcloud/application_default_credentials.json' 
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101' 

##Setting up BQ API
from google.cloud import bigquery
client = bigquery.Client()
project_id = 'som-nero-phi-jonc101'
dataset_id = 'wui_omop_peds'


class Data:
        
    RESOURCE_PATH = ('../resource/')
    def read_BQ(feature_name):
        project_id = 'som-nero-phi-jonc101'
        dataset_id = 'wui_omop_peds'
        prefix = "V3"
        # reading a table from BiqQuery
        table_name = prefix + "_" + feature_name
        print('reading...{}'.format(table_name))
        sql = """ 
            SELECT * FROM 
                `{project_id}.{dataset_id}.{table_id}`
            """.format_map(
                {'project_id':project_id, 
                 'dataset_id':dataset_id, 
                 'table_id':table_name})
        query_job = client.query(sql)
        dataframe = query_job.to_dataframe()
        return dataframe

    def read_JSON(file_name):
        with open(file_name,'r') as fp:
            return json.load(fp)
        
    patientDF = read_BQ('cohort_2014_2020')
    demographicDF = read_BQ('demographic')
    filterItemList = read_BQ('concepts_tofilter')
    
    sameItemMap = read_JSON(RESOURCE_PATH + 'sameItemMap.json')
    itemPrevMap = read_JSON(RESOURCE_PATH + 'baseline_prevalence_map.json') 
    
    outputFeatures = {'measurement','procedure'}
    inputFeatures = {'condition','drug','measurement','procedure'}
    feature_dict = {"age":{},
                    "gender":{},
                    "race":{},
                    "condition":{},
                    "drug":{},
                    "measurement":{},
                    "derived_measurement":{},
                    "procedure":{}}
   
    suffixList = ['CohortPC']
    rrMap = {}
    for cat in inputFeatures:
        for suffix in suffixList:
            rrMap[(cat,suffix)] = read_JSON(RESOURCE_PATH + cat + '_rrMap_' + suffix +'.json')


class Patient:
    counter = 0
    patients = {}

    def __init__(self, row):
        #if  "IndexTime_Exist" not in self.patients[person_id].keys():
        self.person_id = row["person_id"]
        self.primary_visit_id = row["PrimaryCare_visit_id"]
        self.primary_visit_time = row["PrimaryCare_DATETIME"]
        self.specialty_visit_id = row["Specialty_visit_id"]
        self.specialty_visit_time = row["Specialty_DATETIME"]
        self.birthdate = None
        self.gender = None
        self.race = None
        self.age = None
        self.instances = []
        Patient.patients[self.person_id] = self
        Patient.counter += 1
        
    def add_demographics(self, row):
        self.birthdate = row["birth_DATETIME"]
        self.gender = row["gender"]
        self.race = row["race"]
        race_instance = Instance.add_instance(row, 'race')
        gender_instance = Instance.add_instance(row, 'gender')
        Item.addItem(race_instance,'race')
        Item.addItem(gender_instance,'gender')
        
    def add_age(self, row):
        years = relativedelta(self.primary_visit_time, self.birthdate).years 
        months = relativedelta(self.primary_visit_time, self.birthdate).months
        self.age = years * 12 + months
        
        if self.age < 24:
            age_cat = 'infant'
        elif self.age >= 24 and self.age < 144:
            age_cat = 'child'
        elif self.age >= 144:
            age_cat = 'teen'
        age_instance = Instance.add_instance(row, 'age', age_concept = age_cat)
        Item.addItem(age_instance,'age')
        
    def extractItems(self):
        # collect items in pre-post threshold lists
        
        preThreshold = self.primary_visit_time
        postThreshold = self.specialty_visit_id
        self.itemsPre = set()
        self.itemsPost = set()
        
        lookbackWindow = datetime.timedelta(days = 180)
        lookforwardWindow = datetime.timedelta(days = 1)
        
        for i in self.instances:
            instance = Instance.instances[i]
            item_code = instance.item_code 
            item_datetime = instance.item_datetime
            
            # age, race, sex
            if item_datetime == None:
                 self.itemsPre.add(item_code)
            elif (item_datetime >= preThreshold - lookbackWindow) & (item_datetime < preThreshold + lookforwardWindow):
                    self.itemsPre.add(item_code)
            elif instance.visit_id == postThreshold:
                    group_item_code = Item.items[item_code].groupItems()
                    self.itemsPost.add(group_item_code)
                    
        self.itemsPre = Item.processItems(self.itemsPre, mode = "input")
        self.itemsPost = Item.processItems(self.itemsPost, mode = "output") 
        
        return self.itemsPre, self.itemsPost
    
class Item:
    counter = 0
    items = {}
    group_item_map = {}
    
    def __init__(self, item_name, category, item_code, item_concept_id, instances, patients):
        self.name = item_name
        self.category = category 
        self.item_code = item_code
        self.concept_id = item_concept_id
        self.rare = False
        self.filter = False
        self.instances = instances
        self.patients = patients
        self.trainPatients = set()
        self.prevalence = 0
        self.baselinePrevalence = 0
        Item.counter += 1
            
    @classmethod
    def addItem(cls, item_instance, category):

        item_concept_id = item_instance.item_concept_id
        item_name = item_instance.item_name
        person_id = item_instance.person_id
        
        # derived category for high, low, normal lab results
        if item_instance.item_value is not None:
            category = "derived_" + category 
            item_concept_id = item_instance.item_value + "_" + item_concept_id
            item_name = item_instance.item_value + " " + item_name

        if item_concept_id in Data.feature_dict[category]:            
            item_code = Data.feature_dict[category][item_concept_id][0]
            Item.items[item_code].instances.add(Instance.counter)
            Item.items[item_code].patients.add(person_id)
        else:
            item_code = Item.counter
            Data.feature_dict[category][item_concept_id] = (item_code, item_name)
            instances = set([Instance.counter])
            patients = set([person_id])
            Item.items[item_code] = cls(item_name, category, item_code, item_concept_id, instances, patients)
        
        item_instance.item_code = item_code
           
        return item_code
    
    
    @classmethod
    def labelRareItems(cls, patient_count_threshold = 10):
        for item_code in cls.items.keys():
            
            item = cls.items[item_code]
            
            if item.category not in ["gender","race","age"]:
                if len(item.patients) < patient_count_threshold:
                       cls.items[item_code].rare = True
                else:
                       cls.items[item_code].rare = False
    
    @classmethod                    
    def labelFilterItems(cls):
        filterList = list(map(str, Data.filterItemList.concept_id))
        filterList.append('0')
        
        for item_code in cls.items.keys():
            item = cls.items[item_code]
            
            item_concept_id = item.concept_id.replace("high_","").replace("low_","").replace("normal_","")
            
            if item_concept_id == '0':
                cls.items[item_code].filter = True
            
            if item.category not in ["gender","race","age"]:
            
                assert isinstance(item_concept_id, str)
                assert item_concept_id.isdigit(), 'concept ID %r is not all digit' % item_concept_id
                #print(Data.feature_dict[item.category][item_concept_id])

                if item_concept_id in filterList:
                    cls.items[item_code].filter = True
                else: 
                    cls.items[item_code].filter = False
    
    @classmethod  
    def getItemPrevalence(cls):
        for item_code in cls.items.keys():
            item = cls.items[item_code]
            cls.items[item_code].prevalence = len(item.patients)*100/Patient.counter            

    def groupItems(self):
            # group same items using sameItemMap 
            item_category = self.category
            if (self.concept_id in Data.sameItemMap.keys()) and (item_category == 'measurement'):
                new_concept_id = Data.sameItemMap[self.concept_id][0]
                item_code = Data.feature_dict[item_category][new_concept_id][0]
                if item_code not in Item.group_item_map:
                    # store group mapping to calculate prevalence 
                    Item.group_item_map[item_code] = {'item_codes_set': {self.item_code},
                                                      'group_item_patients': 0}
                else:
                    Item.group_item_map[item_code]['item_codes_set'].add(self.item_code)
            else:
                item_code = self.item_code
            return item_code
        
    @classmethod
    def get_group_item_patients(cls):
        # calculate number of patients who have the items grouped
        for group_item_code in cls.group_item_map:
            group_item_patients = set()
            group_item_patients = group_item_patients.union(cls.items[group_item_code].trainPatients)
                   
            for item_code in cls.group_item_map[group_item_code]['item_codes_set']:
                group_item_patients = group_item_patients.union(cls.items[item_code].trainPatients)
            cls.group_item_map[group_item_code]['group_item_patients'] = len(group_item_patients)
    
            
    def getRR_Item(self, mode):
        if mode == 'input':
            tag = 'CohortPC'
        elif mode == 'output':
            tag = 'CohortSC'

        concept_id = re.compile(r'\d+').search(self.concept_id).group(0)
        category = str.replace(self.category,'derived_','')
        
        if concept_id in Data.rrMap[(category, tag)]:
            neglogP, RR = Data.rrMap[(category, tag)][concept_id]
            return neglogP, RR
        else:
            #print(concept_id, ' not found in rrMap ', category, 'with tag: ', tag)
            return 0,0
        
    @staticmethod    
    def processItems(item_codes, mode = "input"):
        
        def filterItems(item_codes):
            filtered_item_codes = set()
            for i in item_codes:
                item = Item.items[i]
                if not (item.rare | item.filter):
                        filtered_item_codes.add(i)
            return filtered_item_codes
          
        
        def outputCategory(item_codes):        
            output_item_codes = set()
            for i in item_codes:
                item = Item.items[i]
                if item.category in Data.outputFeatures:
                    output_item_codes.add(i)
            return output_item_codes
        
        if item_codes:
            processed_item_codes = filterItems(item_codes)
            if mode == "output":
                if processed_item_codes:
                    processed_item_codes = outputCategory(processed_item_codes)
            return processed_item_codes
        else:
            return set()
    
class Instance:
    counter = 0
    instances = []
    def __init__(self, person_id, item_name, item_concept_id, item_datetime, visit_id, item_value):    
        self.count = Instance.counter
        self.person_id = person_id
        self.item_name = item_name
        self.item_code = None
        self.item_concept_id = item_concept_id
        self.item_datetime = item_datetime
        self.visit_id = visit_id
        self.item_value = item_value
        Instance.instances.append(self)
        Instance.counter += 1
        
    @classmethod
    def add_instance(cls, row, feature_category, age_concept = ""):
        person_id = row["person_id"]
        visit_id = None
        item_datetime = None
              
        if feature_category == "age":
            item_concept_id = age_concept
            item_name = age_concept
        else:
            item_concept_id = str(row[feature_category + "_concept_id"])
            
            if feature_category in ["gender","race"]:
                item_name = row[feature_category]
            else:
                item_name = row["concept_name"]
                visit_id = row["visit_id"]
                item_datetime = row[feature_category + "_DATETIME"]
                
        if feature_category == 'measurement':
             item_value = cls.get_item_value(row)
        else:
             item_value = None
                
        Patient.patients[person_id].instances.append(Instance.counter)
        
        return cls(person_id, item_name, item_concept_id, item_datetime, visit_id, item_value)
 
    @staticmethod
    def get_item_value(row):
        def isValid(ref_h, ref_l, v):
            if ref_h and ref_l and v and not (math.isnan(ref_h) or math.isnan(ref_l) or math.isnan(v)):
                return True
            else:
                return False
            
        refRange_high = row["range_high"]
        refRange_low = row["range_low"]
        value = row["value_as_number"]
        if isValid(refRange_high, refRange_low, value):        
                if value >= refRange_low and value <= refRange_high:
                    return "normal"
                elif value > refRange_high:
                    return "high"
                elif value < refRange_low:
                    return "low"
        else:
            return None  