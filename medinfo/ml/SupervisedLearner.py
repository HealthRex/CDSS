'''
Besides the regular pipelining, this new file allows starting from any
intermediate step.

Procedure for writing this module:
1. Make it usable for Lab Normality test (so assume the old naming organization)
2. More flexible for template naming


Assumption 1: Input is raw matrix
This module assumes generated raw matrix (TODO: use luigi).
Do not call function to Extract from SQL and Feature Engineering

Assumption 2: Naming rules

- project_folder (e.g. LabTestAnalysis/)
--- project_ml_folder (machine_learning/)
----- data set folder (e.g. data-Stanford-panel-10000-episodes/)
------- raw matrix (e.g. LABA1C-normality-matrix-raw.tab)
------- pat_split.csv
------- processed matrices (e.g. LABA1C-normality-matrix-processed.tab,
                                LABA1C-normality-train-matrix-processed.tab,
                                LABA1C-normality-evalu-matrix-processed.tab)
------- saved ml classifiers (LABA1C-normality-random-forest-model.pkl)
------- baseline_comparisons.csv, baseline_comparisons_train.csv
------- data alg folder (e.g. random-forest/)
--------- direct_comparisons.csv, direct_comparisons_train.csv

--- project_stats_folder


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



'''
Templates
'''
raw_matrix_template = '%s-normality-matrix-raw.tab'
pat_split_filename = 'pat_split.csv'

processed_matrix_template = '%s-normality-matrix-processed.tab'
processed_matrix_train_template = '%s-normality-train-matrix-processed.tab'
processed_matrix_evalu_template = '%s-normality-evalu-matrix-processed.tab'

direct_comparisons_train_filename = 'direct_comparisons_train.csv'
direct_comparisons_evalu_filename = 'direct_comparisons.csv'

classifier_filename_template = '%s-normality-%s-model.pkl'

############# Util functions #############
'''
General functions for smaller tasks
'''
def split_rows(data_matrix, train_size=0.75, columnToSplitOn='pat_id', random_state=0):
    from sklearn.model_selection import GroupShuffleSplit
    print data_matrix.shape
    train_inds, evalu_inds = next(
        GroupShuffleSplit(n_splits=2, test_size=1-train_size, random_state=random_state)
            .split(data_matrix, groups=data_matrix[columnToSplitOn])
    )
    print len(train_inds) + len(evalu_inds)

    data_matrix_train, data_matrix_evalu = data_matrix.iloc[train_inds], data_matrix.iloc[evalu_inds]

    pat_ids_train = data_matrix_train['pat_id'].values.tolist()
    pat_ids_evalu = data_matrix_evalu['pat_id'].values.tolist()

    # all_possible_ids = sorted(set(data_matrix[columnToSplitOn].values.tolist()))
    #
    # train_ids, test_ids = sklearn_train_test_split(all_possible_ids, train_size=fraction, random_state=random_state)
    #
    # train_matrix = data_matrix[data_matrix[columnToSplitOn].isin(train_ids)].copy()
    # # y_train = pd.DataFrame(train_matrix.pop(outcome_label))
    # # X_train = train_matrix
    #
    # test_matrix = data_matrix[data_matrix[columnToSplitOn].isin(test_ids)].copy()
    # # y_test = pd.DataFrame(test_matrix.pop(outcome_label))
    # # X_test = test_matrix
    #
    # patIds_train = train_matrix['pat_id'].values.tolist()
    # patIds_test = test_matrix['pat_id'].values.tolist()
    assert (set(pat_ids_train) & set(pat_ids_evalu)) == set([])

    print data_matrix_train.shape[0], data_matrix_evalu.shape[0], data_matrix.shape[0]
    assert data_matrix_train.shape[0] + data_matrix_evalu.shape[0] == data_matrix.shape[0]

    return data_matrix_train, pat_ids_evalu


def split_Xy(data_matrix, outcome_label):
    X = data_matrix.loc[:, data_matrix.columns != outcome_label].copy()
    y = data_matrix.loc[:, outcome_label].copy()
    return X, y

def get_algs():
    return SupervisedClassifier.SUPPORTED_ALGORITHMS
############# Util functions #############





############# Procedure functions #############

'''
If do not want to use cached, just delete the file!
'''
def get_train_and_evalu_raw_matrices(lab, data_lab_folderpath, random_state,
                                    train_size=0.75, columnToSplitOn='pat_id'):
    '''
    If train and eval exist, direct get from disk
    Avoided saving as 2 raw matrices, too much space!

    elif raw matrix exists, get from dist and split

    else, get from SQL

    Args:
        raw_matrix_filepath:
        random_state:
        use_cached:

    Returns:

    '''
    raw_matrix_filepath = os.path.join(data_lab_folderpath, raw_matrix_template % lab)
    fm_io = FeatureMatrixIO()

    # TODO: check if raw matrix exists
    raw_matrix = fm_io.read_file_to_data_frame(raw_matrix_filepath)

    pat_split_filepath = os.path.join(data_lab_folderpath, pat_split_filename)

    '''
    Old pipeline style
    '''
    if os.path.exists(pat_split_filepath):
        pat_split_df = pd.read_csv(pat_split_filepath)
        pat_ids_train = pat_split_df[pat_split_df['in_train']==1]['pat_id'].values.tolist()
        raw_matrix_train = raw_matrix[raw_matrix['pat_id'].isin(pat_ids_train)]

        pat_ids_evalu = pat_split_df[pat_split_df['in_train']==0]['pat_id'].values.tolist()
        raw_matrix_evalu = raw_matrix[raw_matrix['pat_id'].isin(pat_ids_evalu)]

    else:
        raw_matrix_train, raw_matrix_evalu = split_rows(raw_matrix,
                                                        train_size=train_size,
                                                        columnToSplitOn=columnToSplitOn,
                                                        random_state=random_state
                                                        )
        pat_ids_train = set(raw_matrix_train['pat_id'].values.tolist())

        pat_split_df = raw_matrix[['pat_id']].copy()
        pat_split_df['in_train'] = pat_split_df['pat_id'].apply(lambda x: 1 if x in pat_ids_train else 0)
        pat_split_df.to_csv(pat_split_filepath, index=False)
    return raw_matrix_train, raw_matrix_evalu


def get_train_and_evalu_processed_matrices(lab, data_lab_folderpath, features, random_state):
    '''



    Args:
        lab:
        data_lab_folderpath:
        random_state:

    Returns:

    '''

    processed_matrix_train_filepath = os.path.join(data_lab_folderpath, processed_matrix_train_template % lab)
    processed_matrix_evalu_filepath = os.path.join(data_lab_folderpath, processed_matrix_evalu_template % lab)

    if os.path.exists(processed_matrix_train_filepath) and os.path.exists(processed_matrix_evalu_filepath):
        pass

    raw_matrix_train, raw_matrix_evalu = get_train_and_evalu_raw_matrices(lab, data_lab_folderpath, random_state)

    '''
    
    '''

    processed_matrix_train, process_template  = process_matrix(lab, raw_matrix_train, features=features)
    processed_matrix_evalu = process_matrix(raw_matrix_evalu, process_template)
    return processed_matrix_train, processed_matrix_evalu



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

def process_matrix(lab, raw_matrix, features, data_path='', impute_template=None):
    '''
    From raw matrix to processed matrix

    If process_template (key: feature, val: imputed val) is provided:
        TODO

    else:
        (1) Remove specified feature (e.g. 'abnormal', 'num_components')
        (2) Select numeric features from the raw matrices
        (exclude y label and info features (to be removed before training),
        e.g. 'pat_id', 'order_time', )

    Args:
        lab:
        raw_matrix:
        features_dict:
        data_path:
        impute_template:

    Returns:

    '''

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

        processed_matrix_full = pd.concat([processed_matrix_full[features['non_impute_features']],
                                           processed_matrix_full[columns_ordered]],
                                          axis=1)

        # TODO: header info like done by fm_io?

    else:
        '''
        Process matrix from scratch
        '''

        processing_matrix = raw_matrix.copy() #

        '''
        Remove features
        '''
        processing_matrix = processing_matrix.drop(features['remove'], axis=1)

        '''
        Set aside info features and ylabel
        '''
        features_setaside = features['info'] + [features['ylabel']]
        processed_matrix = processing_matrix[features_setaside].copy()
        processing_matrix = processing_matrix.drop(features_setaside, axis=1)

        # TODO: test: only numeric features left

        '''
        Impute
        '''
        processing_matrix, impute_template = impute_features(processing_matrix, strategy="mean")

        # TODO: keep order?

        '''
        Keep features
        '''
        processed_matrix = pd.concat([processed_matrix, processing_matrix[features['keep']].copy()], axis=1) # or concat?
        processing_matrix = processing_matrix.drop(features['keep'], axis=1)


        '''
        Select features
        '''
        processing_matrix = select_features(processing_matrix)
        processed_matrix = pd.merge(processed_matrix, processing_matrix)


    return processed_matrix, impute_template




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


def standard_pipeline(lab, algs, learner_params, data_lab_folderpath, random_state):
    '''
    This pipelining procedure is consistent to the previous SupervisedLearningPipeline.py

    Args:
        lab:
        data_lab_folderpath:
        random_state:

    Returns:
        None, just write direct comparisons between y_true and y_pred_proba
    '''

    '''
    Feature selection
    Here process_template is a dictionary w/ {feature: (ind, imputed value)}

    Things to test:
    Number of columns left.
    No missing values. 
    Number of episodes for each patient does not change. 
    '''

    processed_matrix_train, processed_matrix_evalu = \
        get_train_and_evalu_processed_matrices(lab=lab,
                                               features=learner_params['features'],
                                               data_lab_folderpath=data_lab_folderpath,
                                               random_state=random_state)

    '''
    Things to test: numeric only
    '''

    '''
    Things to test:
    No missing features
    No overlapping features
    '''
    X_train, y_train = split_Xy(data_matrix=processed_matrix_train,
                                   outcome_label=outcome_label,
                                   random_state=random_state)

    X_evalu, y_evalu = split_Xy(data_matrix=processed_matrix_evalu,
                                   outcome_label=outcome_label,
                                   random_state=random_state)

    '''
    Training

    Things to test: numeric only:
    Before and after training, the model is different
    '''
    ml_classifiers = []
    for alg in algs:
        '''
        Training
        '''
        data_alg_folderpath = os.path.join(data_lab_folderpath, alg)
        direct_comparisons_evalu_filepath = os.path.join(data_alg_folderpath, direct_comparisons_train_filename)
        if os.path.exists(direct_comparisons_evalu_filepath):
            continue


        # TODO: in the future, even the CV step requires splitByPatId, so carry forward this column?
        # TODO: or load from disk
        ml_classifier_filepath = classifier_filename_template % (lab, alg)
        if os.path.exists(ml_classifier_filepath):
            ml_classifier = load_ml_model(ml_classifier)
        else:

            ml_classifier = train_ml_model(X_train=X_train,
                                              y_train=y_train,
                                              alg=alg,
                                              output_folderpath=data_alg_folderpath
                                              )  # random_state?
            save_ml_model(ml_classifier)

        '''
        Predicting train set results (overfit)
        '''
        # predict(X=X_train,
        #            y=y_train,
        #            ml_classifier=ml_classifier,
        #            output_folderpath=data_alg_folderpath)

        '''
        Predicting evalu set feature selection
        '''
        predict(X=X_eval,
                   y=y_eval,
                   ml_classifier=ml_classifier,
                   output_folderpath=data_alg_folderpath)

    # TODO here: make sure process_matrix works right
    # processed_matrix_full_eval, _ = SL.process_matrix(lab=lab,
    #                                      raw_matrix=raw_matrix_eval,
    #                                      features_dict=features_dict,
    #                                      data_folder=data_folder,
    #                                     process_template=process_template)
    # processed_matrix_eval = processed_matrix_full_eval.drop(info_features+leak_features, axis=1)
    # X_eval, y_eval = SL.split_Xy(data_matrix=processed_matrix_eval,
    #                                outcome_label=outcome_label,
    #                              random_state=random_state)


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

