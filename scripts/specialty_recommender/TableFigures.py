from Util import Util
import pandas as pd
from statistics import mean

class TableFigure:
    def result_table(recommender_instance, method_list):
        
        R = recommender_instance
        df_result = pd.DataFrame(columns = ['precision','precision_ci','recall','recall_ci','auc','auc_ci'], 
                                 index = method_list)

        for method in method_list:
            precision, recall, auc = Util.get_test_results(R, method, R.testPatients, returnMean = False)
            precision_ci, recall_ci, auc_ci = Util.get_confidence_interval(R, method, R.testPatients)
            df_result.loc[method, 'precision'] = precision
            df_result.loc[method, 'recall'] = recall 
            df_result.loc[method, 'auc'] = auc
            df_result.loc[method, 'precision_ci'] = precision_ci
            df_result.loc[method, 'recall_ci'] = recall_ci 
            df_result.loc[method, 'auc_ci'] = auc_ci
        
        """paired t-test"""
        for m, method in enumerate(method_list): 
            if m == 0: # using first method as reference
                result_A = df_result.loc[method,:]
                method_A = method
            else:
                result_B = df_result.loc[method,:]
                method_B = method
                Util.paired_t_test(method_A, result_A, method_B, result_B)
           
        for method in method_list:
            df_result.loc[method, 'precision'] = round(mean(df_result.loc[method, 'precision']),2)
            df_result.loc[method, 'recall'] = round(mean(df_result.loc[method, 'recall']),2)
            df_result.loc[method, 'auc'] = round(mean(df_result.loc[method, 'auc']),2)
        return df_result