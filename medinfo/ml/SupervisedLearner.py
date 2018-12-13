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
    y = data_matrix.loc[:, [outcome_label]].copy()
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

def process_matrix(lab, raw_matrix, features_dict, data_path, impute_template=None):
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


    raw_matrix_path = os.path.join(lab_folder, file_name)

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


############# Compatible functions for previous results #############







############# Stats functions #############
# TODO: move to the stats module

def get_confusion_counts(actual_labels, predict_labels):

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    for i in range(len(actual_labels)):
        if actual_labels[i] == 1 and predict_labels[i] == 1:
            true_positive += 1
        elif actual_labels[i] == 0 and predict_labels[i] == 1:
            false_positive += 1
        elif actual_labels[i] == 1 and predict_labels[i] == 0:
            false_negative += 1
        elif actual_labels[i] == 0 and predict_labels[i] == 0:
            true_negative += 1
        else:
            print "what?!"
    return true_positive, false_positive, true_negative, false_negative

def get_confusion_metrics(actual_labels, predict_probas, threshold):
    #TODO: move to stats unit
    predict_labels = [1 if x > threshold else 0 for x in predict_probas]
    true_positive, false_positive, true_negative, false_negative = \
        get_confusion_counts(actual_labels, predict_labels)

    res_dict = {}
    res_dict['sensitivity'] = float(true_positive) / float(true_positive + false_negative)
    res_dict['specificity'] = float(true_negative) / float(true_negative + false_positive)
    try:
        res_dict['LR_p'] = res_dict['sensitivity'] / (1 - res_dict['specificity'])
    except ZeroDivisionError:
        if res_dict['sensitivity'] == 0:
            res_dict['LR_p'] = float('nan')
        else:
            res_dict['LR_p'] = float('inf')

    try:
        res_dict['LR_n'] = (1 - res_dict['sensitivity']) / res_dict['specificity']
    except ZeroDivisionError:
        if res_dict['sensitivity'] == 1:
            res_dict['LR_n'] = float('nan')
        else:
            res_dict['LR_n'] = float('inf')

    try:
        res_dict['PPV'] = float(true_positive) / float(true_positive + false_positive)
    except ZeroDivisionError:
        res_dict['PPV'] = float('nan')

    try:
        res_dict['NPV'] = float(true_negative) / float(true_negative + false_negative)
    except ZeroDivisionError:
        res_dict['NPV'] = float('nan')

    return res_dict


def pick_threshold(y_pick, y_pick_pred, target_PPV=0.95):
    # TODO: assume both are numpy arrays
    thres_last, PPV_last = 1., 1.
    actual_list = y_pick.flatten().tolist()
    predicted_proba = y_pick_pred.flatten().tolist()
    assert len(actual_list) == len(predicted_proba)
    # TODO: also check proba's and labels

    for thres in np.linspace(1, 0, num=1001):

        predict_class_list = [1 if x > thres else 0 for x in predicted_proba]

        TP, FP, _, _ = get_confusion_counts(actual_list, predict_class_list)
        try:
            PPV = float(TP) / float(TP + FP)
        except ZeroDivisionError:
            # PPV = float('nan')
            continue

        if PPV < target_PPV:
            break
        else:
            thres_last = thres

    return thres_last
############# Stats functions #############



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
    outcome_label = 'all_component_normal'
    algs = get_algs()


    raw_matrix = get_raw_matrix(lab, "")
    raw_matrix_train, raw_matrix_test = train_test_split(raw_matrix)


    processed_matrix_train, process_template = process_matrix(raw_matrix_train)

    X_train, y_train = processed_matrix_train # TODO

    ml_models = train_ml_models(X_train, y_train, lab, algs)  # key: (lab,alg), value: model




    processed_matrix_test, _ = process_matrix(raw_matrix_train, process_template)
    X_test, y_test = processed_matrix_test # TODO

    evaluate_ml_models(X_test, y_test, ml_models)



if __name__ == '__main__':
    main_pipelining()

