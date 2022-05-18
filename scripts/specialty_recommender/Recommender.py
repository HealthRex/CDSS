import numpy as np
import pandas as pd
from Util import Util

class Recommender:

    def __init__(self, Item, Data):
        self.Item = Item
        self.Data = Data
        self.coMatrix = np.zeros((self.Item.counter,self.Item.counter))
        self.trainInputItems = set()
        self.trainOutputItems = set()
        self.trainPatients = []
        self.testPatients = []
        self.invalidPatients = []
        self.patient_results = {}
        
        
    def trainSplitbyYear(self, patients, year):
        for patient in patients:
            if patient.primary_visit_time.year >= year:
                self.testPatients.append(patient) 
            else:
                self.trainPatients.append(patient)
        print("train patients = {}".format(len(self.trainPatients)))
        print("test patients = {}".format(len(self.testPatients)))
            
        
    def buildCoMatrix(self, itemsPre, itemsPost): 
        # itemsPre and itemsPost are set
        
        for i in itemsPre:
            for j in itemsPost:
                self.coMatrix[i][j] += 1
            
    def buildTrainingItems(self, itemsPre, itemsPost, patient):
        self.trainInputItems = self.trainInputItems.union(itemsPre)
        self.trainOutputItems = self.trainOutputItems.union(itemsPost)
        trainingitems = itemsPre.union(itemsPost)
        if trainingitems:
            for i in trainingitems:
                self.Item.items[i].trainPatients.add(patient)  
                
    
    def preprocessing(self):
        print("preprocessing...")
        self.Item.getItemPrevalence()
        self.Item.labelRareItems()
        self.Item.labelFilterItems()
        
        
    
    def training(self, patient_list):
        print("building co-occurence matrix ...")
        for patient in patient_list:
            itemsPre, itemsPost = patient.extractItems()
            self.buildCoMatrix(itemsPre, itemsPost)
            self.buildTrainingItems(itemsPre, itemsPost, patient)
        self.Item.get_group_item_patients()
       
    
    def testing(self, method_list, patient_list, k = 4):
        
        for method in method_list:

            print("testing method: {}".format(method))
        
            for patient in patient_list:
                itemsPre, itemsPost = patient.extractItems()
                inputItems = list(set(itemsPre))
                outputItems = list(set(itemsPost))
                    
                if len(outputItems) != 0 and len(inputItems)!=0:
                
                    rankedItems, rankedScore = self.rankingItems(inputItems, method)
                
                    precision, recall = Util.getPrecisionRecall(rankedItems, outputItems, k = k)
                    auc = Util.getAUC(rankedItems, rankedScore, outputItems)
                    
                    self.patient_results[(method, patient)] = {'precision':precision, 
                                                                'recall': recall,
                                                                'auc': auc}
                
        
    def rankingItems(self, inputItems, method):
        # possible candidate Items
        candidateItems = np.array(list(self.trainOutputItems))
        queryItems = np.array(list(self.trainInputItems.intersection(inputItems)))
        
        score = self.aggStats(candidateItems, queryItems, method)
        # sort based on rankedScore
        sortedIndex = score.argsort()[::-1]
        rankedItems = candidateItems[sortedIndex].tolist()
        rankedScore = score[sortedIndex].tolist()
        return rankedItems, rankedScore
    
    def aggStats(self, candidateItems, queryItems, method):
        
        # this apply statMetrics over queryItems
        getStats = np.vectorize(self.statMetrics) 
                
        def PPV(item):
            sumStats = sum(getStats(item, queryItems, 'ppv'))
            sumN = sum(getStats(item, queryItems, 'numA_pts'))
            return sumStats/sumN
        
        def PPV_mod(item):
            sumStats = sum(getStats(item, queryItems, 'ppv_mod'))
            sumN = sum(getStats(item, queryItems, 'numA_pts'))
            return sumStats/sumN

        def PPV_wt(item):
            sumStats = sum(getStats(item, queryItems, 'ppv_wt'))
            sumN = sum(getStats(item, queryItems, 'numA_pts'))
            return sumStats/sumN
        
        def PPV_mod_wt(item):
            sumStats = sum(getStats(item, queryItems, 'ppv_mod_wt'))
            sumN = sum(getStats(item, queryItems, 'numA_pts'))
            return sumStats/sumN
        
        def RR(item):
            prodStats = np.prod(getStats(item, queryItems, 'rr'))
            return prodStats
        
        def Prevalence(item_code):
            return self.statMetrics(item_code, item_code, 'prevalence')
        
        def BaselinePrevalence(item_code):
            item_concept_id = self.Item.items[item_code].concept_id
            if item_concept_id != '0':
                return self.Data.itemPrevMap[item_concept_id]
            else:
                return 0
        
        def Random(item):
            return np.random.random_sample()
                      
        switcher = {                   
                    'PPV':PPV,
                    'PPV_WT':PPV_wt,
                    'PPV_MOD':PPV_mod,
                    'PPV_MOD_WT':PPV_mod_wt,
                    'RR':RR,
                    'PREVALENCE':Prevalence,
                    'BASELINEPREVALENCE':BaselinePrevalence,
                    'RANDOM':Random
                    }
    
        applyMethod = switcher.get(method.upper())          
        score = np.vectorize(applyMethod)(candidateItems)
        return score 
    
    
    def statMetrics(self, itemB, itemA, metric):
        # item B is the candidate item
        # item A is the query item
        AB_pts = self.coMatrix[itemA][itemB]
        A_pts = len(self.Item.items[itemA].trainPatients)
        N = len(self.trainPatients)
        if itemB in self.Item.group_item_map:
            B_pts = self.Item.group_item_map[itemB]['group_item_patients']
        else:
            B_pts = len(self.Item.items[itemB].trainPatients)
            

        def modifier(itemA, itemB):
            modifierA = 1
            modifierB = 1
            itemA_category = self.Item.items[itemA].category
            itemA_category = str.replace(itemA_category,'derived_','')
            itemB_category = self.Item.items[itemB].category
            itemB_category = str.replace(itemB_category,'derived_','')
            
            if itemA_category in self.Data.inputFeatures:
                neglogP, rr = self.Item.items[itemA].getRR_Item(mode = 'input')
                modifierA = rr
            return modifierA, modifierB
        
        modifierA,modifierB = modifier(itemA, itemB)
        
        def numA_pts():
            return A_pts
        def prevalence():
            return B_pts*100/N
        def PPV():
            return AB_pts
        def PPV_wt():
            return AB_pts/A_pts
        def PPV_mod():
            return modifierA * AB_pts 
        def PPV_mod_wt():
            return (modifierA * AB_pts) / A_pts
        def RR():
            if B_pts == AB_pts:
                adj = 0.5
            else:
                adj = 0
            return (AB_pts/A_pts) / ((B_pts - AB_pts + adj)/(N - A_pts + adj))
        
        switcher = {
                'numA_pts': numA_pts,
                'prevalence': prevalence,
                'ppv': PPV,
                'ppv_wt':PPV_wt,
                'ppv_mod': PPV_mod,
                'ppv_mod_wt':PPV_mod_wt,
                'rr': RR,
                }
    
        func = switcher.get(metric, lambda: 'invalid')    
        
        return func()
    
    def topItemsGivenQuery(self, query_item_codes, n=10, method = 'PPV_mod_wt', RR_threshold = 0):
    
        queryItemNames = list(map(Util.find_item_name, query_item_codes))
        print("clinical items for query: {}".format(queryItemNames))
    
        rankedItems, rankScore = self.rankingItems(set(query_item_codes), method)
    
        df = pd.DataFrame(rankedItems[:n+40], columns=["Item"])
        df["Name"] = df["Item"].map(Util.find_item_name)
    
        formatFunc1 = lambda x:round(x*100,1)
        formatFunc2 = lambda x:round(x,1)
    
        methodMap = {'ppv': ('ppv', formatFunc1),
                     'rr': ('RR',formatFunc2),
                     'prevalence':('prevalence',formatFunc2),
                     'baseline_prevalence':('baselineprevalence',formatFunc2)}
        
        metrics = ["PPV","RR","Prevalence","Baseline_Prevalence"]
        for m in metrics:
            method = m.lower()
            df[m] = df["Item"].apply(self.aggStats, args = (query_item_codes, methodMap[method][0]))
            df[m] = df[m].apply(methodMap[method][1])
    
        
        df = df[df["RR"] >= RR_threshold][:n]
        return df