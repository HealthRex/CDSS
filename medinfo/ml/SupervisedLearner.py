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

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

def get_raw_matrix(lab, lab_folder, file_name=None):
    fm_io = FeatureMatrixIO()

    if not file_name:
        file_name = '%s-normality-matrix-10000-episodes-raw.tab'%lab


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

    processed_matrix_filename = "%s-normality-matrix-10000-episodes-processed.tab"%lab


def impute_features(matrix, strategy, impute_template=None):

    if impute_template:
        #TODO
        pass

    else:
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

def remove_features(matrix, features_to_remove):
    matrix = matrix.drop(features_to_remove, axis=1)
    return matrix

def select_features(matrix, strategy):
    return matrix

def write_processed_matrix(matrix, write_folder=""):
    fm_io = FeatureMatrixIO()
    fm_io.write_data_frame_to_file(matrix, write_folder)
    pass

def get_algs():
    return []


def train_test_split(processed_matrix, columnToSplitOn='pat_id', random_state=0):
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

    train_matrix = processed_matrix[processed_matrix[columnToSplitOn].isin(train_ids)]
    # y_train = pd.DataFrame(train_matrix.pop(outcome_label))
    # X_train = train_matrix

    test_matrix = processed_matrix[processed_matrix[columnToSplitOn].isin(test_ids)]
    # y_test = pd.DataFrame(test_matrix.pop(outcome_label))
    # X_test = test_matrix

    patIds_train = train_matrix['pat_id'].values.tolist()
    patIds_test = test_matrix['pat_id'].values.tolist()
    assert (set(patIds_train) & set(patIds_test)) == set([])
    assert train_matrix.shape[0] + test_matrix.shape[0] == processed_matrix.shape[0]

    return train_matrix, test_matrix

def train(X_train, y_train, alg):
    return None

def predict(X, model):
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

def get_process_template(lab, numeric_features, data_folder):
    raw_matrix_filename = '%s-normality-matrix-10000-episodes-raw.tab' % lab
    raw_matrix_path = os.path.join(data_folder, lab, raw_matrix_filename)

    processed_matrix_filename = '%s-normality-matrix-10000-episodes-processed.tab' % lab
    processed_matrix_path = os.path.join(data_folder, lab, processed_matrix_filename)

    fm_io = FeatureMatrixIO()
    raw_matrix = fm_io.read_file_to_data_frame(raw_matrix_path)
    processed_matrix = fm_io.read_file_to_data_frame(processed_matrix_path)

    final_features = processed_matrix.columns.values.tolist()

    impute_template = {}
    for feature in final_features:
        if feature in numeric_features:
            imputed_value = raw_matrix[feature].mean()
            impute_template[feature] = imputed_value

    return impute_template


def process_matrix(raw_matrix, data_folder, lab, impute_template=None):


    '''
    final features: (imputation value, order)
    also order! 
    '''
    if impute_template:
        intermediate_matrix = raw_matrix
        columns_ordered = [""] * len(impute_template.keys())
        for feature, value_order in impute_template.items():
            impute_value, column_order = value_order
            intermediate_matrix[feature] = intermediate_matrix[feature].fillna(impute_value)
            columns_ordered[column_order] = feature

        processed_matrix = intermediate_matrix[columns_ordered]
        return processed_matrix
    else:
        processed_matrix_filename = '%s-normality-matrix-10000-episodes-processed.tab'%lab
        #TODO: splitted train and test processed ?
        processed_matrix_path = os.path.join(data_folder, processed_matrix_filename)


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

        numeric_matrix = raw_matrix[numeric_features]
        numeric_matrix, impute_template = impute_features(numeric_matrix, strategy="mean")
        numeric_matrix = select_features(numeric_matrix, strategy="")

        # print "numeric_matrix.head()"
        # print numeric_matrix.head()

        # print "raw_matrix[non_impute_features].head()"
        # print raw_matrix[non_impute_features].head()
        processed_matrix_full = pd.concat([raw_matrix[non_impute_features], numeric_matrix], axis=1) # TODO: on?!

        # TODO here
        # processed_matrix_full.sort_values(by=['pat_id','order_proc_id','order_time']).to_csv("TODO.csv", index=False)

        processed_matrix = pd.concat([raw_matrix[outcome_label], numeric_matrix], axis=1)
        # final_columns = processed_matrix.columns.values.tolist()
        # # TODO: outcome label
        # for feature, _ in impute_template.items():
        #     if feature not in final_columns:
        #         impute_features.pop(feature)
        # for i, feature in enumerate(final_columns):
        #     impute_template[feature] = (impute_template[feature], i)

        # print impute_template
        return processed_matrix, impute_template

        # intermediate_matrix = remove_features(intermediate_matrix, features_to_remove=[])



    write_processed_matrix(processed_matrix, "")

    fm_io = FeatureMatrixIO()
    # processed_matrix = fm_io.read_file_to_data_frame(os.path.join(lab_folder, lab, processed_matrix_filename))



    patIds_df = raw_matrix['pat_id'].copy()

    self._train_test_split(raw_matrix, params['outcome_label'])

    # ##
    # folder_path = '/'.join(params['raw_matrix_path'].split('/')[:-1])
    # self._X_train.join(self._y_train).to_csv(folder_path + '/' + 'train_raw.csv', index=False)
    # self._X_test.join(self._y_test).to_csv(folder_path + '/' + 'test_raw.csv', index=False)
    #
    # '''
    # Mini-test that there are no overlapping patients
    # '''
    # assert bool(set(self._X_train['pat_id'].values) & set(self._X_test['pat_id'].values)) == False
    # ##

    fmt = FeatureMatrixTransform()
    train_df = self._X_train.join(self._y_train)
    fmt.set_input_matrix(train_df)

    # Add features.
    self._add_features(fmt, params['features_to_add'])

    # Remove features.
    self._remove_features(fmt, params['features_to_remove'])
    # Filter on features
    if 'features_to_filter_on' in params:
        self._filter_on_features(fmt, params['features_to_filter_on'])

    # HACK: When read_csv encounters duplicate columns, it deduplicates
    # them by appending '.1, ..., .N' to the column names.
    # In future versions of pandas, simply pass mangle_dupe_cols=True
    # to read_csv, but not ready as of pandas 0.22.0.
    for feature in raw_matrix.columns.values:
        if feature[-2:] == ".1":
            fmt.remove_feature(feature)
            self._removed_features.append(feature)

    # Impute data.
    self._impute_data(fmt, train_df, params['imputation_strategies'])

    # In case any all-null features were created in preprocessing,
    # drop them now so feature selection will work
    fmt.drop_null_features()

    # Build interim matrix.
    train_df = fmt.fetch_matrix()

    self._y_train = pd.DataFrame(train_df.pop(params['outcome_label']))
    self._X_train = train_df

    '''
    Select X_test columns according to processed X_train
    '''
    self._X_test = self._X_test[self._X_train.columns]
    '''
    Impute data according to the same strategy when training
    '''
    for feat in self._X_test.columns:
        self._X_test[feat] = self._X_test[feat].fillna(self.feat2imputed_dict[feat])

    self._select_features(params['selection_problem'],
                          params['percent_features_to_select'],
                          params['selection_algorithm'],
                          params['features_to_keep'])

    '''
    The join is based on index by default.
    Will remove 'pat_id' (TODO sxu: more general in the future) later in train().
    '''
    self._X_train = self._X_train.join(patIds_df, how='left')
    self._X_test = self._X_test.join(patIds_df, how='left')

    train = self._y_train.join(self._X_train)
    test = self._y_test.join(self._X_test)

    processed_trainMatrix_path = processed_matrix_path.replace("matrix", "train-matrix")
    fm_io.write_data_frame_to_file(train, processed_trainMatrix_path)
    processed_testMatrix_path = processed_matrix_path.replace("matrix", "test-matrix")
    fm_io.write_data_frame_to_file(test, processed_testMatrix_path)

    processed_matrix = train.append(test)
    '''
    Recover the order of rows before writing into disk, 
    where the index info will be missing.
    '''
    processed_matrix.sort_index(inplace=True)

    return processed_matrix, process_template

    return processed_matrix, process_template


def train_ml_models(X_train, y_train, lab, algs):
    # TODO: How to easily include SVM, Xgboost, and Keras?
    ml_models = {}  # key: (lab,alg), value: model

    for alg in algs:
        model = train(X_train, y_train, alg)

        ml_models[(lab,alg)] = model

    return ml_models

def pick_threshold(X_pick, y_pick, ml_models, target_PPV):
    for model in ml_models:
        y_pick_pred = predict(X_pick, model)
    pass

def load_data(data_type, data_source):
    pass

def evaluate_ml_models(X_test, y_test, ml_models, thresholds):
    '''
    Include AUROC, AUPRC,
    After picking a threshold, also confusion metrics

    Args:
        X_test:
        y_test:
        ml_models:

    Returns:

    '''
    for tag, model in ml_models.items():
        y_pred = predict(X_test, model)
        evaluate(y_test, y_pred)

def get_ml_model(lab, ml_model, data_folder):
    predictor_path = os.path.join(data_folder, ml_model) # TODO
    joblib.load(predictor_path)
    pass

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

