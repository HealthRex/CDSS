import scipy.stats as stats
import numpy as np
from statistics import mean
from sklearn.metrics import roc_auc_score, roc_curve, auc

class Util:
    
    def getPrecisionRecall(predicted_items, actual_items, k = 4):
        classPos = len(actual_items)
        classNeg = len(predicted_items) - len(actual_items) 
        predictPos = k 
        predictNeg = len(predicted_items) - k
        TruePos = 0
        FalsePos = 0
        
        for item in predicted_items[:k]:
            if item in actual_items:        
                TruePos += 1 
            else:
                FalsePos += 1
            
        FalseNeg = classPos - TruePos
        TrueNeg = classNeg - FalsePos
        
        precision = TruePos / predictPos 
        recall = TruePos / classPos
        
        return precision, recall
    
    def getAUC(rankedItems, rankedScore, outputItems):
        addLabel = lambda x: 1 if x in outputItems else 0
        itemLabel = list(map(addLabel, rankedItems))
        if sum(itemLabel) > 0:
            auc = roc_auc_score(itemLabel, rankedScore)
        else:
            auc = 0.5
        return auc

    def find_item_name(item_code):
        category = Item.items[item_code].category
        concept_id = Item.items[item_code].concept_id

        (item_code, item_name) = Data.feature_dict[category][concept_id]
        return item_name
    
    def find_item_code_using_name(name):
        import re
        for item_code, item in enumerate(Item.items):
            item_name = Util.find_item_name(item_code).lower()
            match = re.search(r'{}'.format(name), item_name)
            if match:
                print(item_code,'     ',Item.items[item_code].concept_id,'     ', Util.find_item_name(item_code))
    
                    
    def show_summary_stats(recommenderInstance):
        ri = recommenderInstance
        print("------------Data overview -------------")
        print("Patients: {}".format(len(Patient.patients)))
        print("Instances: {}".format(len(Instance.instances)))
        print("Items: {}".format(len(Item.items)))
        print("---------------------------------------")
        print("Training Input items: ", len(ri.trainInputItems))
        print("Candidate items: ", len(ri.trainOutputItems))
        print("---------------------------------------")        
        
        category_count = {}
        for item in Item.items.values():
            if item.category in category_count:
                category_count[item.category] += 1
            else:
                category_count[item.category] = 1
                
        print("category count: {}".format(category_count))
        
        InputItems = []
        OutputItems = []
        for p in R.trainPatients:
                InputItems.append(len(p.itemsPre))
                OutputItems.append(len(p.itemsPost))
            
        print("Avg number of query items: ", np.mean(InputItems))
        print("Median number of query items: ", np.median(InputItems))
        print("Avg number of output items: ", np.mean(OutputItems))
        print("Median number of output items: ", np.median(OutputItems))
        plt.hist(OutputItems, bins= 'auto')
        plt.show()
        
    def cross_validation(method_list, patient_list, fold=10):
        
        patient_nparray = np.asarray(patient_list)

        from sklearn.model_selection import KFold
        kf = KFold(n_splits=fold, random_state=None, shuffle=True)

        resultDF = pd.DataFrame(index = ['precision','recall','auc'], columns=method_list)
        resultDF = resultDF.applymap(lambda x:[])

        for train_index, test_index in kf.split(patient_nparray): 
            train_patient_list = list(patient_nparray[train_index])
            test_patient_list = list(patient_nparray[test_index])
            R_CV = Recommender()
            R_CV.preprocessing()
            R_CV.training(train_patient_list)
            R_CV.testing(method_list = method_list, patient_list = test_patient_list)
            
            for method in method_list:
                
                precision, recall, auc = Util.get_test_results(R_CV, 
                                                               method, 
                                                               test_patient_list, 
                                                               returnMean = False)
                resultDF.loc['precision', method].extend(precision*100)
                resultDF.loc['recall', method].extend(recall*100) 
                resultDF.loc['auc', method].extend(auc)
                
        """paired t-test"""
        for m, method in enumerate(method_list):
            if m == 0: # using first method as reference
                result_A = resultDF.loc[:, method]
                method_A = method
            else:
                result_B = resultDF.loc[:, method]
                method_B = method

                Util.paired_t_test(method_A, result_A, method_B, result_B)
        
        resultDF = resultDF.applymap(lambda x:mean(x))
        return resultDF
    
    def paired_t_test(method_A, result_A, method_B, result_B):
        print("paired t-test for {} and {} :".format(method_A, method_B))
        t_precision, pval_precision = stats.ttest_rel(result_A.precision, result_B.precision)
        t_recall, pval_recall = stats.ttest_rel(result_A.recall, result_B.recall)
        t_auc, pval_auc = stats.ttest_rel(result_A.auc, result_B.auc)
        print("-----------------------------------------------")
        print("precision: ", pval_precision)
        print("recall: ", pval_recall)
        print("auc: ", pval_auc)
        print("-----------------------------------------------")
    
    def get_test_results(recommender_instance, method, patient_list, returnMean = True):
        precision_list = []
        recall_list = []
        auc_list = []
        valid_test = 0
                                                     
        for patient in patient_list:
            if (method, patient) in recommender_instance.patient_results:
                result = recommender_instance.patient_results[(method, patient)]
                precision_list.append(result['precision'])
                recall_list.append(result['recall'])
                auc_list.append(result['auc'])
                valid_test += 1
        
        if valid_test > 0:
            if returnMean:
                return round(mean(precision_list),2), round(mean(recall_list),2), round(mean(auc_list),2)
            else:
                return precision_list, recall_list, auc_list
        else:
            pass
        
    def get_confidence_interval(recommender_instance, method, patient_list):
        
        def confidence_interval(stats):
            alpha = 0.95
            p = ((1.0 - alpha) / 2.0) * 100
            lower = max(0.0, np.percentile(stats, p))
            p = (alpha + (1.0 - alpha)/2.0) * 100
            upper = min(1.0, np.percentile(stats, p))
            return (round(lower,2), round(upper,2))
        
        from sklearn.utils import resample
        precisions = list()
        recalls = list()
        aucs = list()
        n_iteration = 1000
        n_size = int(len(patient_list) * 1)
        
        for i in range(n_iteration):
            patients = resample(patient_list, n_samples = n_size)
            precision, recall, auc = Util.get_test_results(recommender_instance, method, patients)
            precisions.append(precision)
            recalls.append(recall)
            aucs.append(auc)
            
        precision_ci = confidence_interval(precisions)
        recall_ci = confidence_interval(recalls)
        auc_ci = confidence_interval(aucs)
        
        return precision_ci, recall_ci, auc_ci