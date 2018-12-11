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
from sklearn.model_selection import train_test_split as sklearn_train_test_split

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

def get_raw_matrix(lab,
                         lab_folder=
                         os.path.join(LocalEnv.PATH_TO_CDSS,
                                      'scripts/LabTestAnalysis/machine_learning/data-panels')):
    processed_matrix_filename = "%s-normality-matrix-10000-episodes-raw.tab"%lab
    fm_io = FeatureMatrixIO()
    processed_matrix = fm_io.read_file_to_data_frame(os.path.join(lab_folder, lab, processed_matrix_filename))
    return processed_matrix

def get_processed_matrix(lab,
                         lab_folder=
                         os.path.join(LocalEnv.PATH_TO_CDSS,
                                      'scripts/LabTestAnalysis/machine_learning/data-panels')):
    processed_matrix_filename = "%s-normality-matrix-10000-episodes-processed.tab"%lab
    fm_io = FeatureMatrixIO()
    processed_matrix = fm_io.read_file_to_data_frame(os.path.join(lab_folder, lab, processed_matrix_filename))
    return processed_matrix

def impute_features(matrix, strategy):
    return None

def remove_features(matrix, features_to_remove):
    return None

def select_features(matrix, strategy):
    return None

def write_processed_matrix(matrix, write_folder=""):
    fm_io = FeatureMatrixIO()
    fm_io.write_data_frame_to_file(matrix, write_folder)
    pass

def get_algs():
    return []


def train_test_split(processed_matrix, outcome_label, columnToSplitOn='pat_id', random_state=0):
    '''
    Args:
        processed_matrix:
        Feature matrix ready to train (including the outcome label).

        outcome_label:
        For panels, "all_component_normal".
        For components, "component_normal".

        columnToSplitOn:
        The column to split the matrix on.

    Returns:
        X_train, y_train, X_test, y_test as usual.
    '''
    # log.debug('outcome_label: %s' % outcome_label)
    all_possible_ids = sorted(set(processed_matrix[columnToSplitOn].values.tolist()))

    train_ids, test_ids = sklearn_train_test_split(all_possible_ids, random_state=random_state)

    train_matrix = processed_matrix[processed_matrix[columnToSplitOn].isin(train_ids)].copy()
    y_train = pd.DataFrame(train_matrix.pop(outcome_label))
    X_train = train_matrix

    test_matrix = processed_matrix[processed_matrix[columnToSplitOn].isin(test_ids)].copy()
    y_test = pd.DataFrame(test_matrix.pop(outcome_label))
    X_test = test_matrix

    return X_train, y_train, X_test, y_test

def train(X_train, y_train, alg):
    return None

def predict(X_test, model):
    return None

def evaluate(y_test, y_pred):
    return None

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

def process_matrix(raw_matrix):
    intermediate_matrix = raw_matrix
    intermediate_matrix = remove_features(intermediate_matrix, features_to_remove=[])
    intermediate_matrix = impute_features(intermediate_matrix, strategy="mean")
    intermediate_matrix = select_features(intermediate_matrix, strategy="")
    processed_matrix = intermediate_matrix

    write_processed_matrix(processed_matrix, "")

    return processed_matrix


def train_ml_models(X_train, y_train, lab, algs):
    ml_models = {}  # key: (lab,alg), value: model

    for alg in algs:
        model = train(X_train, y_train, alg)

        ml_models[(lab,alg)] = model

    return ml_models

def pick_threshold(y_true, y_pred, target_PPV):
    pass

def load_data(data_type, data_source):
    pass

def main_pipelining():
    '''
    This pipelining procedure is consistent to the previous SupervisedLearningPipeline.py
    '''

    lab = "LABA1C"


    raw_matrix = get_raw_matrix(lab, "")

    processed_matrix = process_matrix(raw_matrix)

    X_train, y_train, X_test, y_test = train_test_split()

    algs = get_algs()
    ml_models = train_ml_models(X_train, y_train, algs) # key: (lab,alg), value: model


    for tag, model in ml_models.items():
        y_pred = predict(X_test, model)
        evaluate(y_test, y_pred)

        X_pick, y_pick = load_data(data_type='raw_matrix', data_source='AWS')
        y_pick_pred = predict(X_pick, model)
        pick_threshold(y_true=y_pick, y_pred=y_pick_pred, target_PPV=0.95)



if __name__ == '__main__':
    main_pipelining()

