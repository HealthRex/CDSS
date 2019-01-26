

import LocalEnv
import os
from medinfo.ml import SupervisedLearner as SL
from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS
import pandas as pd
pd.set_option('display.width', 3000)
pd.set_option('display.max_columns', 3000)

from medinfo.ml.FeatureSelector import FeatureSelector

from sklearn.externals import joblib

import ml_utils


outcome_label = 'all_components_normal'

info_features = ['pat_id', 'order_proc_id', 'proc_code', 'order_time']
leak_features = ['abnormal_panel', 'num_components', 'num_normal_components']

non_impute_features = info_features + leak_features + [outcome_label]

features_dict = {
    'non_impute_features':non_impute_features,
    'outcome_label':outcome_label,
    'info_features':info_features,
    'leak_features':leak_features
}


# TODO: Write test to make sure:
# 1.worked on all previous use cases
# 2.while writing tests you might find one of the few uses causes a bug
# 3.writing tests to be faster but more involved than the coding itself. The tests should test the intention.
# 4.The ones that do important business logic, thats where the testing is important. Test the requirements.
# 5.Keep your tests small: one test per requirement.

def main_pipelining(labs,
                    data_source = 'Stanford',
                    lab_type = 'panel',
                    num_episodes = 10000,
                    random_state=123456789):
    '''
    Fresh new pipeline.
    :return:
    '''

    from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS


    '''
    Folder organization
    '''
    project_folderpath = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/')
    project_ml_folderpath = os.path.join(project_folderpath, 'machine_learning')

    data_set_foldername = 'data-%s-%s-%s-episodes'%(data_source, lab_type, num_episodes) # TODO: template shared by stats module
    data_set_folderpath = os.path.join(project_ml_folderpath, data_set_foldername)

    # data_subfolder= 'data_new_learner_testing'
    # data_folder = os.path.join(main_folder, data_subfolder)

     # Load

    algs = SL.get_algs()


    for lab in labs:

        data_lab_folderpath = os.path.join(data_set_folderpath, lab)  # TODO: if not exists, mkdir

        #
        '''
        Things to test:
        No overlapping pat_id. 
        Split not too imbalanced. 
        
        '''

        # raw_matrix_filename = (matrix_filename_template.replace('-matrix', '-matrix-raw')) % lab
        # raw_matrix_filepath = os.path.join(data_lab_folderpath, raw_matrix_filename)
        #
        raw_matrix_train, raw_matrix_evalu = SL.get_train_and_evalu_raw_matrices(
            lab = lab,
            data_lab_folderpath=data_lab_folderpath,
            random_state=random_state,
        )

        '''
        Baseline results on train and eval set
        Requires raw matrix info
        
        Baseline calculation is not a necessary part of a supervised learning pipeline.
        So if want to add this result, have to figure out the file system organization yourself!
        
        '''

        baseline_filepath = os.path.join(data_lab_folderpath, 'baseline_comparisons.csv')
        if not os.path.exists(baseline_filepath):
            baseline_evalu = ml_utils.get_baseline(df_train=raw_matrix_train,
                                                   df_test=raw_matrix_evalu,
                                                   y_label='all_components_normal')
            baseline_evalu.to_csv(baseline_filepath)

        '''
        Standard pipeline
        '''
        # print raw_matrix_train.head()
        features = {}
        features['remove'] = ['order_time', 'order_proc_id', # TODO: consistency w/ prev system
                'Birth.pre',
                'Male.preTimeDays', 'Female.preTimeDays',
                'RaceWhiteHispanicLatino.preTimeDays',
                'RaceWhiteNonHispanicLatino.preTimeDays',
                'RaceHispanicLatino.preTimeDays',
                'RaceAsian.preTimeDays',
                'RaceBlack.preTimeDays',
                'RacePacificIslander.preTimeDays',
                'RaceNativeAmerican.preTimeDays',
                'RaceOther.preTimeDays',
                'RaceUnknown.preTimeDays',
                'Death.post',
                'Death.postTimeDays'] # TODO: order_proc_id as info?!


        if lab_type == 'panel':
            features['remove'] += ['proc_code', 'num_components', 'num_normal_components', 'abnormal_panel']
            features['ylabel'] = 'all_components_normal'
        else:
            features['remove'] += ['base_name']
            features['ylabel'] = 'component_normal'
        features['keep'] = ['%s.pre'%lab]

        features['info'] = ['pat_id']
        # features['id'] =

        features['select_params'] = {'selection_problem': FeatureSelector.CLASSIFICATION,
                                     'selection_algorithm': FeatureSelector.RECURSIVE_ELIMINATION,
                                     'percent_features_to_select': 0.05}

        learner_params = {'features':features}
        SL.standard_pipeline(lab=lab,
                             algs=algs,
                             learner_params=learner_params,
                             data_lab_folderpath=data_lab_folderpath,
                             random_state=random_state
                            )


        # TODO: check baseline and ml alg come from the same dataset!

map_lab_Stanford_to_UCSF = {'LABMGN':'Magnesium, Serum - Plasma',
               'LABCAI':'Calcium, Ionized, serum-plasma',
                            'LABURIC':'Uric Acid, Serum - Plasma',
                            'LABALB':'Albumin, Serum - Plasma',
                            'LABTSH':'Thyroid Stimulating Hormone',
                            'LABTNI':'Troponin I',
                            'LABK':'Potassium, Serum - Plasma',
                            'LABNA':'Sodium, Serum - Plasma'
                            }

def map_col_Stanford_to_UCSF(col):

    '''

    Args:
        col:

    Returns:

    '''

    '''
    vitals mapping
    '''

    col = col.replace('BP_Low_Diastolic', 'DBP')
    col = col.replace('BP_High_Systolic', 'SBP')


    '''
    component mapping
    '''
    col = col.replace('CR', 'CREAT')
    col = col.replace('PO2A', 'PO2')
    col = col.replace('PO2V', 'PO2')
    col = col.replace('PCO2A', 'PCO2')

    col = col.replace('CAION', 'CAI')
    if col[:3] == 'TNI':
        col = col.replace('TNI', 'TRPI')

    if col[:2] == 'NA':
        col = col.replace('NA', 'NAWB') # TODO: make clear!
    col = col.replace('LAC', 'LACTWB')

    col = col.replace('TBIL', 'TBILI')

    '''
    cormobidity mapping
    '''
    col = col.replace('Malignancy', 'Cancer')
    col = col.replace('CHF', 'CongestiveHeartFailure')
    col = col.replace('MI', 'MyocardialInfarction')
    col = col.replace('Cerebrovascular', 'Cerebrovascular Disease')

    '''
    team mapping
    '''
    col = col.replace('CVICU', 'ICU')

    for lab_stanford, lab_ucsf in map_lab_Stanford_to_UCSF.items():
        col = col.replace(lab_stanford, lab_ucsf)



    return col


def apply_Stanford_to_UCSF(lab='LABMGN'):
    from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
    import pickle

    '''
    Data folder
    '''
    dataset_folder = "data-apply-Stanford-to-UCSF-10000-episodes/%s/"%lab

    '''
    Helper function
    '''
    fm_io = FeatureMatrixIO()

    '''
    Load raw data from UCSF
    '''
    df_ucsf_raw = fm_io.read_file_to_data_frame(dataset_folder + "%s-normality-matrix-raw.tab"%map_lab_Stanford_to_UCSF[lab])
    raw_columns_ucsf = df_ucsf_raw.columns.values.tolist()

    '''
    Load imputation template from Stanford 
    
    TODO: this is old-versioned template, (1) without column order and (2) a lot of unnecessary columns. 
    '''
    impute_dict_old = pickle.load(open(dataset_folder + "feat2imputed_dict.pkl"))
    del impute_dict_old['all_components_normal'] # TODO?!

    '''
    Use processed_matrix to select columns
    '''
    df_stanford_processed = fm_io.read_file_to_data_frame(dataset_folder + '%s-normality-matrix-processed.tab'%lab)
    df_stanford_processed.pop('pat_id')
    df_stanford_processed.pop('all_components_normal') # TODO?!
    processed_columns_stanford = df_stanford_processed.columns.values.tolist()

    '''
    Finding the corresponding UCSF column of each Stanford's processed feature
    If this feature exists in UCSF, then good
    If not, create dummy feature for UCSF raw matrix!
    '''
    impute_dict_new = {}
    for i, col_selected in enumerate(processed_columns_stanford):
        col_mapped = map_col_Stanford_to_UCSF(col_selected)

        if col_mapped in raw_columns_ucsf:
            impute_dict_new[col_mapped] = (i, impute_dict_old[col_selected])
        else:
            print "Unknown:", col_mapped

            '''
            Features Unknown to Stanford
            '''
            df_ucsf_raw[col_mapped] = df_ucsf_raw['pat_id'].apply(lambda x: 0)
            impute_dict_new[col_mapped] = (i, 0) # TODO: better strategy later?
    quit()



    '''
    Feature auxillary
    '''
    features = {'ylabel': 'all_components_normal',
                'info': ['pat_id']}

    df_ucsf_processed, _ = SL.process_matrix(df_ucsf_raw, features, impute_template=impute_dict_new)

    print "Finished processing!"


    # df_ucsf_processed.pop('all_components_normal')
    df_ucsf_processed.pop('pat_id')


    '''
    Load model
    '''
    classifier = joblib.load(dataset_folder + '%s-normality-random-forest-model.pkl'%lab)

    print "Finished Loading!"

    # print classifier.description() # TODO: why is this step so slow?!
    # print classifier.predict_probability(df_ucsf_processed)

    print classifier._params_random_forest()['decision_features']


    X_evalu, y_evalu = SL.split_Xy(data_matrix=df_ucsf_processed,
                                outcome_label='all_components_normal')
    SL.predict(X_evalu, y_evalu, classifier, output_filepath=dataset_folder+'direct_comparisons.csv')


def statistic_analysis():
    from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score

    dataset_folder = "data-apply-Stanford-to-UCSF-10000-episodes/LABMGN/"
    direct_comparisons = pd.read_csv(dataset_folder + 'direct_comparisons.csv')
    # print direct_comparisons
    print roc_auc_score(direct_comparisons['actual'].values, direct_comparisons['predict'].values)


if __name__ == '__main__':
    # main_pipelining(labs=['LABA1C'], data_source='testingSupervisedLearner')
    apply_Stanford_to_UCSF(lab='LABNA')
    # statistic_analysis()


