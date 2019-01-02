'''
Besides the regular pipelining, this new file allows starting from any
intermediate step.

Trying to piecing together different function parts (reliably),
instead of realizing any specific functions.

TODO: Specific pipelines do not "override" this singleton class, but calls its function?
'''

# Name key functions that thing should have
#  Feature Matrix generation
#  Feature selection
#  Imputation
#  Different model learning with different hyperparam options
#  Evaluating quality of a model (generate result calculation)
#  Separate test set evaluation
#  Saving matrix, models, results to files
#
# - Write the application code file. but API ONLY!
#    Don't implement. Just write function definitions (so you know what goes in and what comes out)
#    "Return empty"
# - Write unit tests that each go after one piece of the application
#    (this should be simple looking. Because it mimics what your final driver/script will look like)
# - Run unit test -> no compiler errors, only value fails.
# - Implement application until test passes.

import LocalEnv
import os

import pandas as pd
pd.set_option('display.width', 3000)
pd.set_option('display.max_columns', 3000)
import numpy as np
from sklearn.model_selection import train_test_split as sklearn_train_test_split
from sklearn.externals import joblib
from sklearn.calibration import CalibratedClassifierCV

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.ml.SupervisedClassifier import SupervisedClassifier


############# Util functions #############
'''
General functions for smaller tasks
'''
def split_rows(data_matrix, fraction=0.75, columnToSplitOn='pat_id', random_state=0):
    all_possible_ids = sorted(set(data_matrix[columnToSplitOn].values.tolist()))

    train_ids, test_ids = sklearn_train_test_split(all_possible_ids, train_size=fraction, random_state=random_state)

    train_matrix = data_matrix[data_matrix[columnToSplitOn].isin(train_ids)].copy()
    # y_train = pd.DataFrame(train_matrix.pop(outcome_label))
    # X_train = train_matrix

    test_matrix = data_matrix[data_matrix[columnToSplitOn].isin(test_ids)].copy()
    # y_test = pd.DataFrame(test_matrix.pop(outcome_label))
    # X_test = test_matrix

    patIds_train = train_matrix['pat_id'].values.tolist()
    patIds_test = test_matrix['pat_id'].values.tolist()
    assert (set(patIds_train) & set(patIds_test)) == set([])
    assert train_matrix.shape[0] + test_matrix.shape[0] == data_matrix.shape[0]

    return train_matrix, test_matrix


def split_Xy(data_matrix, outcome_label):
    X = data_matrix.loc[:, data_matrix.columns != outcome_label].copy()
    y = data_matrix.loc[:, outcome_label].copy()
    return X, y

def get_algs():
    return SupervisedClassifier.SUPPORTED_ALGORITHMS
############# Util functions #############





############# Main functions #############
'''
Pipelining functions for more specific tasks
'''
def SQL_to_raw_matrix(lab, data_path, use_cached=True):
    # TODO: Things to test: All 0's columns,

    if use_cached and os.path.exists(data_path):
        raw_matrix = pd.read_csv(data_path, keep_default_na=False)

    else:
        raw_matrix = pd.DataFrame()

        '''
        TODO: call the Feature Engineering functions
        '''

        raw_matrix.to_csv(data_path, index=False)
    return raw_matrix

def impute_features(matrix, strategy):

    impute_template = {}

    features_to_remove = {}
    for feature in matrix.columns.values:
        # if feature in self._removed_features:
        #     continue
        # TODO _removed_features?

        # If all values are null, just remove the feature.
        # Otherwise, imputation will fail (there's no mean value),
        # and sklearn will ragequit.
        if matrix[feature].isnull().all():
            # remove_feature(feature)
            # self._removed_features.append(feature)
            features_to_remove.append(feature)

        # Only try to impute if some of the values are null.
        # elif matrix[feature].isnull().any():
        else:
            #TODO: other strategies
            if matrix[feature].dtype not in (int, long, float):
                print feature, matrix[feature].dtype
                continue

            imputed_value = matrix[feature].mean()
            impute_template[feature] = imputed_value

            matrix[feature].fillna(imputed_value)

    matrix = matrix.drop(features_to_remove, axis=1)
    # TODO: assert all existing features have impute values

    return matrix, impute_template


def select_features(matrix, strategy):\
    # TODO: fill in
    return matrix

def process_matrix(lab, raw_matrix, features_dict, data_path='', impute_template=None):
    # General philosophy: do not change the input data
    # TODO: Things to test:

    if impute_template is not None:
        '''
        Select and impute feature based on previous template
        '''
        processed_matrix_full = raw_matrix.copy()
        columns_ordered = [""] * len(impute_template.keys())

        for feature, ind_value_pair in impute_template.items():
            column_ind, impute_value = ind_value_pair
            processed_matrix_full[feature] = processed_matrix_full[feature].fillna(impute_value)
            columns_ordered[column_ind] = feature

        if 'abnormal_panel' not in processed_matrix_full.columns.values.tolist(): #TODO: delete in the future
            processed_matrix_full['abnormal_panel'] = processed_matrix_full['all_components_normal'].apply(lambda x:1.-x)

        processed_matrix_full = pd.concat([processed_matrix_full[features_dict['non_impute_features']],
                                           processed_matrix_full[columns_ordered]],
                                          axis=1)

        # TODO: header info like done by fm_io?
        processed_matrix_full.to_csv(data_path, index=False)

    else:

        '''
        Procedure 1 (no impute template):
        raw_matrix_train -> outcome_label (all_components_normal)
                         -> info_matrix (pat_id, order_proc_id, proc_code, order_time)
                         -> leak_matrix (abnormal_panel, num_components, num_normal_components)
                         -> numeric_matrix (all others) -> imputed_matrix -> impute_template
                                                                          -> selected_matrix (5% left)

        selected_matrix + outcome_label + info_matrix + leak_matrix -> processed_matrix_full -> to_csv
        selected_matrix + outcome_label -> processed_matrix

        '''

        numeric_matrix = raw_matrix[features_dict['numeric_features']]

        '''
        impute
        '''
        numeric_matrix, impute_template = impute_features(numeric_matrix, strategy="mean")

        '''
        selection
        '''
        numeric_matrix = select_features(numeric_matrix, strategy="")

        processed_matrix_full = pd.concat([raw_matrix[features_dict['non_impute_features']], numeric_matrix], axis=1) # TODO: on?!
        processed_matrix_full.to_csv(data_path, index=False) #.sort_values(by=['pat_id','order_proc_id','order_time'])


    return processed_matrix_full, impute_template



def predict_baseline():
    pass



def train_ml_model(X_train, y_train, lab, alg):
    # TODO: How to easily include SVM, Xgboost, and Keras?
    ml_models = {}  # key: (lab,alg), value: model

    model = train(X_train, y_train, alg)

    ml_models[(lab,alg)] = model

    return ml_model


def load_ml_model(lab, ml_alg, data_folder):
    ml_model_filename = '%s-normality-%s-model.pkl'%(lab, ml_alg)
    predictor_path = os.path.join(data_folder, lab, ml_model_filename) # TODO
    return joblib.load(predictor_path)


def calibrate_ml_model(ml_model, X_cali, y_cali, cali_method='isotonic'):
    model_isotonic = CalibratedClassifierCV(ml_model, cv='prefit', method=cali_method)
    model_isotonic.fit(X=X_cali, y=y_cali)
    return model_isotonic

def predict(lab, ml_classifier, X, y, data_folder):
    pass


############# Main functions #############





############# Other functions #############




def load_raw_matrix(lab, lab_folder, file_name=None):
    fm_io = FeatureMatrixIO()

    if not file_name:
        file_name = '%s-normality-matrix-raw.tab'%lab


    raw_matrix_path = os.path.join(lab_folder, lab, file_name)

    raw_matrix = fm_io.read_file_to_data_frame(raw_matrix_path)
    return raw_matrix

    # processed_matrix_filename = "%s-normality-matrix-10000-episodes-raw.tab"%lab

    # processed_matrix = fm_io.read_file_to_data_frame(os.path.join(lab_folder, lab, processed_matrix_filename))

def get_processed_matrix(lab,
                         lab_folder=
                         os.path.join(LocalEnv.PATH_TO_CDSS,
                                      'scripts/LabTestAnalysis/machine_learning/data-panels')):
    '''
    Create processed matrix anyway (do not try to load). Because this step is fast. TODO

    :param lab:
    :param lab_folder:
    :return:
    '''

    processed_matrix_filename = "%s-normality-matrix-processed.tab"%lab



############# Other functions #############






############# Compatible functions for previous results #############

def load_process_template(lab, non_impute_features, data_folder):
    raw_matrix_filename = '%s-normality-matrix-raw.tab' % lab
    raw_matrix_path = os.path.join(data_folder, lab, raw_matrix_filename)

    processed_matrix_filename = '%s-normality-matrix-processed.tab' % lab
    processed_matrix_path = os.path.join(data_folder, lab, processed_matrix_filename)

    fm_io = FeatureMatrixIO() # TODO: use def get_raw_matrix instead
    raw_matrix = fm_io.read_file_to_data_frame(raw_matrix_path)

    raw_features_all = raw_matrix.columns.values.tolist()
    numeric_features = [x for x in raw_features_all if x not in non_impute_features]


    processed_matrix = fm_io.read_file_to_data_frame(processed_matrix_path)

    final_features = processed_matrix.columns.values.tolist()

    process_template = {}
    ind_feature = 0
    for feature in final_features:
        if feature in numeric_features:
            imputed_value = raw_matrix[feature].mean()
            process_template[feature] = (ind_feature, imputed_value)
            ind_feature += 1

    return process_template


def get_process_template(feat2imputed_path):
    import pickle
    feat2imputed_dict = pickle.load(open(feat2imputed_path, 'r'))
    return feat2imputed_dict

############# Compatible functions for previous results #############









def pipelining(source_set_folder, labs, source_type, source_ids):
    '''
    This function aims at gluing several steps.

    The full steps are:
        Empty (data in SQL) -> raw matrix -> processed matrix
        -> processed train, processed test -> trained models
        -> results and reports

    Args:
        source_set_folder:
        labs:
        source_type:

    Returns:

    '''
    status = 'ready'
    assert os.path.exists(source_set_folder)

    if source_type == 'raw-matrix':
        # TODO:
        # get one new lab's raw matrix
        # get one old lab's model
        # run it through the model


        for lab in labs:
            cur_folder = os.path.join(source_set_folder,
                                      lab)
            cur_files = os.listdir(cur_folder)
            for cur_file in cur_files:
                if 'raw' in cur_file and all(x in cur_file for x in source_ids):
                    print cur_file

            quit()


    return status


def main_pipelining():
    '''
    This pipelining procedure is consistent to the previous SupervisedLearningPipeline.py
    '''

    lab = "LABA1C"
    lab_type = 'panel'
    outcome_label = 'all_components_normal'
    algs = get_algs()


    raw_matrix = get_raw_matrix(lab, "")
    raw_matrix_train, raw_matrix_test = train_test_split(raw_matrix)


    processed_matrix_train, process_template = process_matrix(raw_matrix_train)

    X_train, y_train = split_rows(processed_matrix_train) # TODO

    ml_models = train_ml_models(X_train, y_train, lab, algs)  # key: (lab,alg), value: model




    processed_matrix_test, _ = process_matrix(raw_matrix_train, process_template)
    X_test, y_test = processed_matrix_test # TODO

    evaluate_ml_models(X_test, y_test, ml_models)


def output_result(X_test, y_test, model_src, res_folderpath):
    y_pred_prob = model_src.predict_probability(X_test)[:,1]

    direct_comparisons = pd.DataFrame({'actual': y_test.values.flatten(), 'predict': y_pred_prob})
    direct_comparisons.to_csv(res_folderpath)

def obtain_baseline_results(train_matrix, test_matrix, dst_filepath='', isLabPanel=True):
    # for episode_dict in self.getPatientEpisodeIterator():
    #     episode_dict

    # Step1: group by pat_id
    # Step2: For each group, obtain predicts
    #   Step 2.1: order by order_time
    #   Step 2.2: Obtain

    actual_cnt_1 = 0
    actual_cnt_0 = 0

    train_labels = train_matrix['all_components_normal'].values

    # Calc the prevalence from training data
    prevalence_1 = float(sum(train_labels))/float(len(train_labels))

    raw_matrix = test_matrix
    episode_cnt = raw_matrix.shape[0]

    if isLabPanel:
        ylabel = 'all_components_normal'
    else:
        ylabel = 'component_normal'

    # raw_matrix = raw_matrix.rename(columns={'component_normal':'all_components_normal'})

    raw_matrix_dict = raw_matrix[['pat_id', 'order_time', ylabel]].to_dict('records')

    # for _ in self.getPatientEpisodeIterator(): # less stupid way to do this
    #     episode_cnt += 1



    episode_groups_dict = {}  # pat_id: [episode_dicts]
    for episode_dict in raw_matrix_dict:
        if episode_dict['pat_id'] in episode_groups_dict:
            episode_groups_dict[episode_dict['pat_id']].append(episode_dict)
        else:
            episode_groups_dict[episode_dict['pat_id']] = [episode_dict]




    baseline_comparisons = pd.DataFrame(columns=['actual', 'predict'])

    for pat_id in episode_groups_dict:
        #   Step 2.1: order by order_time
        newlist = sorted(episode_groups_dict[pat_id], key=lambda k: k['order_time'])

        newlist[0]['predict'] = prevalence_1
        baseline_comparisons = baseline_comparisons.append({'actual':newlist[0][ylabel],
                                     'predict':newlist[0]['predict']}, ignore_index=True)

        for i in range(1,len(newlist)):
            newlist[i]['predict'] = newlist[i-1][ylabel]
            baseline_comparisons = baseline_comparisons.append({'actual': newlist[i][ylabel],
                                         'predict': newlist[i]['predict']}, ignore_index=True)

    baseline_comparisons.to_csv(dst_filepath)

def main_different_testsets():
    '''
    Apply trained model on another test set.

    Returns:

    '''
    main_folder = os.path.join(LocalEnv.PATH_TO_CDSS, 'scripts/LabTestAnalysis/machine_learning/')

    src_foldername = "data-panels-10000-episodes"
    dst_foldername = "data-panels-5000-holdout"

    src_folderpath = os.path.join(main_folder, src_foldername)
    dst_folderpath = os.path.join(main_folder, dst_foldername)

    from scripts.LabTestAnalysis.machine_learning.LabNormalityPredictionPipeline import NON_PANEL_TESTS_WITH_GT_500_ORDERS

    for lab in NON_PANEL_TESTS_WITH_GT_500_ORDERS:

        feat2imputed_path = os.path.join(src_folderpath, lab, 'feat2imputed_dict.csv')
        template_src = pd.read_csv(feat2imputed_path, keep_default_na=False)#get_process_template(feat2imputed_path)

        # TODO: such info should be hidden in the function?

        raw_matrix_src = load_raw_matrix(lab, src_folderpath)

        #
        raw_matrix_dst = load_raw_matrix(lab, dst_folderpath)

        raw_matrix_1, raw_matrix_2 = split_rows(raw_matrix_dst, fraction=0.5)
        raw_matrices = [raw_matrix_1, raw_matrix_2]

        for ml_alg in SupervisedClassifier.SUPPORTED_ALGORITHMS:  # TODO
            model_src = load_ml_model(lab, ml_alg, src_folderpath)



            res_foldername_template = "results-from-panels-10000-to-panels-5000-part-%i/"
            for ind, raw_matrix_dst in enumerate(raw_matrices):
                res_foldername = res_foldername_template%(ind+1)
                res_folderpath = os.path.join(main_folder, res_foldername)

                baseline_filename = 'baseline_comparisons.csv'
                baseline_filepath = os.path.join(res_folderpath, lab, baseline_filename)
                # obtain_baseline_results(raw_matrix_src, raw_matrix_dst, baseline_filepath)


                if not os.path.exists(res_folderpath):
                    os.mkdir(res_folderpath)

                if not os.path.exists(os.path.join(res_folderpath, lab)):
                    os.mkdir(os.path.join(res_folderpath, lab))

                feat2imputed = template_src.to_dict()
                for key in feat2imputed:
                    feat2imputed[key] = feat2imputed[key][0]

                raw_matrix_dst_filepath = os.path.join(res_folderpath, lab, '%s-normality-test-matrix-raw.tab' % lab)
                # raw_matrix_dst.to_csv(raw_matrix_dst_filepath, index=False)



                processed_matrix_dst = raw_matrix_dst[template_src.columns.tolist()+['pat_id']].fillna(feat2imputed)

                processed_matrix_dst_filepath = os.path.join(res_folderpath, lab, '%s-normality-test-matrix-processed.tab'%lab)
                processed_matrix_dst.to_csv(processed_matrix_dst_filepath, index=False) # TODO: use fm_io

                processed_matrix_dst.pop('pat_id')
                continue

                X_test, y_test = split_Xy(processed_matrix_dst, outcome_label='all_components_normal')

                output_filename = 'direct_comparisons.csv'
                output_filepath = os.path.join(res_folderpath, lab, ml_alg, output_filename)
                if not os.path.exists(os.path.join(res_folderpath, lab, ml_alg)):
                    os.mkdir(os.path.join(res_folderpath, lab, ml_alg))
                output_result(X_test, y_test, model_src, output_filepath)




if __name__ == '__main__':
    main_different_testsets()

