


import LabNormalityLearner as LNL
import LabNormalityLearner_Config as Config
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

remover = LNL.FeatureRemover(Config.features_to_remove)

fm_io = FeatureMatrixIO()
raw_matrix = fm_io.read_file_to_data_frame('LabNormalityLearner_TestData/LABA1C-normality-matrix-raw.tab')
print raw_matrix.shape

processed_matrix_removed = remover.transform(raw_matrix)
print processed_matrix_removed.shape


def test(test_suite=[]):
    import LabNormalityLearner_Config as Config
    from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

    fm_io = FeatureMatrixIO()
    raw_matrix = fm_io.read_file_to_data_frame('LabNormalityLearner_TestData/LABA1C-normality-matrix-raw.tab')

    if 'remove' in test_suite:
        remover = LNL.FeatureRemover(Config.features_to_remove)
        processed_matrix_removed = remover.transform(raw_matrix)
        assert raw_matrix.shape[0] < processed_matrix_removed.shape[0]
        assert raw_matrix.shape[1] == processed_matrix_removed.shape[1]

    if 'impute' in test_suite:
        features_to_impute = ['TBIL.-14_0.max','TBIL.-14_0.median','TBIL.-14_0.mean','TBIL.-14_0.std']
            #('min', 'max', 'median', 'mean', 'std', 'first', 'last', 'diff', 'slope', 'proximate')
        imputation_dict = {}
        for feature in features_to_impute:
            imputation_dict[feature] = 0

        imputer = LNL.FeatureImputer(imputation_dict=imputation_dict)
        columns_to_look = ['pat_id', 'TBIL.-14_0.max','TBIL.-14_0.median','TBIL.-14_0.mean','TBIL.-14_0.std']
        print 'raw_matrix[columns_to_look].head():', raw_matrix[columns_to_look].head()

        processed_matrix_imputed = imputer.fit_transform(raw_matrix)
        print 'processed_matrix_imputed[columns_to_look].head():', processed_matrix_imputed[columns_to_look].head()

        assert processed_matrix_imputed[columns_to_look].isna().any().any() == False
        assert (raw_matrix['order_proc_id'].values == processed_matrix_imputed['order_proc_id'].values).all()