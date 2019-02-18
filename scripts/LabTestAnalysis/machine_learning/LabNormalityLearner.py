

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


# outcome_label = 'all_components_normal'
#
# info_features = ['pat_id', 'order_proc_id', 'proc_code', 'order_time']
# leak_features = ['abnormal_panel', 'num_components', 'num_normal_components']
#
# non_impute_features = info_features + leak_features + [outcome_label]
#
# features_dict = {
#     'non_impute_features':non_impute_features,
#     'outcome_label':outcome_label,
#     'info_features':info_features,
#     'leak_features':leak_features
# }


def get_feature_dict():
    features = {}
    features['remove'] = ['order_time', 'order_proc_id',  # TODO: consistency w/ prev system
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
                          'Death.postTimeDays']  # TODO: order_proc_id as info?!

    if lab_type == 'panel':
        features['remove'] += ['proc_code', 'num_components', 'num_normal_components', 'abnormal_panel']
        features['ylabel'] = 'all_components_normal'
    else:
        features['remove'] += ['base_name']
        features['ylabel'] = 'component_normal'
    features['keep'] = ['%s.pre' % lab]

    features['info'] = ['pat_id']
    # features['id'] =

    features['select_params'] = {'selection_problem': FeatureSelector.CLASSIFICATION,
                                 'selection_algorithm': FeatureSelector.RECURSIVE_ELIMINATION,
                                 'percent_features_to_select': 0.05}
    return features


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
        features = get_feature_dict()

        learner_params = {'features':features}
        SL.standard_pipeline(lab=lab,
                             algs=algs,
                             learner_params=learner_params,
                             data_lab_folderpath=data_lab_folderpath,
                             random_state=random_state
                            )


        # TODO: check baseline and ml alg come from the same dataset!





def map_col_Stanford_to_UCSF(col):

    '''

    Args:
        col:

    Returns:

    '''

    '''
    vitals mapping
    '''

    for key, val in ml_utils.map_vitals_from_Stanford_to_UCSF.items():
        if col[:len(key)+1] == key+'.':
            col = col.replace(key, val)

    '''
    component mapping, only replace if it is a pre-fix
    '''
    for key, val in ml_utils.map_component_from_Stanford_to_UCSF.items():
        if col[:len(key)+1] == key+'.':
            col = col.replace(key, val)

    '''
    cormobidity mapping
    '''
    for key, val in ml_utils.map_cormobidity_from_Stanford_to_UCSF.items():
        if col[:len(key)+1] == key+'.':
            col = col.replace(key, val)

    '''
    team mapping
    '''
    for key, val in ml_utils.map_team_from_Stanford_to_UCSF.items():
        if col[:len(key)+1] == key+'.':
            col = col.replace(key, val)

    '''
    The lab of interest
    '''
    for lab_stanford, lab_ucsf in ml_utils.map_panel_from_Stanford_to_UCSF.items():
        col = col.replace(lab_stanford, lab_ucsf) # TODO: very dangerous for pre-fix, BLC2!

    return col


def apply_src_to_dst(lab, lab_type,
                           src_dataset_folderpath,
                           dst_dataset_folderpath,
                           output_folderpath,
                     use_cached_results=True):
    '''
    What: Use case that transfers model from one institute (src) to another (dst)

    Why:
    TODO: automatically recognize lab_type

    How:
    Load inputs:
    (1) Read dst raw matrix from dst dataset_folder/lab
    (2) Read src imputation template (only includes final features) from src dataset_folder/lab
    (3) Read src trained model from src dataset_folder/lab

    Process:
    (1)
    Create a dst imputation template
    For each src feature in the src imputation template
        map the feature to dst column
        if not exists such dst column:
            create a new column in the dst raw matrix, fill with the src imputing value

    (2)
    Feed into process_matrix, pop pat_id and info features, split Xy

    (3)
    Feed X into classifier, get y_pred, write to direct_comparisons with y_true

    Args:
        lab:
        lab_type:
        dataset_folder:

    Returns:

    '''
    from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
    import pickle

    import os
    if not os.path.exists(output_folderpath):
        os.mkdir(output_folderpath)
    output_filepath = os.path.join(output_folderpath, 'direct_comparisons.csv')
    if use_cached_results and os.path.exists(output_filepath):
        print output_filepath + ' exists!'
        return

    # TODO: UMich?
    if lab_type == 'panel':
        from scripts.LabTestAnalysis.machine_learning.ml_utils import map_panel_from_Stanford_to_UCSF as map_lab
        ylabel = 'all_components_normal'
    else:
        from scripts.LabTestAnalysis.machine_learning.ml_utils import map_component_from_Stanford_to_UCSF as map_lab
        ylabel = 'component_normal'

    lab_mapped = map_lab.get(lab,lab)
    print lab_mapped

    '''
        Helper function
        '''
    fm_io = FeatureMatrixIO()


    '''
    Data folder
    '''
    # lab_folder = os.path.join(dataset_folder, lab)


    '''
    Load raw data from UCSF
    '''
    df_raw_dst = SL.load_raw_matrix(lab=lab_mapped, dataset_folderpath=dst_dataset_folderpath)

    # imputations_stanford = SL.load_imputation_template(lab=lab_mapped, dataset_folderpath=dst_dataset_folderpath, lab_type=lab_type)



    # df_ucsf_raw = fm_io.read_file_to_data_frame(lab_folder + '/' + "%s-normality-matrix-raw.tab"%map_lab_Stanford_to_UCSF[lab])
    raw_columns_dst = df_raw_dst.columns.values.tolist()

    '''
    From test processed, get the patient evalu set  
    '''

    df_processed_evalu_dst = SL.load_processed_matrix(lab_mapped, dst_dataset_folderpath, type='evalu') #fm_io.read_file_to_data_frame(lab_folder + '/'  + "%s-normality-test-matrix-processed.tab" % map_lab_Stanford_to_UCSF[lab])
    patIds_evalu_dst = ml_utils.get_patIds(df_processed_evalu_dst) #set(df_ucsf_processed_evalu['pat_id'].values.tolist())

    df_raw_evalu_dst = df_raw_dst[df_raw_dst['pat_id'].isin(patIds_evalu_dst)]


    assert df_raw_dst.shape[0] > df_raw_evalu_dst.shape[0]

    '''
    Load imputation template from Stanford 
    
    TODO: this is old-versioned template, (1) without column order and (2) a lot of unnecessary columns. 
    '''

    # del impute_dict_old[ylabel] #

    '''
    Use processed_matrix to select columns
    '''
    df_processed_src = fm_io.read_file_to_data_frame(src_dataset_folderpath + '/' + lab + '/%s-normality-matrix-processed.tab'%lab)
    df_processed_src.pop('pat_id')
    df_processed_src.pop(ylabel) # TODO?!
    processed_columns_stanford = df_processed_src.columns.values.tolist()

    classifier_src = SL.load_ML_model(lab=lab, alg='random-forest', dataset_folderpath=src_dataset_folderpath)


    '''
    Finding the corresponding UCSF column of each Stanford's processed feature
    If this feature exists in UCSF, then good
    If not, create dummy feature for UCSF raw matrix!
    '''
    # imputations_ucsf = {}

    # for feature, ind_val_pair in imputations_stanford.items():
    #     feature_ucsf = map_col_Stanford_to_UCSF(feature)
    #     if feature_ucsf not in raw_columns_dst:
    #         print feature_ucsf
    #         pass
        # imputations_ucsf[]

    impute_dict_old = pickle.load(open(src_dataset_folderpath + '/' + lab + '/' + "feat2imputed_dict.pkl"))
    del impute_dict_old[ylabel]

    impute_dict_new = {}
    i = 0
    for col_selected in processed_columns_stanford:
        col_mapped = map_col_Stanford_to_UCSF(col_selected)

        if col_selected in raw_columns_dst:
            col_mapped = col_selected

        elif col_mapped not in raw_columns_dst:
            print "Unknown:", col_mapped
            '''
            Stanford feature that has not corresponding UCSF one; create dummy UCSF column
            '''

            df_raw_evalu_dst[col_mapped] = df_raw_evalu_dst['pat_id'].apply(lambda x: 0)
        elif col_mapped in impute_dict_new:
            '''
            Different src features map into the same dst feature
            '''
            col_mapped = col_selected
            df_raw_evalu_dst[col_mapped] = df_raw_evalu_dst['pat_id'].apply(lambda x: 0)
            pass

        '''
        Use Stanford mean to impute
        '''
        if col_mapped in df_raw_evalu_dst:
            # print col_mapped # TODO: XPPT and PPT are the same thing?
            pass

        # print i, col_selected, col_mapped
        '''
        40 PCO2A.-14_0.proximate PCO2.-14_0.proximate
        41 PCO2V.-14_0.proximate PCO2.-14_0.proximate
        '''

        impute_dict_new[col_mapped] = (i, impute_dict_old[col_selected]) #

        i += 1
    '''
    Feature auxillary
    '''
    features = {'ylabel': ylabel,
                'info': ['pat_id']}

    df_ucsf_processed_evalu, _ = SL.process_matrix(df_raw_evalu_dst, features, impute_template=impute_dict_new)

    print "Finished processing!"


    # df_ucsf_processed.pop('all_components_normal')
    df_ucsf_processed_evalu.pop('pat_id')


    '''
    Load model
    '''


    print "Finished Loading!"

    # print classifier.description() # TODO: why is this step so slow?!
    # print classifier.predict_probability(df_ucsf_processed)

    print classifier_src._params_random_forest()['decision_features']


    X_evalu, y_evalu = SL.split_Xy(data_matrix=df_ucsf_processed_evalu,
                                outcome_label=ylabel)


    SL.predict(X_evalu, y_evalu, classifier_src, output_filepath=output_filepath)


def statistic_analysis(lab, dataset_folder):
    from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score

    direct_comparisons = pd.read_csv(os.path.join(dataset_folder, 'direct_comparisons.csv'))
    # print direct_comparisons
    print lab, roc_auc_score(direct_comparisons['actual'].values, direct_comparisons['predict'].values)


def transfer_labs(src_dataset='Stanford', dst_dataset='UCSF', lab_type='panel'):
    # main_pipelining(labs=['LABA1C'], data_source='testingSupervisedLearner')
    # dataset_folder = "data-apply-Stanford-to-UCSF-10000-episodes"

    from LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS, STRIDE_COMPONENT_TESTS

    if lab_type == 'panel':
        labs = ['LABURIC']
        # from scripts.LabTestAnalysis.machine_learning.ml_utils import map_panel_from_Stanford_to_UCSF as map_lab
    else:
        from scripts.LabTestAnalysis.lab_statistics import stats_utils
        labs = stats_utils.get_important_labs(lab_type=lab_type) #STRIDE_COMPONENT_TESTS
        # from scripts.LabTestAnalysis.machine_learning.ml_utils import map_component_from_Stanford_to_UCSF as map_lab

    for lab in labs:
        direct_comparisons_folderpath = 'data-%s-%s-%s-10000-episodes/'%(lab_type,src_dataset,dst_dataset)+lab
        apply_src_to_dst(lab=lab, lab_type=lab_type,
                               src_dataset_folderpath='data-%s-%s-10000-episodes'%(src_dataset, lab_type),#'data-Stanford-%s-10000-episodes'%lab_type,
                               dst_dataset_folderpath='data-%s-%s-10000-episodes'%(dst_dataset, lab_type),
                               output_folderpath=direct_comparisons_folderpath)
        statistic_analysis(lab=lab, dataset_folder=direct_comparisons_folderpath)

if __name__ == '__main__':
    transfer_labs(src_dataset='Stanford', dst_dataset='UCSF', lab_type='component')
    # statistic_analysis(lab='LABURIC', dataset_folder=os.path.join('data', 'LABURIC', 'transfer_Stanford_to_UCSF')) #'data-panel-Stanford-UCSF-10000-episodes'
    # apply_Stanford_to_UCSF(lab='LABURIC', lab_type='panel',
    #                        src_dataset_folderpath=os.path.join('data', 'LABURIC', 'wi last normality - Stanford'),
    #                        dst_dataset_folderpath=os.path.join('data', 'LABURIC', 'wi last normality - UCSF'),
    #                        output_folderpath=os.path.join('data', 'LABURIC', 'transfer_Stanford_to_UCSF'))
