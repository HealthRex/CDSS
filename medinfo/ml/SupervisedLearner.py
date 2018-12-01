'''
Besides the regular pipelining, this new file allows starting from any
intermediate step.

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

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
import os
import LocalEnv

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

def train_test_split():
    return None

def train(X_train, y_train, alg):
    return None

def predict(X_test, model):
    return None

def evaluate(y_test, y_pred):
    return None

def main_pipelining():
    '''
    This pipelining procedure is consistent to the previous SupervisedLearningPipeline.py
    '''

    lab = "LABA1C"
    raw_matrix = get_raw_matrix(lab, "")

    intermediate_matrix = raw_matrix
    intermediate_matrix = remove_features(intermediate_matrix, features_to_remove=[])
    intermediate_matrix = impute_features(intermediate_matrix, strategy="mean")
    intermediate_matrix = select_features(intermediate_matrix, strategy="")
    processed_matrix = intermediate_matrix

    write_processed_matrix(processed_matrix, "")

    X_train, y_train, X_test, y_test = train_test_split()
    algs = get_algs()
    for alg in algs:
        model = train(X_train, y_train, alg)


        y_pred = predict(X_test, model)

        evaluate(y_test, y_pred)

if __name__ == '__main__':
    main_pipelining()

