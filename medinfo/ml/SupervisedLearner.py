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
from medinfo.ml.SupervisedClassifier import SupervisedClassifier


def load_processed_matrix(lab, data_folder, tag=None):
    # TODO sxu: delete '10000' in the future
    # TODO: correct old file names in the old script
    processed_matrix_filename = '%s-normality-matrix-processed'%lab
    if tag is not None:
        processed_matrix_filename += '-' + tag
    processed_matrix_filename += '.tab'

    processed_matrix_path = os.path.join(data_folder, lab, processed_matrix_filename)
    fm_io = FeatureMatrixIO()
    return fm_io.read_file_to_data_frame(processed_matrix_path)

def load_raw_matrix(lab, data_folder):
    raw_matrix_filename = '%s-normality-matrix-raw.tab' % lab
    raw_matrix_path = os.path.join(data_folder, lab, raw_matrix_filename)
    fm_io = FeatureMatrixIO()
    return fm_io.read_file_to_data_frame(raw_matrix_path)

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

def load_ml_model(lab, ml_alg, data_folder):
    ml_model_filename = '%s-normality-%s-model.pkl'%(lab, ml_alg)
    predictor_path = os.path.join(data_folder, lab, ml_model_filename) # TODO
    return joblib.load(predictor_path)


def get_algs():
    return SupervisedClassifier.SUPPORTED_ALGORITHMS




def get_raw_matrix(lab, lab_folder, file_name=None):
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





def process_matrix(lab, raw_matrix, features_dict, data_folder, impute_template=None):


    '''
    final features: (imputation value, order)
    also order! 
    '''
    if impute_template:
        print impute_template

        intermediate_matrix = raw_matrix
        columns_ordered = [""] * len(impute_template.keys())

        for feature, order_value in impute_template.items():
            column_order, impute_value = order_value
            intermediate_matrix[feature] = intermediate_matrix[feature].fillna(impute_value)

            print feature, column_order, len(columns_ordered)
            columns_ordered[column_order] = feature

        print intermediate_matrix.head()

        if 'abnormal_panel' not in intermediate_matrix.columns.values.tolist():
            intermediate_matrix['abnormal_panel'] = intermediate_matrix['all_components_normal'].apply(lambda x:1.-x) #TODO: delete in the future
        processed_matrix_full = \
            pd.concat([intermediate_matrix[features_dict['non_impute_features']], intermediate_matrix[columns_ordered]], axis=1)
        processed_matrix_full_path = os.path.join(data_folder, lab,
            "%s-normality-matrix-processed.tab"%lab)
        processed_matrix_full.to_csv(processed_matrix_full_path) # TODO: fm_io

        processed_matrix = \
            pd.concat([intermediate_matrix[features_dict['outcome_label']], intermediate_matrix[columns_ordered]], axis=1)

        # TODO: print out processed_matrix_full
        return processed_matrix
    else:
        processed_matrix_filename = '%s-normality-matrix-processed.tab'%lab
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


def train_ml_models(X_train, y_train, lab, algs):
    # TODO: How to easily include SVM, Xgboost, and Keras?
    ml_models = {}  # key: (lab,alg), value: model

    for alg in algs:
        model = train(X_train, y_train, alg)

        ml_models[(lab,alg)] = model

    return ml_models

def pick_threshold(y_pick_pred, y_pick, target_PPV=0.95):
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

